#!/usr/bin/python
# -*- coding: utf8 -*-
from collections import Counter

import networkx as nx
import numpy as np
import spacy
from nltk import tokenize
from nltk.stem import SnowballStemmer

Languages = {
    'es': 'spanish',
}

class _graphStatistics():

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    def statistics(self):
        res = {}
        graph = self.graph
        res['number_of_nodes'] = graph.number_of_nodes()
        res['number_of_edges'] = graph.number_of_edges()
        res['PE'] = (np.array(list(Counter(graph.edges()).values())) > 1).sum()
        res['LCC'] = nx.algorithms.components.number_weakly_connected_components(graph)
        res['LSC'] = nx.algorithms.components.number_strongly_connected_components(graph)

        degrees = list(dict(graph.degree()).values())
        res['degree_average'] = np.mean(degrees)
        res['degree_std'] = np.std(degrees)

        adj_matrix = nx.to_scipy_sparse_array(graph).toarray()
        adj_matrix2 = np.dot(adj_matrix, adj_matrix)
        adj_matrix3 = np.dot(adj_matrix2, adj_matrix)

        res['L1'] = np.trace(adj_matrix)
        res['L2'] = np.trace(adj_matrix2)
        res['L3'] = np.trace(adj_matrix3)

        return res


class naiveGraph():
    def __init__(self, lang: str):
        self.lang = lang

    def _text2graph(self, text: str):
        words = tokenize.word_tokenize(text, language=Languages[self.lang])
        gr = nx.MultiDiGraph()
        gr.add_edges_from(zip(words[:-1], words[1:]))
        return gr

    def analyzeText(self, text: str):
        dgr = self._text2graph(text)
        return _graphStatistics(dgr).statistics()


class stemGraph():

    def __init__(self, lang: str):
        self.lang = lang
        self.stemmer = SnowballStemmer(Languages[self.lang])

    def _text2graph(self, text: str):
        words = tokenize.word_tokenize(text, language=Languages[self.lang])
        stemmead_words = [self.stemmer.stem(w) for w in words]

        gr = nx.MultiDiGraph()
        gr.add_edges_from(zip(stemmead_words[:-1], stemmead_words[1:]))
        return gr

    def analyzeText(self, text: str):
        dgr = self._text2graph(text)
        return _graphStatistics(dgr).statistics()


class posGraph():

    def __init__(self, lang: str):
        assert lang == "es"
        self.lang = lang
        self.nlp = spacy.load(
            "es_core_news_md"
        )

    def _text2graph(self, text: str):
        document = self.nlp(text)

        tags = [token.pos_ for token in document]
        gr = nx.MultiDiGraph()
        gr.add_edges_from(zip(tags[:-1], tags[1:]))
        return gr

    def analyzeText(self, text: str):
        dgr = self._text2graph(text)
        return _graphStatistics(dgr).statistics()


class SpeechGraph():

    def __init__(self, lang: str):
        self.lang = lang
        self.naive = naiveGraph(lang)
        self.stem = stemGraph(lang)
        self.pos = posGraph(lang)

    def get_speech_graph(self, text: str):
        naive = self.naive.analyzeText(text)
        stem = self.stem.analyzeText(text)
        pos = self.pos.analyzeText(text)

        naive = {"naive_" + k: v for k, v in naive.items()}
        stem = {"stem_" + k: v for k, v in stem.items()}
        pos = {"pos_" + k: v for k, v in pos.items()}

        return {
            **naive,
            **stem,
            **pos,
        }