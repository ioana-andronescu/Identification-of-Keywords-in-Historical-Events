import os
import lucene
from org.apache.lucene.store import *
from org.apache.lucene.analysis.standard import *
from org.apache.lucene.util import *
from org.apache.lucene.index import *
from org.apache.lucene.document import *
from org.apache.lucene.queryparser.classic import *
from org.apache.lucene.search import *
from java.io import *

import matplotlib.pyplot as plt
import pylab

'''
    Compute time series from the Google Books Ngram Corpus given a word.
'''

class TimeSeries():

    def __init__(self, word):
        self.word               = word
        self.total_counts       = {}
        self.counts_filename    = os.path.join('data', 'googlebooks-eng-all-totalcounts-20120701-optim.txt')
        self.min_year           = 1505
        self.time_diff          = 504
        self.max_range          = 509
        self.year_range         = [1500, 2008]
        self.get_total_counts()

    # Write to file only year+total_counts
    def process_counts_filename(self):
        filename = os.path.join('data', 'googlebooks-eng-all-totalcounts-20120701.txt')
        fr = open(filename, 'r')
        fw = open(self.counts_filename, 'w')
        for line in fr:
            for row in line.split('\t'):
                row = row.lstrip()
                if row:
                    row = row.split(',')
                    fw.write(row[0] + ',' + row[1] + '\t')
        fr.close()
        fw.close()

    # Get total counts for each year
    def get_total_counts(self):
        f = open(self.counts_filename, 'r')
        for line in f:
            for row in line.split('\t'):
                row = row.lstrip()
                if row:
                    row = map(int, row.split(','))
                    self.total_counts[row[0]] = row[1]
        f.close()

    # Query NgramsIndex by first letter of the given word
    def get_query_results(self):
        query_result = {}
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        index_dir = os.path.join('data', 'NgramsIndex')
        directory = str(self.word[0]).lower()
        if directory not in alphabet:
            return None

        index_dir = os.path.join(index_dir, directory)
        # Initialize lucene and JVM
        lucene.initVM()

        # Get index storage
        store = SimpleFSDirectory(File(index_dir))

        # Get the analyzer
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

        # Get index reader
        reader = IndexReader.open(store)
        searcher = IndexSearcher(reader)

        # Make a query for the specified string
        query = QueryParser(Version.LUCENE_CURRENT, 'ngram', analyzer).parse(self.word)

        num_docs = 1000000
        results = searcher.search(query, num_docs)

        for hit in results.scoreDocs:
            doc = searcher.doc(hit.doc)
            year = int(doc.get('year'))
            match_count = float(doc.get('match_count'))
            if year not in query_result:
                query_result[year] = []
            query_result[year].append(match_count)
        reader.close()

        # Get the maximum match count for each year
        result = {}
        for q in query_result:
            result[q] = max(query_result[q])
        return result

    # Get time series for the word
    def get_series(self):
        series = self.get_query_results()
        if series is None:
            return None
        for year in series:
            series[year] /= float(self.total_counts[year])
        return series

    # Get smoothing series for a given window size - not used
    def get_smooth_time_series(self, smoothing_window):
        sparse_series = self.get_series()
        series_size = len(sparse_series)
        series = [0 for _ in range(self.time_diff)]
        for year in sparse_series:
            series[year - self.min_year] = sparse_series[year]
        smoothing_series = {t: 0.0 for t in range(self.time_diff)}
        for t in xrange(smoothing_window, series_size - smoothing_window):
            for k in xrange(-smoothing_window, smoothing_window + 1):
                smoothing_series[t] += float(series[t + k]) / (2 * smoothing_window + 1)
        return smoothing_series

    # Get time series as an array from 0 to 509
    def get_modified_series(self, time_series):
        series = [0.0 for _ in range(self.max_range)]
        for year in time_series:
            series[year - self.year_range[0]] = time_series[year]
        return series

    # Get smoothing series
    def smoothify_series(self, series, smoothing_window):
        series_size = len(series)
        smoothing_series = [0.0 for _ in range(series_size)]
        for t in xrange(smoothing_window, series_size - smoothing_window):
            for k in xrange(-smoothing_window, smoothing_window + 1):
                smoothing_series[t] += float(series[t + k]) / (2 * smoothing_window + 1)
        if smoothing_window > 0:
            last = series_size - smoothing_window
            for t in xrange(last, series_size):
                smoothing_series[t] = series[t]
        return smoothing_series

if __name__ == "__main__":
    time_series = TimeSeries('slavery')
    time_series.process_counts_filename()
    series = time_series.get_series()