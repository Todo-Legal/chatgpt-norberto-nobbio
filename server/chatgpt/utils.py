# %%
try:
    import cPickle as pickle
except ImportError:  # Python 3.x
    import pickle

import openai
import tiktoken
import pandas as pd
import numpy as np

from .constants import Environment
openai.api_key = Environment.OPENAI_API
MAX_SECTION_LEN = Environment.MAX_SECTION_LEN
SEPARATOR = "\n* "
ENCODING = "gpt2"  # encoding for text-davinci-003

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

f"Context separator contains {separator_len} tokens"

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
        document_section = df.loc[section_index]
        
        chosen_sections_len += document_section.tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break
            
        chosen_sections.append(SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))
            
    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))
    
    header = """Answer the question as truthfully as possible using the provided context, paraphrase the answer and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    
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
                    {"role": "system", "content": f"Answer the question as truthfully as possible using the provided context, paraphrase the answer and if the answer is not contained within the text below, say I don't know.{contexts}"},
                    {"role": "user", "content": query}
                ]
                # **COMPLETIONS_API_PARAMS
            )
    return response["choices"][0]["message"]["content"]

# %%

# answer_query_with_context("¿Cuáles son los parámetros mínimos que deben cumplir los tratamientos de datos relativos a la salud, según la normativa emitida por la autoridad de protección de datos personales?", df, document_embeddings, show_prompt=True)
