from fastapi import FastAPI
from .chatgpt.router import router
from fastapi.middleware.cors import CORSMiddleware

from .database import crud, models, schemas
from .database.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


# origins = [
#     "http://localhost",
#     "http://localhost:5000",
# ]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
