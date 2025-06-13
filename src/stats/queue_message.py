from pydantic import BaseModel

class CreateStatsMessage(BaseModel):
    email: str
    timestamp: str
