"""
Event Bus Service
Implements publish/subscribe pattern using Redis Streams for event-driven architecture.
"""
from typing import Dict, List, Any, Optional, Callable
import json
import uuid
from datetime import datetime
import asyncio
import structlog
from redis import asyncio as aioredis
from app.core.config import settings

logger = structlog.get_logger(__name__)


class EventTypes:
    """Event type constants for the application."""
    
    # Order events
    ORDER_CREATED = 'orders.created'
    ORDER_UPDATED = 'orders.updated'
    ORDER_FULFILLED = 'orders.fulfilled'
    ORDER_CANCELLED = 'orders.cancelled'
    
    # Message events
    MESSAGE_RECEIVED = 'message.received'
    MESSAGE_SENT = 'message.sent'
    MESSAGE_READ = 'message.read'
    MESSAGE_FAILED = 'message.failed'
    
    # AI events
    AI_RESPONSE_GENERATED = 'ai.responded'
    AI_CONFIDENCE_LOW = 'ai.confidence.low'
    AI_ESCALATED = 'ai.escalated'
    AI_TRAINING_COMPLETED = 'ai.training.completed'
    
    # Customer events
    CUSTOMER_CREATED = 'customer.created'
    CUSTOMER_UPDATED = 'customer.updated'
    CUSTOMER_DELETED = 'customer.deleted'
    
    # Social events
    COMMENT_RECEIVED = 'social.comment.received'
    POST_PUBLISHED = 'social.post.published'
    SOCIAL_ACCOUNT_CONNECTED = 'social.account.connected'
    
    # Integration events
    INTEGRATION_CONNECTED = 'integration.connected'
    INTEGRATION_DISCONNECTED = 'integration.disconnected'
    INTEGRATION_ERROR = 'integration.error'
    
    # Analytics events
    ANALYTICS_GENERATED = 'analytics.generated'
    REPORT_CREATED = 'report.created'


