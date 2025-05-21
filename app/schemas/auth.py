from pydantic import BaseModel, Field, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
    
class ChangePasswordByTokenRequest(BaseModel):
    new_password: str = Field(..., min_length=8)
    retype_new_password: str = Field(..., min_length=8)
