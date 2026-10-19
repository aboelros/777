"""
OpenRouter AI client for multi-model access via unified OpenAI-compatible API.
"""

from typing import Dict, Any, Optional, List
import json
import structlog
import aiohttp

from app.core.config import settings

logger = structlog.get_logger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API supporting any model via unified completions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL or "google/gemini-2.0-flash-001"
        self.base_url = (base_url or settings.OPENROUTER_BASE_URL or "https://openrouter.ai/api/v1").rstrip("/")

    @property
    def is_configured(self) -> bool:
        """Check if OpenRouter API key is set."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_functions: bool = False,
        user_id: Optional[Any] = None,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response via OpenRouter chat completion API."""
        if not self.is_configured:
            logger.error("OpenRouter API key not configured")
            return {"text": "", "error": "OpenRouter API key not configured"}

        messages: List[Dict[str, Any]] = []

        system_instruction = ""
        if context:
            if isinstance(context, dict):
                system_instruction = context.get("persona_detail") or context.get("system_prompt") or ""
            elif isinstance(context, str):
                system_instruction = context

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        user_content: Any = prompt
        if media_url and "image" in str(media_type or ""):
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": media_url}}
            ]

        messages.append({"role": "user", "content": user_content})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://ai-sales-bot.onrender.com",
            "X-Title": "AI Sales Commander",
            "Content-Type": "application/json"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.GEMINI_TEMPERATURE or 0.7,
            "max_tokens": 1024
        }
        candidate_models = list(dict.fromkeys([self.model, "minimax/minimax-m3.1-flash:free"]))
        url = f"{self.base_url}/chat/completions"
        last_error = ""

        try:
            timeout = aiohttp.ClientTimeout(total=45)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for cand_model in candidate_models:
                    payload["model"] = cand_model
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            choices = data.get("choices", [])
                            if choices:
                                message_obj = choices[0].get("message", {})
                                content = message_obj.get("content", "")
                                return {
                                    "text": content.strip() if content else "",
                                    "function_calls": [],
                                    "model": cand_model,
                                    "provider": "openrouter"
                                }
                            return {"text": "", "error": "No completion choice returned"}

                        last_error = await response.text()
                        logger.warning("OpenRouter model attempt failed", model=cand_model, status=response.status, error=last_error)

                logger.error("All OpenRouter models failed", error=last_error)
                return {"text": "", "error": f"OpenRouter error: {last_error}"}
        except Exception as e:
            logger.error("OpenRouter request failed", error=str(e))
            return {"text": "", "error": str(e)}

    async def generate_content(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate plain text content via OpenRouter."""
        res = await self.generate_response(prompt=prompt, context=context, use_functions=False)
        return res.get("text", "")

    async def generate_sales_reply(
        self,
        customer_message: str,
        order_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate sales reply via OpenRouter."""
        context = {
            "conversation_history": conversation_history or [],
            "order": order_context
        }
        return await self.generate_response(prompt=customer_message, context=context, use_functions=False)

    async def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze message sentiment via OpenRouter."""
        prompt = (
            f"Analyze the sentiment of this customer message:\n\"{message}\"\n\n"
            "Return JSON only with keys: sentiment (positive, neutral, negative), "
            "urgency (low, medium, high, urgent), score (-1.0 to 1.0)."
        )
        res = await self.generate_response(prompt=prompt, use_functions=False)
        text = res.get("text", "")
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(cleaned)
        except Exception:
            return {"sentiment": "neutral", "urgency": "medium", "score": 0.0, "raw": text}

