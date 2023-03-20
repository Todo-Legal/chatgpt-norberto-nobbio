from pydantic import BaseModel

class Message(BaseModel):
    bot: str
    prompt: str
