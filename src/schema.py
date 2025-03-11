from typing import Optional
from pydantic import BaseModel

class GuardRailResponse(BaseModel):
    triggered: bool
    rewritten: str
    fallback: Optional[str]
    reason: str

class BinaryClassificationResponse(BaseModel):
    result: bool
    reason: str