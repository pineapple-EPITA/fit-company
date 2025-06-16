from pydantic import BaseModel

class CreateWodMessage(BaseModel):
    email: str

class CreatePerformedMessage(BaseModel):
    email: str
    workout_id: int 
    
    
    