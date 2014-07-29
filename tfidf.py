import math

class TfIdf():

    def __init__(self, documents):
        self.documents = documents

    def compute_tf(self, word, document):
        return float(document.words.count(word)) / len(document.words)

    def compute_idf(self, word):
        count_docs = sum(1 for doc in self.documents if word in doc)
        return math.log(float(len(self.documents)) / (1 + count_docs))

    def compute_tfidf(self, word, document):
        return self.compute_tf(word, document) * self.compute_idf(word)