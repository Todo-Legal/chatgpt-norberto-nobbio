import pandas as pd
try:
    import cPickle as pickle
except ImportError:  # Python 3.x
    import pickle

from .utils import answer_query_with_context, answer_query_with_gpt, answer_query_prox_with_gpt,\
    search
from .models import Message

class Resource:

    def __init__(self):

        self.df = pd.read_csv('./server/resources/dataset_1.csv')
        self.df = self.df.set_index(["title", "heading"])
        self.document_embeddings = None
        with open('./server/resources/document_embeddings.data', 'rb') as fp:
            self.document_embeddings = pickle.load(fp)

class BotManager:

    def answer_to_bot(self, message: Message, chats = []):
        response = None
        if message.bot == 'ProxTrainer':
            response = search(query = message.prompt)#answer_query_prox_with_gpt(query = message.prompt)
        else:
            response = answer_query_with_gpt(query = message.prompt, history = chats)
        return response
    
