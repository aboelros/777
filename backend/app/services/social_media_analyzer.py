from typing import List, Dict, Any, Optional
import structlog
import re
import json

from app.domains.social.models import SocialMediaPost, SocialMediaComment
from app.domains.ai.providers.gemini import GeminiClient

logger = structlog.get_logger(__name__)


def extract_json_payload(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from response text."""
    try:
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(text)
    except Exception:
        return None


async def analyze_post_content(
    gemini_client: GeminiClient,
    content: str,
    platform: str,
    media_type: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze post content using AI."""
    prompt = f"""Analyze this {platform.upper()} post:

Content: "{content}"
Media Type: {media_type or 'text'}

Extract:
1. Overall sentiment (positive, negative, neutral, promotional, informative)
2. Main topics (max 5)
3. Keywords (max 10)
4. A brief 1-sentence summary

Respond in JSON format:
{{
    "overall_sentiment": "sentiment",
    "topics": ["topic1", "topic2"],
    "keywords": ["keyword1", "keyword2"],
    "summary": "Brief summary"
}}"""
    try:
        response = await gemini_client.generate_response(prompt=prompt, use_functions=False, temperature=0.3)
        data = extract_json_payload(response.get("text", ""))
        return data or {
            "overall_sentiment": "neutral",
            "topics": [],
            "keywords": [],
            "summary": content[:100] if content else ""
        }
    except Exception as e:
        logger.error("Failed to analyze post content", error=str(e))
        return {
            "overall_sentiment": "neutral",
            "topics": [],
            "keywords": [],
            "summary": content[:100] if content else ""
        }


async def analyze_comments_batch(
    gemini_client: GeminiClient,
    comments: List[str],
    platform: str
) -> Dict[str, Any]:
    """Analyze a batch of comments."""
    if not comments:
        return {
            "overall_sentiment": "neutral",
            "common_topics": [],
            "questions_count": 0,
            "complaints_count": 0,
            "praise_count": 0
        }

    formatted_comments = "\n".join([f"- {c}" for c in comments[:30]])
    prompt = f"""Analyze these {platform.upper()} comments:

{formatted_comments}

Provide:
1. Overall sentiment
2. Common topics/themes
3. Number of questions
4. Number of complaints
5. Number of praise/compliments

Respond in JSON format:
{{
    "overall_sentiment": "sentiment",
    "common_topics": ["topic1", "topic2"],
    "questions_count": 0,
    "complaints_count": 0,
    "praise_count": 0
}}"""
    try:
        response = await gemini_client.generate_response(prompt=prompt, use_functions=False, temperature=0.3)
        data = extract_json_payload(response.get("text", ""))
        return data or {
            "overall_sentiment": "neutral",
            "common_topics": [],
            "questions_count": 0,
            "complaints_count": 0,
            "praise_count": 0
        }
    except Exception as e:
        logger.error("Failed to analyze comments batch", error=str(e))
        return {
            "overall_sentiment": "neutral",
            "common_topics": [],
            "questions_count": 0,
            "complaints_count": 0,
            "praise_count": 0
        }


def assess_comment_priority(comment: SocialMediaComment) -> int:
    """Assess comment priority (0=normal, 1=high, 2=urgent)."""
    priority = 0
    content_lower = comment.content.lower()
    urgent_keywords = ["refund", "scam", "broken", "terrible", "worst", "never received", "lawyer", "police"]
    if any(k in content_lower for k in urgent_keywords):
        return 2

    high_keywords = ["price", "cost", "how much", "where to buy", "discount", "coupon", "problem", "not working"]
    if any(k in high_keywords for k in content_lower):
        priority = 1
    if comment.intent in ["pricing_inquiry", "product_inquiry", "complaint"]:
        priority = max(priority, 1)
    if comment.sentiment == "negative":
        priority = max(priority, 1)

    return priority


async def extract_post_learnings(
    gemini_client: GeminiClient,
    post: SocialMediaPost
) -> List[Dict[str, Any]]:
    """Extract actionable learnings from a high-performing post."""
    prompt = f"""This {post.platform.upper()} post performed very well (engagement rate: {post.engagement_rate:.1f}%):

Content: "{post.content}"
Topics: {json.dumps(post.topics)}
Hashtags: {json.dumps(post.hashtags)}

Why did this post perform well? What can the business learn from it?
Provide 1-3 specific, actionable insights.

Respond in JSON format:
{{
    "insights": [
        {{
            "insight": "Description of why it worked",
            "score": 0.9
        }}
    ]
}}"""
    try:
        response = await gemini_client.generate_response(prompt=prompt, use_functions=False, temperature=0.5)
        data = extract_json_payload(response.get("text", ""))
        return data.get("insights", []) if data else []
    except Exception as e:
        logger.error("Failed to extract post learnings", error=str(e))
        return []
