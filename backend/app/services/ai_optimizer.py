"""
AI Usage Optimization Service.
Reduces costs through caching, prompt optimization, and smart model selection.
"""

from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime, timedelta
from redis import asyncio as aioredis
import structlog

logger = structlog.get_logger(__name__)


class AIOptimizer:
    """
    Optimize AI usage to reduce costs while maintaining quality.
    
    Strategies:
    1. Cache common responses
    2. Optimize prompts (reduce tokens)
    3. Use cheaper models for simple tasks
    4. Batch similar requests
    """
    
    def __init__(self):
        self.cache = {}  # In-memory cache (use Redis in production)
        self.cache_ttl = 3600  # 1 hour
        
    def optimize_prompt(self, prompt: str, task_type: str = "general") -> str:
        """
        Optimize prompt to use fewer tokens while maintaining quality.
        
        Strategies:
        - Remove unnecessary words
        - Use abbreviations where clear
        - Compress repetitive instructions
        """
        optimized = prompt
        
        # Remove excessive whitespace
        optimized = " ".join(optimized.split())
        
        # Common replacements to reduce tokens
        replacements = {
            "please respond with": "respond:",
            "I would like you to": "",
            "Could you please": "",
            "based on the following information": "given:",
            "information": "info",
            "customer": "cust",
            "message": "msg",
            "product": "prod",
            "generate a response": "reply:",
            "analyze the sentiment": "sentiment:",
            "extract the following": "extract:",
        }
        
        for old, new in replacements.items():
            optimized = optimized.replace(old, new)
        
        # Task-specific optimization
        if task_type == "sentiment":
            # Shorter prompt for sentiment analysis
            optimized = optimized.replace(
                "Analyze the sentiment and provide detailed analysis",
                "Sentiment (positive/neutral/negative):"
            )
        elif task_type == "order_extraction":
            # More concise order extraction
            optimized = optimized.replace(
                "Extract order details including products, quantities, and customer information",
                "Extract: products, qty, customer"
            )
        
        logger.info(
            "Prompt optimized",
            original_length=len(prompt),
            optimized_length=len(optimized),
            savings=len(prompt) - len(optimized)
        )
        
        return optimized
    
    def _generate_cache_key(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate cache key from prompt and context."""
        cache_string = f"{prompt}:{json.dumps(context or {}, sort_keys=True)}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def get_cached_response(
        self,
        prompt: str,
        context: Optional[Dict] = None
    ) -> Optional[str]:
        """Get cached response if available."""
        cache_key = self._generate_cache_key(prompt, context)
        
        cached = self.cache.get(cache_key)
        if cached and cached["expires_at"] > datetime.utcnow():
            logger.info("Cache hit", cache_key=cache_key)
            return cached["response"]
        
        return None
    
    async def cache_response(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict] = None,
        ttl: int = None
    ):
        """Cache AI response."""
        cache_key = self._generate_cache_key(prompt, context)
        ttl = ttl or self.cache_ttl
        
        self.cache[cache_key] = {
            "response": response,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
        }
        
        logger.info("Response cached", cache_key=cache_key, ttl=ttl)
    
    def should_use_cache(self, task_type: str) -> bool:
        """Determine if task type should use caching."""
        # Cache these types of requests
        cacheable_types = [
            "sentiment_analysis",
            "common_faq",
            "template_response",
            "product_info",
            "business_hours"
        ]
        
        return task_type in cacheable_types
    
    def select_optimal_model(self, task_type: str, complexity: str = "medium") -> Dict[str, Any]:
        """
        Select the most cost-effective model for the task.
        
        Returns model config with temperature and max_tokens optimized.
        """
        # Model selection based on task complexity
        configs = {
            "simple": {
                "model": "gemini-2.0-flash",  # Fastest, cheapest
                "temperature": 0.3,
                "max_tokens": 150,
                "use_case": "sentiment, classification, yes/no"
            },
            "medium": {
                "model": "gemini-2.0-flash",
                "temperature": 0.7,
                "max_tokens": 500,
                "use_case": "responses, summaries, extraction"
            },
            "complex": {
                "model": "gemini-2.0-flash",
                "temperature": 0.9,
                "max_tokens": 1500,
                "use_case": "creative, long-form, detailed"
            }
        }
        
        # Task-specific overrides
        task_complexity = {
            "sentiment": "simple",
            "classification": "simple",
            "yes_no": "simple",
            "extract_order": "medium",
            "generate_response": "medium",
            "summarize": "medium",
            "creative_writing": "complex",
            "detailed_analysis": "complex"
        }
        
        complexity = task_complexity.get(task_type, complexity)
        config = configs.get(complexity, configs["medium"])
        
        logger.info("Model selected", task_type=task_type, complexity=complexity)
        
        return config
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (1 token ≈ 4 characters)."""
        return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate AI cost based on Gemini pricing.
        
        Gemini 2.0 Flash (if paid):
        - Input: $0.075 per 1M tokens
        - Output: $0.30 per 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
        return input_cost + output_cost
    
    async def batch_similar_requests(
        self,
        requests: list[Dict[str, Any]]
    ) -> list[str]:
        """
        Batch similar requests to reduce API calls.
        
        Combine multiple similar requests into one AI call.
        """
        if len(requests) <= 1:
            return requests
        
        # Group by similarity (task type, context)
        batches = {}
        for req in requests:
            task_type = req.get("task_type", "general")
            if task_type not in batches:
                batches[task_type] = []
            batches[task_type].append(req)
        
        logger.info("Requests batched", total=len(requests), batches=len(batches))
        
        return batches
    
    def compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress context to reduce token usage.
        
        - Remove unnecessary fields
        - Truncate long strings
        - Summarize arrays
        """
        compressed = {}
        
        for key, value in context.items():
            if isinstance(value, str):
                # Truncate very long strings
                if len(value) > 500:
                    compressed[key] = value[:500] + "..."
                else:
                    compressed[key] = value
            elif isinstance(value, list):
                # Limit array size
                if len(value) > 5:
                    compressed[key] = value[:5] + [f"...{len(value)-5} more"]
                else:
                    compressed[key] = value
            elif isinstance(value, dict):
                # Recursively compress nested dicts
                compressed[key] = self.compress_context(value)
            else:
                compressed[key] = value
        
        return compressed
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        cache_size = len(self.cache)
        
        # Clean expired cache
        now = datetime.utcnow()
        expired = [k for k, v in self.cache.items() if v["expires_at"] <= now]
        for key in expired:
            del self.cache[key]
        
        return {
            "cache_size": cache_size,
            "cache_active": len(self.cache),
            "cache_expired": len(expired),
            "estimated_savings_tokens": cache_size * 300,  # Rough estimate
            "estimated_savings_cost": (cache_size * 300 / 1_000_000) * 0.20
        }


# Global optimizer instance
ai_optimizer = AIOptimizer()
