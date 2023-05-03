from fastapi import APIRouter, Form, Body, Depends
from .utils import answer_query_with_context, get_db
from .manager import Resource, BotManager
from .models import Message
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import crud, models, schemas
from uuid import uuid4

router = APIRouter()
resource = Resource()

@router.post('/get-answer-by-context')
async def answer_gpt(message: Message, db: Session = Depends(get_db)):
    print(message.prompt)
    # response = 'ok'
    response = answer_query_with_context(message.prompt, resource.df, resource.document_embeddings, show_prompt=True)
    return JSONResponse(content={'answer':response, 'status':'success'}, status_code=200)  
    # return 'si'

@router.post('/get_answer')
async def answer_gpt(message: Message, db: Session = Depends(get_db)):
    print(message.prompt)
    # response = 'ok'
    chat = schemas.Chat(message = message.prompt, role= 'user', author = message.bot)
    crud.add_chat(db, chat)
    chats = [i.dict() for i in crud.get_messages(db, message.bot)]
    response = BotManager().answer_to_bot(message, chats)#answer_query_with_gpt(query = message.prompt)
    chat = schemas.Chat(message = response, role= 'bot', author = message.bot)
    crud.add_chat(db, chat)
    return JSONResponse(content={'answer':response, 'status':'success'}, status_code=200)  
  
@router.post('/hello')
async def welcome(bot: str = Body(...), prompt: str = Body(...), db: Session = Depends(get_db)):
    chats = [i.dict() for i in crud.get_messages(db, bot)]
    chats.append({'role': 'bot', 'message':f"Hola, soy {bot} ¿En que te puedo ayudar hoy?" })
    return JSONResponse(content={'answer':chats , 'status':'success'}, status_code=200)
