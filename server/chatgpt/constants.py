import os

from dotenv import load_dotenv

load_dotenv()

class Environment:
    OPENAI_API: str = os.getenv('OPENIA_API')