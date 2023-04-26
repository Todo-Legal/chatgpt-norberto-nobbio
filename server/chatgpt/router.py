from fastapi import APIRouter, Form, Body
from .utils import answer_query_with_context
from .manager import Resource, BotManager
from .models import Message
from fastapi.responses import JSONResponse


router = APIRouter()
resource = Resource()

@router.post('/get-answer-by-context')
async def answer_gpt(message: Message):
    print(message.prompt)
    # response = 'ok'
    response = answer_query_with_context(message.prompt, resource.df, resource.document_embeddings, show_prompt=True)
    return JSONResponse(content={'answer':response, 'status':'success'}, status_code=200)  
    # return 'si'

@router.post('/get_answer')
async def answer_gpt(message: Message):
    print(message.prompt)
    # response = 'ok'
    response = BotManager().answer_to_bot(message)#answer_query_with_gpt(query = message.prompt)
    return JSONResponse(content={'answer':response, 'status':'success'}, status_code=200)  
  
@router.post('/hello')
async def welcome(bot: str = Body(...), prompt: str = Body(...)):
    return JSONResponse(content={'answer': f"Hola, soy {bot} ¿En que te puedo ayudar?", 'status':'success'}, status_code=200)