class EventBus:
    """
    Event bus for publishing and subscribing to events using Redis Streams.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: Optional[aioredis.Redis] = None
        self.max_stream_length = 10000
        self.subscribers: Dict[str, List[Callable]] = {}
    
    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            logger.info("Event bus connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("Event bus disconnected from Redis")
    
    async def publish(
        self,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish an event to the event bus.
        
        Args:
            event_type: Type of event (e.g., 'orders.created')
            payload: Event data
            metadata: Optional metadata (user_id, project_id, etc.)
            
        Returns:
            Event ID
        """
        await self.connect()
        
        event_id = str(uuid.uuid4())
        event = {
            'id': event_id,
            'type': event_type,
            'payload': json.dumps(payload),
            'metadata': json.dumps(metadata or {}),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            # Publish to specific event type stream
            stream_key = f'events:{event_type}'
            await self.redis.xadd(
                stream_key,
                event,
                maxlen=self.max_stream_length
            )
            
            # Also publish to general events stream
            await self.redis.xadd(
                'events:all',
                event,
                maxlen=self.max_stream_length
            )
            
            logger.info(
                "Event published",
                event_id=event_id,
                event_type=event_type
            )
            
            return event_id
            
        except Exception as e:
            logger.error(
                "Failed to publish event",
                event_type=event_type,
                error=str(e)
            )
            raise
    
    async def subscribe(
        self,
        event_types: List[str],
        consumer_group: str,
        consumer_name: str,
        handler: Callable
    ):
        """
        Subscribe to events and process them with a handler.
        
        Args:
            event_types: List of event types to subscribe to
            consumer_group: Consumer group name
            consumer_name: Consumer name within group
            handler: Async function to handle events
        """
        await self.connect()
        
        # Create consumer groups if they don't exist
        for event_type in event_types:
            stream_key = f'events:{event_type}'
            try:
                await self.redis.xgroup_create(
                    stream_key,
                    consumer_group,
                    id='0',
                    mkstream=True
                )
                logger.info(
                    "Consumer group created",
                    stream=stream_key,
                    group=consumer_group
                )
            except Exception:
                # Group already exists
                pass
        
        # Start consuming
        logger.info(
            "Starting event consumer",
            event_types=event_types,
            group=consumer_group,
            consumer=consumer_name
        )
        
        while True:
            try:
                # Read from all subscribed streams
                streams = {f'events:{t}': '>' for t in event_types}
                
                messages = await self.redis.xreadgroup(
                    consumer_group,
                    consumer_name,
                    streams,
                    count=10,
                    block=5000  # 5 second timeout
                )
                
                if messages:
                    for stream, events in messages:
                        for event_id, event_data in events:
                            try:
                                # Parse event
                                event = {
                                    'id': event_data['id'],
                                    'type': event_data['type'],
                                    'payload': json.loads(event_data['payload']),
                                    'metadata': json.loads(event_data['metadata']),
                                    'timestamp': event_data['timestamp']
                                }
                                
                                # Handle event
                                await handler(event)
                                
                                # Acknowledge event
                                await self.redis.xack(
                                    stream,
                                    consumer_group,
                                    event_id
                                )
                                
                            except Exception as e:
                                logger.error(
                                    "Error processing event",
                                    event_id=event_id,
                                    error=str(e)
                                )
                                # Event will be retried or sent to DLQ
                
            except Exception as e:
                logger.error("Error in event consumer", error=str(e))
                await asyncio.sleep(5)  # Wait before retry
    
    async def get_pending_events(
        self,
        event_type: str,
        consumer_group: str
    ) -> List[Dict]:
        """
        Get pending events that haven't been acknowledged.
        
        Args:
            event_type: Event type
            consumer_group: Consumer group
            
        Returns:
            List of pending events
        """
        await self.connect()
        
        stream_key = f'events:{event_type}'
        pending = await self.redis.xpending(
            stream_key,
            consumer_group
        )
        
        return pending


class IdempotentEventHandler:
    """
    Ensures events are processed exactly once using Redis for deduplication.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis: Optional[aioredis.Redis] = None
        self.ttl = 86400  # 24 hours
    
    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)
    
    async def is_processed(self, event_id: str) -> bool:
        """Check if event has been processed."""
        await self.connect()
        key = f'processed:{event_id}'
        return await self.redis.exists(key) > 0
    
    async def mark_processed(self, event_id: str):
        """Mark event as processed."""
        await self.connect()
        key = f'processed:{event_id}'
        await self.redis.setex(key, self.ttl, 'true')
    
    async def handle_event(
        self,
        event: Dict[str, Any],
        handler: Callable
    ) -> Dict[str, Any]:
        """
        Handle event with idempotency guarantee.
        
        Args:
            event: Event data
            handler: Handler function
            
        Returns:
            Handler result or skip status
        """
        event_id = event['id']
        
        # Check if already processed
        if await self.is_processed(event_id):
            logger.info("Event already processed", event_id=event_id)
            return {'status': 'already_processed', 'event_id': event_id}
        
        try:
            # Process event
            result = await handler(event)
            
            # Mark as processed
            await self.mark_processed(event_id)
            
            logger.info("Event processed successfully", event_id=event_id)
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            logger.error(
                "Event processing failed",
                event_id=event_id,
                error=str(e)
            )
            
            # Send to dead letter queue
            await self.send_to_dlq(event, str(e))
            
            raise
    
    async def send_to_dlq(self, event: Dict[str, Any], error: str):
        """Send failed event to dead letter queue."""
        await self.connect()
        
        dlq_event = {
            'event_id': event['id'],
            'event_type': event['type'],
            'payload': json.dumps(event['payload']),
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.redis.xadd('events:dead_letter', dlq_event)
        
        logger.warning(
            "Event sent to DLQ",
            event_id=event['id'],
            error=error
        )


# Global event bus instance
event_bus = EventBus()
idempotent_handler = IdempotentEventHandler()
