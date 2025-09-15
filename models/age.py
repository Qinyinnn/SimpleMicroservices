from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class Age(BaseModel):
    person_name: str = Field(..., description="Full name of the person", json_schema_extra={"example": "Ada Lovelace"})
    birth_date: date = Field(..., description="Date of birth (YYYY-MM-DD)", json_schema_extra={"example": "1815-12-10"})
    current_age: Optional[int] = Field(None, description="Calculated age in years", json_schema_extra={"example": 36})

    model_config = {
        "json_schema_extra": {
            "example": {
                "person_name": "Ada Lovelace",
                "birth_date": "1815-12-10",
                "current_age": 36
            }
        }
    }
