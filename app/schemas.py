from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NewsClassificationBase(BaseModel):
    """Base schema for NewsClassification"""

    review: str
    label: str


class NewsClassificationCreate(NewsClassificationBase):
    """Schema for creating a NewsClassification"""

    pass


class NewsClassificationUpdate(BaseModel):
    """Schema for updating a NewsClassification"""

    review: Optional[str] = None
    label: Optional[str] = None


class NewsClassificationResponse(NewsClassificationBase):
    """Schema for NewsClassification response"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
