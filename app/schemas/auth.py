from pydantic import BaseModel

class TokenData(BaseModel):
    email : str
    
class LoginData(BaseModel):
    email : str
    password : str