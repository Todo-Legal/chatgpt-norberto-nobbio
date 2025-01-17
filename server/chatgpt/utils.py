
import os
import openai
import tiktoken
import pandas as pd
import numpy as np
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..database import crud

from .constants import Environment, PATH
openai.api_key = Environment.OPENAI_API
os.environ['OPENAI_API_KEY'] = Environment.OPENAI_API
MAX_SECTION_LEN = int(Environment.MAX_SECTION_LEN)
SEPARATOR = "\n* "
ENCODING = "gpt2"  # encoding for text-davinci-003

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

f"Context separator contains {separator_len} tokens"

## LLAMA-index
DIRECTORY = PATH.PROXTRAINER

# %%
EMBEDDING_MODEL = "text-embedding-ada-002"
def get_embedding(text: str, model: str=EMBEDDING_MODEL):
    result = openai.Embedding.create(
      model=model,
      input=text
    )
    return result["data"][0]["embedding"]

# %%
def vector_similarity(x, y):
    """
    Returns the similarity between two vectors.
    
    Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
    """
    return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(query, contexts) :
    """
    Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
    to find the most relevant sections. 
    
    Return the list of document sections, sorted by relevance in descending order.
    """
    query_embedding = get_embedding(query)
    
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)
    
    return document_similarities

# %%
def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame):
    """
    Fetch relevant 
    """
    most_relevant_document_sections = order_document_sections_by_query_similarity(question, context_embeddings)
    
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []
     
    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.        
        document_section = df.loc[section_index[1:]]
        
        chosen_sections_len += document_section.tokens + separator_len
        print(chosen_sections_len)
        if isinstance(chosen_sections_len,np.int64 ) and chosen_sections_len > MAX_SECTION_LEN:
            break
        elif isinstance(chosen_sections_len,list) and chosen_sections_len[0] > MAX_SECTION_LEN:
            break
        chosen_sections.append(SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index[1:]))
            
    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))
    
    header = """Answer the question as truthfully as possible using your information and the context provided, paraphrase the answer and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    
    return header + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:", "".join(chosen_sections)

# %%
COMPLETIONS_MODEL = "text-davinci-003"
COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 600,
    "model": COMPLETIONS_MODEL,
}

# %%
def answer_query_with_context(
    query: str,
    df: pd.DataFrame,
    document_embeddings,
    show_prompt: bool = False
) -> str:
    prompt = construct_prompt(
        query,
        document_embeddings,
        df
    )
    contexts = prompt[1]
    prompt = prompt[0]
    if show_prompt:
        print(prompt)

    response = openai.ChatCompletion.create(
                # prompt=prompt,
                model="gpt-3.5-turbo",
                temperature =  0.0,
                messages=[
                    {"role": "system", "content": f"Answer the question as truthfully as possible using your information and the context provided, paraphrase the answer and if the answer is not contained within the text below, say I don't know.{contexts}"},
                    {"role": "user", "content": query}
                ]
                # **COMPLETIONS_API_PARAMS
            )
    return response["choices"][0]["message"]["content"]

def generate_message_structure(chats):
    messages = [{"role": "system", "content": f"Answer the question as truthfully as possible using your information and pdf's of this drive: https://drive.google.com/drive/folders/1a57LtGGr_ComDjAwYVef2IUOsFrQljub?usp=sharing, paraphrase the answer and limit your answers to questions of law only, say I don't know in other cases"},]
    for chat in chats:
        messages.append({
            "role": 'assistant' if chat.get('role', '') == 'bot' else 'user', 
            "content": chat.get('message')
        })
    return messages
def answer_query_with_gpt(
    ** kargs,
) -> str:

    query = kargs.get('query')
    history = kargs.get('history')
    messages = generate_message_structure(history)
    response = openai.ChatCompletion.create(
                # prompt=prompt,
                model="gpt-3.5-turbo",
                temperature =  0.0,
                messages = messages
                # messages=[
                #     {"role": "system", "content": f"Answer the question as truthfully as possible using your information and pdf's of this drive: https://drive.google.com/drive/folders/1a57LtGGr_ComDjAwYVef2IUOsFrQljub?usp=sharing, paraphrase the answer and limit your answers to questions of law only, say I don't know in other cases"},
                #     {"role": "user", "content": "My name is Moises"},
                #     {"role": "user", "content": query}
                # ]
                # **COMPLETIONS_API_PARAMS
            )
    return response["choices"][0]["message"]["content"]

def answer_query_prox_with_gpt(
    ** kargs,
) -> str:

    query = kargs.get('query')
    response = openai.ChatCompletion.create(
                # prompt=prompt,
                model="gpt-3.5-turbo",
                temperature =  0.0,
                messages=[
                    {"role": "system", "content": f"Answer the question as truthfully as possible using your information and pdf's of this drive: https://drive.google.com/drive/folders/1a57LtGGr_ComDjAwYVef2IUOsFrQljub?usp=sharing, say I don't know in other cases"},
                    {"role": "user", "content": query}
                ]
                # **COMPLETIONS_API_PARAMS
            )
    return response["choices"][0]["message"]["content"]


# %%
def search(query):
    try:
        documents = SimpleDirectoryReader(DIRECTORY).load_data()
    except AttributeError:
        print(f'ERROR trying to load {DIRECTORY} ')
        return 
    index = GPTSimpleVectorIndex.from_documents(documents)

    response = index.query(query)
    
    return response.response

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
