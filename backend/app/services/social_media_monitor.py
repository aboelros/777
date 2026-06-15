"""
Social Media Post and Comment Monitoring Service.
Handles post analysis, comment detection, and automated responses.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import structlog
import re
import json

from app.services.gemini_client import GeminiClient
from app.services.enhanced_ai_service import EnhancedAIService
from app.db.models import (
    SocialMediaPost, SocialMediaComment, BusinessContext,
    AutoResponseTemplate
)

logger = structlog.get_logger(__name__)


class SocialMediaMonitor:
    """
    Monitor social media posts and comments for automated engagement.
    """
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
        self.gemini_client = GeminiClient()
        self.ai_service = EnhancedAIService(db, project_id)
    
    async def analyze_post(
        self,
        post_id: UUID,
        fetch_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a social media post using AI.
        Extracts topics, sentiment, keywords, and generates insights.
        """
        # Get post
        result = await self.db.execute(
            select(SocialMediaPost).where(SocialMediaPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        # Analyze post content
        analysis = await self._analyze_post_content(
            content=post.content or "",
            platform=post.platform,
            media_type=post.media_type
        )
        
        # Update post with analysis
        post.ai_analyzed = True
        post.sentiment = analysis.get("overall_sentiment")
        post.topics = analysis.get("topics", [])
        post.keywords = analysis.get("keywords", [])
        post.ai_summary = analysis.get("summary")
        
        # Calculate engagement rate if we have metrics
        if post.likes_count or post.comments_count or post.shares_count:
            total_engagement = (
                post.likes_count + 
                (post.comments_count * 2) +  # Comments count more
                (post.shares_count * 3)  # Shares count even more
            )
            # Assuming follower count is in extra_data or use default
            followers = post.extra_data.get("follower_count", 1000)
            post.engagement_rate = (total_engagement / followers) * 100
        
        await self.db.commit()
        await self.db.refresh(post)
        
        # Analyze comments if requested
        comment_analysis = None
        if fetch_comments:
            comment_analysis = await self.analyze_post_comments(post_id)
        
        logger.info("Post analyzed", post_id=str(post_id), sentiment=post.sentiment)
        
        return {
            "post": {
                "id": str(post.id),
                "platform": post.platform,
                "sentiment": post.sentiment,
                "topics": post.topics,
                "keywords": post.keywords,
                "summary": post.ai_summary,
                "engagement_rate": post.engagement_rate
            },
            "analysis": analysis,
            "comment_analysis": comment_analysis
        }
    
    async def analyze_post_comments(self, post_id: UUID) -> Dict[str, Any]:
        """
        Analyze all comments on a post.
        Identifies questions, complaints, and engagement opportunities.
        """
        # Get post
        result = await self.db.execute(
            select(SocialMediaPost).where(SocialMediaPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        # Get comments for this post
        result = await self.db.execute(
            select(SocialMediaComment)
            .where(
                and_(
                    SocialMediaComment.project_id == self.project_id,
                    SocialMediaComment.post_id == post.external_id
                )
            )
            .order_by(desc(SocialMediaComment.created_at))
        )
        comments = result.scalars().all()
        
        if not comments:
            return {"total_comments": 0, "analysis": None}
        
        # Analyze comments
        comment_texts = [c.content for c in comments[:50]]  # Analyze up to 50 recent
        
        analysis = await self._analyze_comments_batch(
            comments=comment_texts,
            platform=post.platform
        )
        
        # Identify priority comments that need responses
        priority_comments = []
        for comment in comments:
            if not comment.responded:
                priority = await self._assess_comment_priority(comment)
                if priority > 0:
                    comment.priority = priority
                    priority_comments.append(comment)
        
        await self.db.commit()
        
        # Update post
        post.unresponded_comments = len([c for c in comments if not c.responded])
        post.last_comment_check = datetime.utcnow()
        await self.db.commit()
        
        return {
            "total_comments": len(comments),
            "unresponded_comments": post.unresponded_comments,
            "priority_comments": len(priority_comments),
            "overall_sentiment": analysis.get("overall_sentiment"),
            "common_topics": analysis.get("common_topics", []),
            "questions_count": analysis.get("questions_count", 0),
            "complaints_count": analysis.get("complaints_count", 0),
            "praise_count": analysis.get("praise_count", 0)
        }
    
    async def generate_comment_reply(
        self,
        comment_id: UUID,
        use_templates: bool = True,
        auto_send: bool = False
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered reply to a comment.
        Can use templates or generate custom response.
        """
        # Get comment
        result = await self.db.execute(
            select(SocialMediaComment).where(SocialMediaComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        
        # Check if we should use template
        template_response = None
        if use_templates:
            template_response = await self._find_matching_template(
                comment_content=comment.content,
                platform=comment.platform,
                intent=comment.intent
            )
        
        # Generate response
        if template_response:
            response = await self._personalize_template(
                template=template_response,
                comment=comment
            )
            method = "template"
        else:
            response = await self._generate_custom_reply(comment)
            method = "ai_generated"
        
        # Update comment
        comment.response_content = response
        comment.auto_generated = True
        
        if auto_send:
            comment.responded = True
            comment.response_sent_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(comment)
        
        logger.info(
            "Comment reply generated",
            comment_id=str(comment_id),
            method=method,
            auto_send=auto_send
        )
        
        return {
            "comment_id": str(comment_id),
            "response": response,
            "method": method,
            "auto_sent": auto_send,
            "requires_approval": not auto_send
        }
    
    async def auto_respond_to_comments(
        self,
        post_id: Optional[UUID] = None,
        max_responses: int = 10
    ) -> Dict[str, Any]:
        """
        Automatically respond to pending comments.
        Prioritizes urgent and high-value comments.
        """
        # Build query for unresponded comments
        query = select(SocialMediaComment).where(
            and_(
                SocialMediaComment.project_id == self.project_id,
                SocialMediaComment.responded == False,
                SocialMediaComment.requires_human == False  # Don't auto-respond to complex ones
            )
        )
        
        if post_id:
            result = await self.db.execute(
                select(SocialMediaPost).where(SocialMediaPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            if post:
                query = query.where(SocialMediaComment.post_id == post.external_id)
        
        query = query.order_by(
            desc(SocialMediaComment.priority),
            desc(SocialMediaComment.created_at)
        ).limit(max_responses)
        
        result = await self.db.execute(query)
        comments = result.scalars().all()
        
        responses_sent = 0
        responses_generated = []
        
        for comment in comments:
            try:
                # Generate and send response
                reply_result = await self.generate_comment_reply(
                    comment_id=comment.id,
                    use_templates=True,
                    auto_send=True
                )
                responses_sent += 1
                responses_generated.append(reply_result)
                
            except Exception as e:
                logger.error(
                    "Failed to respond to comment",
                    comment_id=str(comment.id),
                    error=str(e)
                )
        
        return {
            "responses_sent": responses_sent,
            "total_pending": len(comments),
            "responses": responses_generated
        }
    
    async def learn_from_post_performance(self, post_id: UUID) -> Dict[str, Any]:
        """
        Analyze post performance and learn what works.
        Updates business context with insights.
        """
        result = await self.db.execute(
            select(SocialMediaPost).where(SocialMediaPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        # Determine if this is a high-performing post
        if post.engagement_rate and post.engagement_rate > 5.0:  # 5% is good
            post.best_performing = True
            
            # Extract learnings
            learnings = await self._extract_post_learnings(post)
            
            # Save as business context
            for learning in learnings:
                context = BusinessContext(
                    project_id=self.project_id,
                    context_type="content_strategy",
                    context_key=f"high_performing_{post.platform}",
                    title=f"Successful {post.platform.title()} Post Pattern",
                    content=learning["insight"],
                    tags=[post.platform, "high_engagement", "content_strategy"],
                    relevance_score=learning.get("score", 0.8),
                    learned_from="ai_analysis",
                    confidence_score=0.7,
                    active_for_platforms=[post.platform],
                    examples=[{
                        "post_id": post.external_id,
                        "engagement_rate": post.engagement_rate,
                        "content_snippet": post.content[:100] if post.content else ""
                    }]
                )
                self.db.add(context)
            
            await self.db.commit()
            logger.info("Learned from high-performing post", post_id=str(post_id))
            
            return {
                "learnings_extracted": len(learnings),
                "insights": learnings
            }
        
        return {"learnings_extracted": 0, "reason": "Post performance not significant"}
    
    async def _analyze_post_content(
        self,
        content: str,
        platform: str,
        media_type: Optional[str]
    ) -> Dict[str, Any]:
        """
        Analyze post content using AI.
        """
        prompt = f"""Analyze this {platform.upper()} post:

Content: "{content}"
Media Type: {media_type or 'text'}

Extract:
1. Overall sentiment (positive, negative, neutral, promotional, informative)
2. Main topics (max 5)
3. Keywords (max 10)
4. Target audience
5. Call-to-action present? 
6. Brief summary (max 50 words)

Return as JSON:
{{
    "overall_sentiment": "",
    "topics": [],
    "keywords": [],
    "target_audience": "",
    "has_cta": true/false,
    "cta_type": "",
    "summary": ""
}}"""

        try:
            response = await self.gemini_client.generate_content(prompt=prompt, temperature=0.3)
            return json.loads(self._extract_json(response))
        except Exception as e:
            logger.error("Failed to analyze post", error=str(e))
            return {}
    
    async def _analyze_comments_batch(
        self,
        comments: List[str],
        platform: str
    ) -> Dict[str, Any]:
        """
        Analyze multiple comments together for insights.
        """
        comments_text = "\n".join([f"- {c}" for c in comments[:30]])
        
        prompt = f"""Analyze these comments from a {platform.upper()} post:

{comments_text}

Provide:
1. Overall sentiment
2. Common topics/themes
3. Number of questions
4. Number of complaints
5. Number of praise/positive comments
6. Key concerns or interests

Return as JSON:
{{
    "overall_sentiment": "",
    "common_topics": [],
    "questions_count": 0,
    "complaints_count": 0,
    "praise_count": 0,
    "key_concerns": [],
    "engagement_quality": "high/medium/low"
}}"""

        try:
            response = await self.gemini_client.generate_content(prompt=prompt, temperature=0.3)
            return json.loads(self._extract_json(response))
        except:
            return {}
    
    async def _assess_comment_priority(self, comment: SocialMediaComment) -> int:
        """
        Assess priority level of a comment (0=low, 1=medium, 2=high, 3=urgent).
        """
        priority = 0
        content_lower = comment.content.lower()
        
        # Urgent keywords
        urgent_keywords = [
            "urgent", "asap", "immediately", "help", "problem", "issue",
            "broken", "error", "not working", "disappointed", "angry", 
            "refund", "cancel", "terrible", "worst"
        ]
        
        # Question indicators
        question_indicators = ["?", "how", "when", "where", "what", "why", "can i", "is it"]
        
        # Check for urgent keywords
        if any(keyword in content_lower for keyword in urgent_keywords):
            priority = 3
        # Check for questions
        elif any(indicator in content_lower for indicator in question_indicators):
            priority = 2
        # Check sentiment
        elif comment.sentiment in ["negative", "frustrated"]:
            priority = 2
        else:
            priority = 1
        
        return priority
    
    async def _find_matching_template(
        self,
        comment_content: str,
        platform: str,
        intent: Optional[str]
    ) -> Optional[AutoResponseTemplate]:
        """
        Find matching auto-response template.
        """
        query = select(AutoResponseTemplate).where(
            and_(
                AutoResponseTemplate.project_id == self.project_id,
                AutoResponseTemplate.is_active == True,
                or_(
                    AutoResponseTemplate.trigger_platforms == [],
                    AutoResponseTemplate.trigger_platforms.contains([platform])
                )
            )
        )
        
        if intent:
            query = query.where(AutoResponseTemplate.trigger_intent == intent)
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        # Find best matching template based on keywords
        comment_lower = comment_content.lower()
        best_match = None
        max_matches = 0
        
        for template in templates:
            matches = sum(
                1 for keyword in template.trigger_keywords 
                if keyword.lower() in comment_lower
            )
            if matches > max_matches:
                max_matches = matches
                best_match = template
                template.times_used += 1
        
        if best_match:
            await self.db.commit()
        
        return best_match
    
    async def _personalize_template(
        self,
        template: AutoResponseTemplate,
        comment: SocialMediaComment
    ) -> str:
        """
        Personalize template with customer name and context.
        """
        response = template.response_template
        
        # Basic replacements
        response = response.replace("{{username}}", comment.author_username or "there")
        response = response.replace("{{platform}}", comment.platform.title())
        
        # Use AI to enhance if enabled
        if template.use_ai_enhancement:
            prompt = f"""Personalize this template response to feel more natural:

Template: "{response}"
Customer Comment: "{comment.content}"
Platform: {comment.platform}

Make it sound personal and friendly while keeping the main message. Return only the personalized response."""

            try:
                response = await self.gemini_client.generate_content(
                    prompt=prompt,
                    temperature=0.7
                )
            except:
                pass  # Use template as-is if AI fails
        
        return response
    
    async def _generate_custom_reply(self, comment: SocialMediaComment) -> str:
        """
        Generate a custom AI reply for comment.
        """
        # Get business context
        contexts = await self.ai_service.get_business_context(platform=comment.platform)
        
        context_info = "\n".join([f"- {c.title}: {c.content}" for c in contexts[:5]])
        
        prompt = f"""Generate a helpful, friendly reply to this {comment.platform.upper()} comment:

Comment: "{comment.content}"
Author: {comment.author_username}
Sentiment: {comment.sentiment or 'neutral'}

Business Context:
{context_info}

Generate a reply that:
1. Addresses the comment appropriately
2. Maintains brand voice
3. Is platform-appropriate (length, tone)
4. Includes emoji if suitable for {comment.platform}
5. Encourages engagement

Return only the reply text, no explanations."""

        response = await self.gemini_client.generate_content(
            prompt=prompt,
            temperature=0.8
        )
        
        return response
    
    async def _extract_post_learnings(self, post: SocialMediaPost) -> List[Dict]:
        """
        Extract learnings from successful post.
        """
        prompt = f"""Analyze this high-performing {post.platform.upper()} post:

Content: "{post.content}"
Engagement Rate: {post.engagement_rate}%
Likes: {post.likes_count}
Comments: {post.comments_count}
Shares: {post.shares_count}
Topics: {post.topics}
Sentiment: {post.sentiment}

What made this post successful? Provide 3-5 actionable insights.

Return as JSON array:
[
    {{"insight": "...", "score": 0.0-1.0}},
    ...
]"""

        try:
            response = await self.gemini_client.generate_content(prompt=prompt, temperature=0.4)
            return json.loads(self._extract_json(response))
        except:
            return []
    
    def _extract_json(self, response: str) -> str:
        """Extract JSON from response."""
        json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return response
