import pandas as pd
try:
    import cPickle as pickle
except ImportError:  # Python 3.x
    import pickle



class Resource:

    def __init__(self):

        self.df = pd.read_csv('resources/dataset_1.csv')
        self.df = self.df.set_index(["title", "heading"])
        self.document_embeddings = None
        with open('resources/document_embeddings.data', 'rb') as fp:
            self.document_embeddings = pickle.load(fp)

