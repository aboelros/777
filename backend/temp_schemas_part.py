
# ============================================================================
# Message Schemas
# ============================================================================

class MessageSend(BaseModel):
    recipient: Dict[str, Any]
    content: str
    content_type: str = "text"
    provider: Provider
    order_id: Optional[UUID] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class MessageResponse(BaseModel):
    id: UUID
    project_id: UUID
    order_id: Optional[UUID]
    customer_id: Optional[UUID]
    direction: MessageDirection
    channel: Optional[str] = None # combined provider/platform
    provider: str
    platform: Optional[str] = None
    content: Optional[str]
    content_type: str
    status: str
    is_read: bool = False
    created_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    sender: Optional[Dict[str, Any]]
    recipient: Optional[Dict[str, Any]]
    attachments: Optional[List[Dict[str, Any]]] = None
    ai_generated: bool = False
    human_override: bool = False
    
    # Enriched fields
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    channel: str
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    customer_avatar: Optional[str]
    customer_id: Optional[str]
    order_id: Optional[str]
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int = 0
    total_messages: int = 0
    ai_messages: int = 0
    ai_enabled: bool = False
    recipient: Dict[str, Any] = {}
    profile_id: Optional[str] = None # UUID as string
    overall_sentiment: Optional[str] = None
    is_vip: bool = False


class ConversationMessage(BaseModel):
    # This might be used for simplified message view in some contexts
    id: UUID
    content: str
    direction: MessageDirection
    created_at: datetime
    is_read: bool
