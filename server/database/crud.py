from sqlalchemy.orm import Session
from . import models, schemas
from uuid import uuid4

def add_chat(db: Session, chat: schemas.Chat):
    db_chat = models.Chat(id = str(uuid4()), message = chat.message, role = chat.role, author = chat.author)

    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat.id


def get_messages(db: Session, author: str, skip: int = 0, limit: int = 20):
    response = []
    try:
        response = db.query(models.Chat).filter(models.Chat.author == author).limit(limit).all()
    except Exception as e:
        print('Error get messages', e)
    
    return  response


