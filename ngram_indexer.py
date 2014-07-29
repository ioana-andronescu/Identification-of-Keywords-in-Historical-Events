import lucene
from org.apache.lucene.store import *
from org.apache.lucene.analysis.standard import *
from org.apache.lucene.util import *
from org.apache.lucene.index import *
from org.apache.lucene.document import *
from org.apache.lucene.queryparser.classic import *
from org.apache.lucene.search import *
from java.io import *
import os

'''
    Indexes the .csv uni-grams from http://storage.googleapis.com/books/ngrams/books/datasetsv2.html
'''


class GoogleNgram():

    def __init__(self, ngram_path, index_path):
        self.ngram_path = ngram_path
        self.index_path = index_path

        # Initialize lucene and JVM
        lucene.initVM()

    def build_ngrams_index(self, path, filename):
        # Get the analyzer
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

        # Get index storage
        store = SimpleFSDirectory(File(path))

        # Get index writer
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        writer = IndexWriter(store, config)

        try:
            f = open(filename, 'r')
            print filename
            for record in f:
                record = record.split('\t')
                doc = Document()
                # Add a fields to this document: (ngram, year, match_count, volume_count)
                doc.add(Field('ngram', str(record[0]), Field.Store.YES, Field.Index.ANALYZED))
                doc.add(Field('year', str(record[1]), Field.Store.YES, Field.Index.ANALYZED))
                doc.add(Field('match_count', str(record[2]), Field.Store.YES, Field.Index.ANALYZED))
                doc.add(Field('volume_count', str(record[3]), Field.Store.YES, Field.Index.ANALYZED))
                # Add the document to the index
                writer.addDocument(doc)
            f.close()
        except Exception, e:
            print "Failed in creating document to add to the index:", e

        # Close the index writer
        writer.close()

    def index_all(self):
        # Index to the directory corresponding to the 1st letter of the uni-gram
        self.filenames  = os.listdir(self.ngram_path)

        for filename in self.filenames:
            filename = os.path.join(self.ngram_path, filename)
            path = os.path.join(self.index_path, filename[-1])
            self.build_ngrams_index(path, filename)

if __name__ == "__main__":
    ngram_path  = 'Ngrams'
    index_path  = 'NgramsIndex'

    ngram = GoogleNgram(ngram_path, index_path)
    ngram.index_all()