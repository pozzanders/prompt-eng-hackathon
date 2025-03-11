from pydantic import BaseModel

class GuardRailResponse(BaseModel):
    triggered: bool
    new_text: str
    exclude: bool
    reason: str

class BinaryClassificationResponse(BaseModel):
    result: bool
    reason: str