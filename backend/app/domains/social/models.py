from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, Index, JSON, Enum as SQLEnum, LargeBinary, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SocialMediaComment(Base):
    """Social media comments/posts to respond to."""
    __tablename__ = "social_media_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Platform info
    platform = Column(String(50), nullable=False)  # instagram, facebook, tiktok
    external_id = Column(String(255), nullable=False)  # Platform comment ID
    post_id = Column(String(255))  # Parent post ID
    
    # Comment details
    content = Column(Text, nullable=False)
    author_username = Column(String(255))
    author_id = Column(String(255))
    
    # Response tracking
    responded = Column(Boolean, default=False)
    response_content = Column(Text)
    response_sent_at = Column(DateTime(timezone=True))
    auto_generated = Column(Boolean, default=False)
    
    # AI analysis
    sentiment = Column(String(50))  # positive, negative, neutral, question
    intent = Column(String(100))  # product_inquiry, complaint, praise, etc.
    requires_human = Column(Boolean, default=False)  # Escalate to human
    
    # Priority
    priority = Column(Integer, default=0)  # 0=normal, 1=high, 2=urgent
    
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="social_comments")
    
    # Indexes
    __table_args__ = (
        Index("idx_social_comment_project", "project_id"),
        Index("idx_social_comment_platform_external", "platform", "external_id"),
        Index("idx_social_comment_responded", "responded"),
    )
    
    def __repr__(self):
        return f"<SocialMediaComment {self.platform} - {self.external_id}>"



class SocialMediaPost(Base):
    """Track social media posts for monitoring and engagement."""
    __tablename__ = "social_media_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Platform info
    platform = Column(String(50), nullable=False)  # instagram, facebook, tiktok, twitter
    external_id = Column(String(255), nullable=False, unique=True)  # Platform post ID
    post_url = Column(String(500))
    
    # Post content
    content = Column(Text)  # Caption/text content
    media_type = Column(String(50))  # image, video, carousel, story
    media_urls = Column(JSONB, default=[])  # Array of media URLs
    
    # Author info (usually the business itself)
    author_username = Column(String(255))
    author_id = Column(String(255))
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # AI analysis
    ai_analyzed = Column(Boolean, default=False)
    sentiment = Column(String(50))  # overall sentiment of comments
    topics = Column(JSONB, default=[])  # Main topics discussed
    keywords = Column(JSONB, default=[])  # Extracted keywords
    ai_summary = Column(Text)  # AI-generated summary of post and comments
    
    # Comment monitoring
    last_comment_check = Column(DateTime(timezone=True))
    unresponded_comments = Column(Integer, default=0)
    
    # Performance tracking
    engagement_rate = Column(Float)  # Calculated engagement percentage
    best_performing = Column(Boolean, default=False)  # Flag for high-performing posts
    
    # Metadata
    hashtags = Column(JSONB, default=[])
    mentions = Column(JSONB, default=[])
    location = Column(String(255))
    
    extra_data = Column(JSONB, default={})
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="social_posts")
    
    # Indexes
    __table_args__ = (
        Index("idx_social_post_project", "project_id"),
        Index("idx_social_post_platform_external", "platform", "external_id"),
        Index("idx_social_post_engagement", "engagement_rate"),
        Index("idx_social_post_posted_at", "posted_at"),
    )
    
    def __repr__(self):
        return f"<SocialMediaPost {self.platform} - {self.external_id}>"

