
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Chat(Base):

    __tablename__ = 'chat'

    id = Column(String, primary_key = True)
    message = Column(String)
    role = Column(String)
    author = Column(String)

    def dict(self):
        return {
            'message': self.message,
            'role': self.role,
            'author': self.author
        }
