from pydantic import BaseModel

class GuardRailResponse(BaseModel):
    triggered: bool
    new_text: str
    proceed: bool

class BinaryClassificationResponse(BaseModel):
    result: bool
    reason: str