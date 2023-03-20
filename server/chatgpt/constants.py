import os

from dotenv import load_dotenv

load_dotenv()

class Environment:
    OPENAI_API: str = os.getenv('OPENIA_API')
    MAX_SECTION_LEN: str = os.getenv('MAX_SECTION_LEN', 2000)
