from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"

class NotificationType(str, Enum):
    EMAIL = "email"

class CreateNotification(SQLModel):
    user_id: int
    email: str
    message: str

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    notification_type: NotificationType
    message: str
    status: NotificationStatus = NotificationStatus.QUEUED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

