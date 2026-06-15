"""
AI Chat Bot Service - Automatically manages customer conversations.
Handles all incoming messages, provides intelligent responses, and manages orders.
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import re
import structlog
import hashlib
from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langdetect import detect, detect_langs, LangDetectException

from app.db.models import (
    Message,
    Order,
    MessageDirection,
    OrderStatus,
    CustomerProfile,
    BotInstruction,
)
from app.services.enhanced_ai_service import EnhancedAIService
from app.services.service_factory import get_gemini_with_tracking

logger = structlog.get_logger(__name__)

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "ar": "Arabic",
}


LANGUAGE_NAMES = {
    "en": "English",
    "en-us": "English",
    "en-gb": "English",
    "es": "Spanish",
    "es-419": "Spanish",
    "es-es": "Spanish",
    "fr": "French",
    "fr-fr": "French",
    "fr-ca": "French",
    "ar": "Arabic",
    "ar-eg": "Arabic",
    "ar-sa": "Arabic",
}

LOCALIZED_MESSAGES = {
    "en": {
        "generic_fallback": "I’m still gathering the details I need to finish your request. Please share any extra information you have, and I’ll follow up right away.",
        "technical_issue": "I ran into a technical issue while working on your request and have logged it for follow-up. I’ll keep you updated.",
        "command_removed": "I couldn’t complete that action automatically. Please let me know the details you need help with and I’ll take care of it manually.",
    },
    "es": {
        "generic_fallback": "Aún estoy recopilando los detalles necesarios para completar tu solicitud. Por favor comparte cualquier información adicional y te responderé enseguida.",
        "technical_issue": "Encontré un problema técnico al trabajar en tu solicitud y ya lo registré para darle seguimiento. Te mantendré al tanto.",
        "command_removed": "No pude completar esa acción automáticamente. Cuéntame los detalles que necesitas y lo gestiono personalmente.",
    },
    "fr": {
        "generic_fallback": "Je rassemble encore les informations nécessaires pour finaliser votre demande. Merci de partager tout renseignement complémentaire et je vous répondrai rapidement.",
        "technical_issue": "J’ai rencontré un incident technique en traitant votre demande et je l’ai signalé pour suivi. Je vous tiendrai informé.",
        "command_removed": "Je n’ai pas pu effectuer cette action automatiquement. Donnez-moi les détails dont vous avez besoin et je m’en occupe directement.",
    },
    "ar": {
        "generic_fallback": "ما زلت أجمع التفاصيل اللازمة لإكمال طلبك. شاركني أي معلومات إضافية لديك وسأعود إليك فورًا.",
        "technical_issue": "واجهت مشكلة تقنية أثناء معالجة طلبك وقد قمت بتسجيلها للمتابعة. سأبقيك على اطلاع.",
        "command_removed": "لم أتمكن من تنفيذ هذا الإجراء تلقائيًا. أخبرني بالتفاصيل المطلوبة وسأتولى الأمر يدويًا.",
    },
}

LANGUAGE_CODE_ALIASES = {
    "en-us": "en",
    "en-gb": "en",
    "es-419": "es",
    "pt-pt": "pt",
    "pt-br": "pt-br",
    "zh-cn": "zh",
    "zh-tw": "zh",
}

LANGUAGE_DIRECTIVE_KEYWORDS = {
    "language",
    "speak",
    "talk",
    "reply",
    "respond",
    "write",
    "type",
    "use",
    "switch",
    "habla",
    "hablar",
    "responde",
    "dillo",
    "parla",
    "parlez",
    "تكلم",
    "بال",
}

LANGUAGE_REQUEST_KEYWORDS = {
    "en": {"english", "inglés", "ingles", "anglais"},
    "es": {"spanish", "español", "espanol", "castellano"},
    "fr": {"french", "français", "francais"},
    "ar": {"arabic", "arab", "عربي", "العربية", "بالعربي"},
}

SCRIPT_LANGUAGE_PATTERNS = [
    (re.compile(r"[\u0600-\u06FF]"), "ar"),
]

NON_LATIN_LANG_CODES = {"ar"}

ACCENTED_CHAR_PATTERN = re.compile(r"[\u00C0-\u017F]")


class AIChatBot:
    """
    Intelligent AI Chat Bot that automatically:
    - Responds to customer messages
    - Tracks orders and provides status updates
    - Manages order changes
    - Escalates complex issues
    - Provides personalized support
    """
    
    def __init__(self, db: AsyncSession, project_id: UUID, user_id: Optional[UUID] = None):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.gemini_client = get_gemini_with_tracking(db)
        self.enhanced_service = EnhancedAIService(db, project_id)
    
    async def process_incoming_message(
        self,
        customer_message: str,
        customer_id: str,
        channel: str,
        order_id: Optional[UUID] = None,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming message from a customer.
        
        Args:
            customer_message: The content of the message
            customer_id: Unique identifier for the customer (phone, email, etc.)
            channel: The communication channel (whatsapp, telegram, etc.)
            order_id: Optional order ID context
            customer_phone: Optional phone number
            customer_email: Optional email
            external_id: Optional unique message ID from provider (for deduplication)
            
        Returns:
            Dictionary with AI response and actions to take
        """
        # 🔒 DISTRIBUTED LOCK: Use Postgres Advisory Lock
        # ALWAYS use Content Lock to ensure cross-webhook deduplication
        # (e.g. WA-Gateway vs Official API might have different IDs but same content)
        # This matches the lock key used in webhooks.py
        clean_id = str(customer_id).split('@')[0].replace('+', '').replace(' ', '').strip()
        clean_text = customer_message.strip()
        lock_key_str = f"{clean_id}:{clean_text}"
            
        lock_key = int(hashlib.sha256(lock_key_str.encode('utf-8')).hexdigest()[:15], 16)
        
        # Try to acquire lock
        result = await self.db.execute(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": lock_key})
        lock_acquired = result.scalar()
        
        if not lock_acquired:
            logger.warning(
                "🔒 LOCK: AIChatBot skipping duplicate message", 
                customer_id=customer_id,
                lock_key=lock_key_str
            )
            return {
                "response": "",
                "intent": {},
                "actions_taken": [],
                "should_escalate": False,
                "status": "skipped"
            }

        logger.info(
            "Processing customer message",
            customer_id=customer_id,
            channel=channel,
            message_preview=customer_message[:50]
        )
        
        detected_language: Optional[str] = None
        language_source: str = "default"

        try:
            detected_language, language_source = await self._detect_language(
                customer_message,
                customer_id,
                channel
            )
            normalized_language = self._ensure_supported_language(detected_language)

            profile = await self._update_customer_profile(
                customer_id=customer_id,
                channel=channel,
                language=normalized_language,
                customer_phone=customer_phone,
                customer_email=customer_email
            )

            inbound_msg = Message(
                project_id=self.project_id,
                order_id=order_id,
                customer_id=customer_id,
                direction=MessageDirection.INBOUND,
                content=customer_message,
                channel=channel,
                provider=channel,
                sender={
                    "preferred_language": normalized_language,
                    "language_source": language_source,
                    "profile_id": str(profile.id) if profile else None,
                },
                extra_data={
                    "customer_phone": customer_phone,
                    "customer_email": customer_email
                }
            )
            self.db.add(inbound_msg)
            await self.db.commit()

            intent = await self._detect_intent(customer_message)

            context = await self._build_context(
                customer_id=customer_id,
                order_id=order_id,
                intent=intent
            )

            await self._store_conversation_event(
                customer_id=customer_id,
                customer_name=profile.name if profile else None,
                channel=channel,
                message=customer_message,
                direction=MessageDirection.INBOUND,
                intent=intent.get("primary_intent"),
                sentiment=intent.get("sentiment"),
                entities=intent.get("entities"),
                language=normalized_language,
            )

            ai_response = await self._generate_response(
                message=customer_message,
                intent=intent,
                context=context,
                channel=channel,
                language=normalized_language,
                customer_name=profile.name if profile else None
            )
            
            # Execute any required actions
            actions_taken = await self._execute_actions(ai_response.get("function_calls", []))
            
            # Prepare outbound response text
            raw_response_text = ai_response.get("text") or ""
            response_content, commands_removed = self._sanitize_response_text(
                raw_response_text,
                detected_language,
            )

            if not response_content:
                fallback_key = "command_removed" if commands_removed else "generic_fallback"
                if ai_response.get("function_calls") and fallback_key == "generic_fallback":
                    fallback_key = "technical_issue"
                response_content = self._get_localized_message(detected_language, fallback_key)

            elif commands_removed:
                notice = self._get_localized_message(detected_language, "command_removed")
                if notice:
                    response_content = f"{response_content}\n\n{notice}"

            if actions_taken:
                response_content = (
                    f"{response_content}\n\n✅ Actions completed: {', '.join(actions_taken)}"
                )
            
            # Save outbound message
            outbound_msg = Message(
                project_id=self.project_id,
                order_id=order_id,
                customer_id=customer_id,
                direction=MessageDirection.OUTBOUND,
                content=response_content,
                channel=channel,
                provider=channel,
                extra_data={
                    "ai_generated": True,
                    "model": ai_response.get("model"),
                    "tokens_used": ai_response.get("tokens_used"),
                    "cost": ai_response.get("cost"),
                    "intent": intent,
                    "actions_taken": actions_taken,
                    "language": normalized_language,
                    "language_source": language_source,
                    "persona": ai_response.get("metadata", {}).get("persona"),
                    "commands_removed": commands_removed,
                    "raw_response": raw_response_text,
                }
            )
            self.db.add(outbound_msg)
            await self.db.commit()

            await self._store_conversation_event(
                customer_id=customer_id,
                customer_name=profile.name if profile else None,
                channel=channel,
                message=response_content,
                direction=MessageDirection.OUTBOUND,
                intent=intent.get("primary_intent"),
                sentiment=intent.get("sentiment"),
                entities={"actions_taken": actions_taken} if actions_taken else None,
                language=normalized_language,
            )
            
            logger.info(
                "AI response generated",
                customer_id=customer_id,
                intent=intent,
                actions_count=len(actions_taken),
                tokens_used=ai_response.get("tokens_used")
            )
            
            return {
                "response": response_content,
                "intent": intent,
                "actions_taken": actions_taken,
                "tokens_used": ai_response.get("tokens_used"),
                "cost": ai_response.get("cost"),
                "should_escalate": intent.get("urgency") == "urgent"
            }
            
        except Exception as e:
            logger.error("Failed to process message", error=str(e), customer_id=customer_id)
            
            fallback_response = self._get_localized_message(detected_language, "technical_issue")
            
            fallback_msg = Message(
                project_id=self.project_id,
                customer_id=customer_id,
                direction=MessageDirection.OUTBOUND,
                content=fallback_response,
                channel=channel,
                provider=channel,
                extra_data={"error": str(e), "fallback": True}
            )
            self.db.add(fallback_msg)
            await self.db.commit()
            
            return {
                "response": fallback_response,
                "error": str(e),
                "should_escalate": True
            }
    
    async def _detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect customer intent from message.
        
        Returns:
            Dictionary with intent type, confidence, and extracted entities
        """
        prompt = f"""Analyze this customer message and determine the intent:

Message: "{message}"

Identify:
1. Primary intent (order_status, cancel_order, modify_order, complaint, question, other)
2. Urgency (low, medium, high, urgent)
3. Sentiment (positive, neutral, negative)
4. Extracted entities (order numbers, product names, etc.)

Respond in JSON format."""
        
        response = await self.gemini_client.generate_response(
            prompt=prompt,
            use_functions=False,
            temperature=0.2,
            user_id=self.user_id
        )
        
        try:
            import json
            intent = json.loads(response["text"])
            return intent
        except:
            return {
                "primary_intent": "question",
                "urgency": "medium",
                "sentiment": "neutral",
                "entities": {}
            }
    
    async def _build_context(
        self,
        customer_id: str,
        order_id: Optional[UUID],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build conversation context including history, orders, and customer profile."""
        context: Dict[str, Any] = {}

        # Conversation history (last 10 messages)
        result = await self.db.execute(
            select(Message)
            .where(Message.project_id == self.project_id)
            .where(Message.customer_id == customer_id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        messages = result.scalars().all()

        context["conversation_history"] = [
            {
                "role": "assistant" if msg.direction == MessageDirection.OUTBOUND else "user",
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
            }
            for msg in reversed(messages)
        ]

        # Order context when useful
        relevant_intents = {"order_status", "cancel_order", "modify_order"}
        if order_id or intent.get("primary_intent") in relevant_intents:
            if order_id:
                order_result = await self.db.execute(select(Order).where(Order.id == order_id))
            else:
                order_result = await self.db.execute(
                    select(Order)
                    .where(Order.project_id == self.project_id)
                    .where(Order.customer_email == customer_id)
                    .order_by(Order.order_date.desc())
                    .limit(1)
                )

            order = order_result.scalar_one_or_none()
            if order:
                context["order"] = {
                    "id": str(order.id),
                    "external_id": order.external_id,
                    "status": order.status.value,
                    "customer_name": order.customer_name,
                    "customer_email": order.customer_email,
                    "total": float(order.total),
                    "currency": order.currency,
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "line_items": order.line_items,
                    "tracking_number": (order.extra_data or {}).get("tracking_number"),
                }

        # Customer stats (orders)
        orders_result = await self.db.execute(
            select(Order)
            .where(Order.project_id == self.project_id)
            .where(Order.customer_email == customer_id)
        )
        customer_orders = orders_result.scalars().all()
        context["customer_info"] = {
            "total_orders": len(customer_orders),
            "is_repeat_customer": len(customer_orders) > 1,
            "customer_lifetime_value": float(sum(order.total for order in customer_orders)),
        }

        profile = await self._get_customer_profile(customer_id)
        context["customer_profile"] = {
            "preferred_language": profile.preferred_language if profile else None,
            "communication_style": profile.communication_style if profile else None,
            "name": profile.name if profile else None,
        }

        # Project-specific instructions (AI Saler persona relies on these)
        instructions_result = await self.db.execute(
            select(BotInstruction)
            .where(BotInstruction.project_id == self.project_id)
            .where(BotInstruction.is_active == True)
            .order_by(BotInstruction.priority.desc())
        )
        instructions = instructions_result.scalars().all()

        if instructions:
            context["custom_instructions"] = [
                {
                    "title": inst.title,
                    "instruction": inst.instruction,
                    "category": inst.category,
                    "priority": inst.priority,
                    "platforms": inst.active_for_platforms,
                }
                for inst in instructions
            ]

        return context

    async def _get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        if not customer_id:
            return None
        try:
            profile = await self.enhanced_service.get_customer_profile(customer_id)
            return profile
        except Exception as exc:
            logger.warning("Failed to load customer profile", error=str(exc), customer_id=customer_id)
            return None

    async def _update_customer_profile(
        self,
        customer_id: str,
        channel: Optional[str],
        language: Optional[str],
        customer_phone: Optional[str],
        customer_email: Optional[str],
    ) -> Optional[CustomerProfile]:
        if not customer_id:
            return None

        updates: Dict[str, Any] = {}

        if customer_phone:
            updates["phone"] = customer_phone
        if customer_email:
            updates["email"] = customer_email
        if channel:
            updates["preferred_platform"] = channel.lower()
        normalized_language = self._normalize_language_code(language)
        if normalized_language:
            updates["preferred_language"] = normalized_language

        try:
            profile = await self.enhanced_service.update_customer_profile(
                customer_id=customer_id,
                platform=(channel or "unknown"),
                **updates,
            )
            return profile
        except Exception as exc:
            logger.warning("Failed to update customer profile", error=str(exc), customer_id=customer_id)
            return await self._get_customer_profile(customer_id)

    def _normalize_language_code(self, code: Optional[str]) -> Optional[str]:
        if not code:
            return None

        normalized = code.strip().lower()
        normalized = LANGUAGE_CODE_ALIASES.get(normalized, normalized)

        if normalized in LANGUAGE_NAMES:
            return normalized

        base = normalized.split("-", 1)[0]
        if base in LANGUAGE_NAMES:
            return base

        return normalized or None

    def _get_language_display_name(self, code: Optional[str]) -> str:
        normalized = self._ensure_supported_language(code)
        return SUPPORTED_LANGUAGES.get(normalized, SUPPORTED_LANGUAGES["en"])

    def _ensure_supported_language(self, code: Optional[str]) -> str:
        normalized = self._normalize_language_code(code or "") if code else None
        if normalized and normalized in SUPPORTED_LANGUAGES:
            return normalized
        return "en"

    def _extract_language_request(self, message: str) -> Optional[str]:
        if not message:
            return None

        lowered = message.lower()
        directive_detected = any(keyword in lowered for keyword in LANGUAGE_DIRECTIVE_KEYWORDS)

        for lang_code, keywords in LANGUAGE_REQUEST_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lowered:
                    if directive_detected:
                        return lang_code

                    pattern = rf"(?:^|\b)(?:in|en|de|per|para|pour|nel|na|على|بال|باللغة)?\s*{re.escape(keyword)}\b"
                    if re.search(pattern, lowered):
                        return lang_code

                    stripped = lowered.strip()
                    if stripped.startswith(keyword) or stripped.endswith(keyword):
                        return lang_code

                    if re.search(rf"{re.escape(keyword)}\s+please", lowered) or re.search(rf"please\s+{re.escape(keyword)}", lowered):
                        return lang_code

        return None

    def _guess_language_from_script(self, message: str) -> Optional[str]:
        for pattern, lang_code in SCRIPT_LANGUAGE_PATTERNS:
            if pattern.search(message):
                return lang_code
        return None

    def _infer_language_from_text(self, message: str) -> Optional[str]:
        if not message:
            return None

        try:
            language_candidates = detect_langs(message)
            if language_candidates:
                top_candidate = language_candidates[0]
                if top_candidate.prob >= 0.6:
                    return self._normalize_language_code(top_candidate.lang)
        except LangDetectException:
            pass
        except Exception:
            logger.debug("detect_langs failed", text_preview=message[:30])

        try:
            detected = detect(message)
            if detected:
                return self._normalize_language_code(detected)
        except LangDetectException:
            return None

        return None

    async def _detect_language(
        self,
        message: str,
        customer_id: str,
        channel: Optional[str],
    ) -> Tuple[Optional[str], str]:
        normalized_message = (message or "").strip()

        profile = await self._get_customer_profile(customer_id)
        stored_language: Optional[str] = None
        if profile and profile.preferred_language and profile.interaction_count:
            stored_language = self._normalize_language_code(profile.preferred_language)

        explicit_request = self._extract_language_request(normalized_message)
        if explicit_request:
            lang = self._ensure_supported_language(explicit_request)
            source = "customer_request" if lang == self._normalize_language_code(explicit_request) else "fallback"
            return lang, source

        if stored_language:
            lang = self._ensure_supported_language(stored_language)
            source = "profile" if lang == stored_language else "fallback"
            return lang, source

        candidate_lang: Optional[str] = None
        source = "default"

        if normalized_message:
            inferred_language = self._infer_language_from_text(normalized_message)
            if inferred_language:
                candidate_lang = inferred_language
                source = "message"
            else:
                script_language = self._guess_language_from_script(normalized_message)
                if script_language:
                    candidate_lang = script_language
                    source = "script"

        if not candidate_lang and channel:
            channel_defaults = {
                "whatsapp": "es",
                "telegram": "en",
                "instagram": "en",
                "facebook": "en",
                "tiktok": "en",
                "web": "en",
            }
            channel_lang = channel_defaults.get(channel.lower())
            if channel_lang:
                candidate_lang = channel_lang
                source = "channel_default"

        final_lang = self._ensure_supported_language(candidate_lang)
        final_source = source if candidate_lang and final_lang == self._normalize_language_code(candidate_lang) else "fallback"

        return final_lang, final_source

    async def _store_conversation_event(
        self,
        *,
        customer_id: str,
        customer_name: Optional[str],
        channel: str,
        message: str,
        direction: MessageDirection,
        intent: Optional[str],
        sentiment: Optional[str],
        entities: Optional[Dict[str, Any]],
        language: Optional[str],
    ) -> None:
        try:
            merged_entities = dict(entities or {})
            if language:
                merged_entities.setdefault("_language", language)

            await self.enhanced_service.save_conversation(
                customer_id=customer_id,
                customer_name=customer_name,
                platform=channel,
                message_content=message,
                direction=direction,
                intent=intent,
                sentiment=sentiment,
                entities=merged_entities,
            )
        except Exception as exc:
            logger.warning(
                "Failed to persist conversation event",
                error=str(exc),
                customer_id=customer_id,
                channel=channel,
            )

    async def _generate_response(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        channel: str,
        language: Optional[str],
        customer_name: Optional[str]
    ) -> Dict[str, Any]:
        """Generate AI response based on message, intent, and context."""
        
        enhanced_context = {
            **context,
            "intent": intent,
            "current_message": message,
            "language": self._normalize_language_code(language) or "en",
            "channel": channel,
            "customer_name": customer_name,
            "language_name": self._get_language_display_name(language),
        }

        enhanced_context["persona"] = "ai_saler"
        enhanced_context["persona_detail"] = self._get_persona_prompt(channel, enhanced_context["language"])

        response = await self.gemini_client.generate_response(
            prompt=message,
            context=enhanced_context,
            use_functions=True,
            temperature=0.7,
            user_id=self.user_id,
        )

        metadata = response.setdefault("metadata", {})
        metadata["persona"] = "ai_saler"
        if language:
            metadata.setdefault("language", language)

        return response

    def _sanitize_response_text(
        self,
        text: str,
        language: Optional[str],
    ) -> Tuple[str, bool]:
        """Remove backend commands or code blocks from the AI text."""
        if not text:
            return "", False

        sanitized = text
        commands_removed = False

        code_block_pattern = re.compile(r"```[\s\S]*?```", re.IGNORECASE)
        if code_block_pattern.search(sanitized):
            sanitized = code_block_pattern.sub("", sanitized)
            commands_removed = True

        sanitized_lines: List[str] = []
        command_line_pattern = re.compile(
            r"^\s*(?:/[\w-]+|command\s*:|cmd\s*:|cmd\s+>|shell\s*:)",
            re.IGNORECASE,
        )

        for line in sanitized.splitlines():
            stripped = line.strip()
            if not stripped:
                sanitized_lines.append("")
                continue

            if command_line_pattern.match(stripped) or stripped.startswith("#!"):
                commands_removed = True
                continue

            sanitized_lines.append(line.strip())

        sanitized = "\n".join(sanitized_lines)
        sanitized = re.sub(r"\n{3,}", "\n\n", sanitized).strip()

        return sanitized, commands_removed

    def _get_localized_message(self, language: Optional[str], key: str) -> str:
        lang_code = self._normalize_language_code(language) or "en"
        messages = LOCALIZED_MESSAGES.get(lang_code) or LOCALIZED_MESSAGES.get(
            lang_code.split("-", 1)[0]
        )
        if not messages:
            messages = LOCALIZED_MESSAGES["en"]

        return messages.get(key) or LOCALIZED_MESSAGES["en"].get(key, "")

    def _get_persona_prompt(self, channel: str, language: Optional[str]) -> str:
        language_name = self._get_language_display_name(language)

        base_prompt = (
            "You are a professional human sales consultant representing the merchant's brand. "
            "Respond only in {language_name}, mirroring the customer's tone while staying polite and concise. "
            "Never expose system commands, backend steps, or code snippets. Focus on helpful product and order guidance."
        ).format(language_name=language_name)

        channel = (channel or "").lower()
        channel_prompts = {
            "web": (
                "You are the official AI assistant in the store's web chat. Be transparent that you are an AI helper, stay professional, and offer proactive assistance."
            ),
            "telegram": "You are chatting in Telegram as the store's dedicated sales agent. Keep it conversational and reassuring, like a real teammate.",
            "whatsapp": "You are messaging on WhatsApp as the customer's personal sales representative. Use a warm, personable tone and relevant product suggestions.",
            "instagram": "You are answering Instagram DMs as the brand's social sales specialist. Keep replies stylish, friendly, and product-aware.",
            "facebook": "You are replying on Facebook Messenger as the business page manager. Sound trustworthy, provide specifics, and invite follow-up questions.",
            "tiktok": "You are responding to TikTok messages as the creator's e-commerce agent. Stay energetic, on-brand, and product oriented.",
            "discord": "You are helping in Discord as the community store rep. Keep it friendly, concise, and helpful."
        }

        persona_detail = channel_prompts.get(channel)
        if not persona_detail:
            persona_detail = "You are assisting on a customer messaging channel. Maintain a friendly, sales-focused voice."

        closing_rules = (
            "Always answer directly, in natural sentences, without listing raw commands or placeholder text. "
            "If information is missing, state that politely and explain what you'll do next."
        )

        return f"{base_prompt}\n{persona_detail}\n{closing_rules}"

    async def _execute_actions(self, function_calls: List[Dict[str, Any]]) -> List[str]:
        """Run follow-up actions requested by the AI model."""
        actions_taken: List[str] = []

        for func_call in function_calls:
            function_name = func_call.get("name")
            parameters = func_call.get("parameters", {})

            try:
                if function_name == "update_order_status":
                    await self._update_order_status(
                        order_id=parameters.get("order_id"),
                        status=parameters.get("status"),
                        note=parameters.get("note"),
                    )
                    actions_taken.append(
                        f"Updated order status to {parameters.get('status')}"
                    )

                elif function_name == "send_tracking_info":
                    await self._send_tracking_info(
                        order_id=parameters.get("order_id"),
                        tracking_number=parameters.get("tracking_number"),
                    )
                    actions_taken.append("Sent tracking information")

                elif function_name == "schedule_followup":
                    await self._schedule_followup(
                        customer_id=parameters.get("customer_id"),
                        delay_hours=parameters.get("delay_hours"),
                        message=parameters.get("message"),
                    )
                    actions_taken.append("Scheduled follow-up message")

                elif function_name == "create_support_ticket":
                    await self._create_support_ticket(
                        customer_id=parameters.get("customer_id"),
                        subject=parameters.get("subject"),
                        description=parameters.get("description"),
                        priority=parameters.get("priority", "medium"),
                    )
                    actions_taken.append("Created support ticket for human review")

                logger.info("Executed action", name=function_name, parameters=parameters)

            except Exception as exc:
                logger.error(
                    "Failed to execute function call",
                    name=function_name,
                    error=str(exc),
                )

        return actions_taken
    
    async def _update_order_status(
        self,
        order_id: str,
        status: str,
        note: Optional[str] = None
    ):
        """Update order status in database."""
        result = await self.db.execute(
            select(Order).where(Order.id == UUID(order_id))
        )
        order = result.scalar_one_or_none()
        
        if order:
            order.status = OrderStatus(status)
            if note:
                order.extra_data = order.extra_data or {}
                order.extra_data["status_notes"] = order.extra_data.get("status_notes", [])
                order.extra_data["status_notes"].append({
                    "note": note,
                    "timestamp": datetime.utcnow().isoformat(),
                    "updated_by": "AI Bot"
                })
            await self.db.commit()
    
    async def _send_tracking_info(
        self,
        order_id: str,
        tracking_number: str
    ):
        """Add tracking information to order."""
        result = await self.db.execute(
            select(Order).where(Order.id == UUID(order_id))
        )
        order = result.scalar_one_or_none()
        
        if order:
            order.extra_data = order.extra_data or {}
            order.extra_data["tracking_number"] = tracking_number
            order.extra_data["tracking_updated_at"] = datetime.utcnow().isoformat()
            await self.db.commit()
    
    async def _schedule_followup(
        self,
        customer_id: str,
        delay_hours: int,
        message: str
    ):
        """Schedule a follow-up message (would integrate with Celery)."""
        # TODO: Integrate with Celery to schedule task
        logger.info(
            "Follow-up scheduled",
            customer_id=customer_id,
            delay_hours=delay_hours
        )
    
    async def _create_support_ticket(
        self,
        customer_id: str,
        subject: str,
        description: str,
        priority: str = "medium"
    ):
        """Create a support ticket for human review."""
        # TODO: Integrate with ticketing system
        logger.info(
            "Support ticket created",
            customer_id=customer_id,
            subject=subject,
            priority=priority
        )
    
    async def handle_order_inquiry(
        self,
        customer_id: str,
        order_number: str,
        channel: str
    ) -> Dict[str, Any]:
        """
        Specifically handle order inquiry - get status and provide update.
        """
        # Find order
        result = await self.db.execute(
            select(Order)
            .where(Order.project_id == self.project_id)
            .where(Order.external_id == order_number)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            return await self.process_incoming_message(
                customer_message=f"What's the status of order {order_number}?",
                customer_id=customer_id,
                channel=channel
            )
        
        # Build order status message
        status_message = f"""📦 Order Status Update

Order #{order.external_id}
Status: {order.status.value.upper()} ✓
Order Date: {order.order_date.strftime('%B %d, %Y')}
Total: {order.currency} {order.total}

"""
        
        if order.status == OrderStatus.SHIPPED:
            tracking = order.extra_data.get("tracking_number") if order.extra_data else None
            if tracking:
                status_message += f"🚚 Tracking Number: {tracking}\n"
            status_message += "Your order is on its way! 🎉"
        elif order.status == OrderStatus.PROCESSING:
            status_message += "We're preparing your order for shipment. You'll receive tracking info soon!"
        elif order.status == OrderStatus.FULFILLED:
            status_message += "Your order has been delivered! We hope you enjoy it! 😊"
        else:
            status_message += "We're processing your order and will update you soon!"
        
        # Save as outbound message
        outbound_msg = Message(
            project_id=self.project_id,
            order_id=order.id,
            customer_id=customer_id,
            direction=MessageDirection.OUTBOUND,
            content=status_message,
            channel=channel,
            provider=channel,
            extra_data={"ai_generated": True, "type": "order_status_update"}
        )
        self.db.add(outbound_msg)
        await self.db.commit()
        
        return {
            "response": status_message,
            "order_id": str(order.id),
            "status": order.status.value
        }


# Factory function
def get_chat_bot(db: AsyncSession, project_id: UUID, user_id: Optional[UUID] = None) -> AIChatBot:
    """Get AI Chat Bot instance with usage tracking."""
    return AIChatBot(db, project_id, user_id)
