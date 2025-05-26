from pydantic import BaseModel, EmailStr

class UserSchema(BaseModel):
    email: EmailStr
    name: str
    role: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str 