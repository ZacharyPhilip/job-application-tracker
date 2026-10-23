"""Request and response models. Pydantic validates incoming data against these."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["wishlist", "applied", "interview", "offer", "rejected"]


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    company: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    status: Status = "wishlist"
    applied_date: Optional[date] = None
    url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)


class ApplicationOut(BaseModel):
    id: int
    company: str
    role: str
    status: Status
    applied_date: Optional[date] = None
    url: Optional[str] = None
    notes: Optional[str] = None