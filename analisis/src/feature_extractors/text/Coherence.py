import numpy as np
from flair.data import Sentence
from flair.embeddings import WordEmbeddings
from nltk import tokenize, download

download('perluniprops')
download('nonbreaking_prefixes')
download('punkt')
download('punkt_tab')

Languages = {
    'es': 'spanish',
    'en': 'english',
    'fr': 'french',
    'it': 'italian',
    'pt': 'portuguese',
    'de': 'german'
}

def normalized_embedding(x):
    norm = np.linalg.norm(x)

    if norm == 0:
        return x

    return x / norm


class Coherence():
    def __init__(self, lang: str):
        self.lang = lang
        self.embeddings = WordEmbeddings(self.lang)

    def get_coherence(self, text: str, max_order: int = 1, coherence_level: str = 'sentence') -> dict:

        assert max_order > 0, "max_order must be greater than 0. Please, check the documentation."

        embeddings = self._get_sentences_embedding(text, coherence_level)
        max_order = min(max_order, embeddings.shape[0] - 1)

        # If max_order is 0, return None for all metrics
        if max_order == 0:
            return {
                f'order_{order}': None
                for order in range(1, max_order + 1)
            }

        # Similarity matrix
        # when embeddings are normalized the similarity matrix is the same as 
        # the multiplication of the matrix by its transpose
        m = np.array([normalized_embedding(x) for x in embeddings])
        similarity_matrix = np.dot(m, m.T)

        similarity_orders = [
            (order, np.diag(similarity_matrix, order))
            for order in range(1, max_order + 1)
        ]
        similarity_metrics = {
            f'order_{order}': self._get_statistics(s)
            for order, s in similarity_orders
        }

        # TODO: Check if I should normalize the coherence metrises as in Facu's code (ask facu if he ended up using it)
        # Normalized similarity matrix
        '''
        normalized_coeff=[ list(map(np.mean,zip(len_words_per_vectors[:-i],len_words_per_vectors[i:]))) for i in range(1,max_order)]
        similarity_orders_normalized = [ s/ np.array(coeff_list) for s, coeff_list in zip(similarity_orders,normalized_coeff)]
        similarity_metrics_normalized = { 'normalized_order_'+str(i):self._get_statistics(s) for i,s in enumerate(similarity_orders_normalized) }
        similarity_metrics.update(similarity_metrics_normalized)	
        '''

        return similarity_metrics

    def _get_statistics(self, s):
        res = {
            'mean': np.mean(s),
            'std': np.std(s),
            'min': np.min(s),
            'max': np.max(s),
            'median': np.median(s),
            'percentile_1': np.percentile(s, 1),
            'percentile_5': np.percentile(s, 5),
            'percentile_10': np.percentile(s, 10),
            'percentile_25': np.percentile(s, 25),
            'percentile_75': np.percentile(s, 75),
            'percentile_90': np.percentile(s, 90),
            'percentile_95': np.percentile(s, 95),
            'percentile_99': np.percentile(s, 99)
        }
        return res

    def _get_sentences_embedding(self, text: str, coherence_level: str = 'sentence'):

        # Sentence tokenization (from paper)
        sentences = tokenize.sent_tokenize(text, language=Languages[self.lang])
        sentences = [Sentence(sent) for sent in sentences]

        # Sentences words embedding (from paper)
        res = []
        for sent in sentences:
            self.embeddings.embed(sent)
            # |sentences| x |words| x |embedding|
            res.append(np.array([word.embedding.cpu().numpy() for word in sent]))

        # Coherence level
        # if Word level, ceate a sentence for each word
        if coherence_level == 'word':
            res = np.concatenate(res, axis=0)
            n_words, embedding_dims = res.shape
            res = res.reshape(n_words, 1, embedding_dims)

        # Summary vector (from paper)
        res = np.array([np.mean(sent, axis=0) for sent in res])

        return res