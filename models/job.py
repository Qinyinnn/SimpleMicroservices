from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID, uuid4

class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Job ID", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    title: str = Field(..., description="Job title", json_schema_extra={"example": "Software Engineer"})
    company: str = Field(..., description="Company name", json_schema_extra={"example": "GitHub"})
    start_date: date = Field(..., description="Start date", json_schema_extra={"example": "2023-06-01"})
    end_date: Optional[date] = Field(None, description="End date (if applicable)", json_schema_extra={"example": "2025-09-01"})
    is_current: bool = Field(default=True, description="Whether this is the current job", json_schema_extra={"example": True})

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Software Engineer",
                "company": "GitHub",
                "start_date": "2023-06-01",
                "end_date": None,
                "is_current": True
            }
        }
    }
