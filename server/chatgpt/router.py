from fastapi import APIRouter, Form
from .utils import answer_query_with_context
from .manager import Resource
from .models import Message
from fastapi.responses import JSONResponse


router = APIRouter()
resource = Resource()

@router.post('/get_answer')
async def answer_gpt(message: Message):
    print(message.prompt)
    # response = 'ok'
    response = answer_query_with_context(message.prompt, resource.df, resource.document_embeddings, show_prompt=True)
    return JSONResponse(content={'answer':response, 'status':'success'}, status_code=200)  
    # return 'si'
