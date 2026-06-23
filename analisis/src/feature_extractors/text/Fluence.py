import numpy as np
import spacy
import textstat
from nltk import tokenize

from src.feature_extractors.text.utils import ensure_model_installed
        
ensure_model_installed('es_core_news_lg')
ensure_model_installed('en_core_web_lg')

Languages = {
    'es': 'spanish',
    'en': 'english',
    'fr': 'french', 
    'it': 'italian',
    'pt': 'portuguese',
    'de': 'german'
}

functions = [
    textstat.fernandez_huerta, 
    textstat.szigriszt_pazos,
    textstat.gutierrez_polini,
    textstat.crawford
]

class Fluence():

    def __init__(self, lang: str):

        assert lang in ['es', 'en'], 'Only spanish and English are supported at the moment.'

        SPACY_MODELS = {
            'es': 'es_core_news_lg',
            'en': 'en_core_web_lg'
        }

        self.lang = lang
        self.nlp = spacy.load(SPACY_MODELS[self.lang])
        textstat.set_lang(self.lang)

    def get_postag(self, text: str):
        
        POSTAGS = [
            "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
            "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "OTHER"
        ]
        tags = {tag: 0 for tag in POSTAGS}

        for token in self.nlp(text):
            if token.pos_ not in tags:
                tags['OTHER'] += 1
            else:
                tags[token.pos_] += 1

        n_tags = sum(tags.values())
        return {
            k: {'count': v, 'freq': v / n_tags}
            for k, v in tags.items()
        }

    def get_total_words(self, text: str):
        # count words using word tokenizer
        words = tokenize.word_tokenize(text, language=Languages[self.lang])
        return len(words)

    def get_words_per_sentence(self, text: str):
        sentences = tokenize.sent_tokenize(text, language=Languages[self.lang])

        # count words per sentence using word tokenizer
        words_per_sentence = np.array([
            len(tokenize.word_tokenize(sentence, language=Languages[self.lang]))
            for sentence in sentences
        ])

        return {
            'mean': np.mean(words_per_sentence),
        }

    def get_lexical_complexity(self, text: str):
        res = {}
        for function in functions:
            try:
                res[function.__name__] = function(text)
            except:
                pass

        return res

    def get_unique_words_ratio(self, text: str):
        # calculate the lexical complexity of the text
        document = self.nlp(text)
        n_words = len(document)
        n_unique_words = len(set([token.text for token in document]))

        return (n_unique_words / n_words)

    def get_fluence(self, text: str):

        return {
            'postags': self.get_postag(text),
            'total_words': self.get_total_words(text),
            'words_per_sentence': self.get_words_per_sentence(text),
            'unique_words_ratio': self.get_unique_words_ratio(text),
            'lexical_complexity': self.get_lexical_complexity(text)
        }