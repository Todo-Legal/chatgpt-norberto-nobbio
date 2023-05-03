 

from pydantic import BaseModel


class Chat(BaseModel):

    message: str
    role: str 
    author: str 
    
    class Config:
        orm_mode = True