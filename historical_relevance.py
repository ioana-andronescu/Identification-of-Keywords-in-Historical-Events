# coding: utf-8
import os, sys
import lucene
from org.apache.lucene.store import *
from org.apache.lucene.analysis.standard import *
from org.apache.lucene.util import *
from org.apache.lucene.index import *
from org.apache.lucene.document import *
from org.apache.lucene.queryparser.classic import *
from org.apache.lucene.search import *
from java.io import *
from double_change_peak import DoubleChangePeakDetector
from level_peak import LevelPeakDetector
from series import TimeSeries
from window_peak import WindowPeakDetector
from divergence import KullbackLeibler
from plotter import Plotter

'''
    Historical Relevance of an event.
'''

class HistoricalRelevance():

    def __init__(self):
        self.max_range      = 509
        self.year_range     = [1500, 2008]
        self.num_methods    = 6

    # Compute relevance (0-10) for peaks
    def compute_relevance(self, peaks):
        if len(peaks) == 0:
            return [0 for _ in range(self.max_range)]
        if type(peaks) is dict:
            max_peak = max(peaks.values())
        elif type(peaks) is list:
            max_peak = max(peaks)
        if max_peak == 0:
            return [0 for _ in range(self.max_range)]

        counts = []
        for t in range(self.max_range):
            if type(peaks) is dict:
                if t in peaks:
                    count = int(10 * peaks[t] / max_peak)
                else:
                    count = 0
            else:
                count = int(10 * peaks[t] / max_peak)
            counts.append(count)
        return counts

    # Plot resulted keywords
    def plot_keywords(self, event, words, period):
        time_series = []
        for i in range(len(words)):
            original_series = TimeSeries(words[i]).get_series()
            original_series = original_series.get_modified_series(original_series)
            series = original_series.smoothify_series(original_series, 2)
            time_series.append(series)

        x0 = [i + self.year_range[0] for i in range(self.max_range)]
        plotter = Plotter(x0, [], period)
        plotter.plot_keywords(event, words, time_series)

    # Plot historical relevance for a word
    def plot_historical_relevance(self, word, period, method, smooth=None):
        time_series = TimeSeries(word)
        series = time_series.get_series()
        original_series = time_series.get_modified_series(series)
        if smooth != None:
            series = time_series.smoothify_series(original_series, smooth)
        else:
            series = original_series

        x0 = [i + self.year_range[0] for i in range(self.max_range)]
        y0 = self.compute_relevance(original_series)

        if 'level' in method:
            level_peak = LevelPeakDetector(series)
            if method == 'level 1':
                y = self.compute_relevance(level_peak.get_levels(1))
            else:
                y = self.compute_relevance(level_peak.get_levels(2))
        elif 'window' in method:
            window_peak = WindowPeakDetector(series)
            if method == 'window 1':
                y = self.compute_relevance(window_peak.compute_peaks(1))
            elif method == 'window 2':
                y = self.compute_relevance(window_peak.compute_peaks(2))
            else:
                y = self.compute_relevance(window_peak.compute_peaks(3))
        elif 'double' in method:
            double_peak = DoubleChangePeakDetector(series)
            y = double_peak.compute_relevance(0.1)

        plotter = Plotter(x0, series, period)
        plotter.plot_peaks(word, y, method + ' function')

    # Plot results for 6 methods of peak detection
    def plot_all_methods(self, word, period, smooth=None):
        time_series = TimeSeries(word)
        series = time_series.get_series()
        original_series = time_series.get_modified_series(series)
        if smooth != None:
            series = time_series.smoothify_series(original_series, smooth)
        else:
            series = original_series

        x0 = [i + self.year_range[0] for i in range(self.max_range)]
        y0 = self.compute_relevance(original_series)

        y = []

        level_peak = LevelPeakDetector(series)
        y.append(self.compute_relevance(level_peak.get_levels(1)))
        y.append(self.compute_relevance(level_peak.get_levels(2)))

        window_peak = WindowPeakDetector(series)
        y.append(self.compute_relevance(window_peak.compute_peaks(1)))
        y.append(self.compute_relevance(window_peak.compute_peaks(2)))
        y.append(self.compute_relevance(window_peak.compute_peaks(3)))

        double_peak = DoubleChangePeakDetector(series)
        y.append(double_peak.compute_relevance(0.1))

        plotter = Plotter(x0, series, period)
        plotter.plot_multiple_peaks(word, y, period)

    # Detect if the word was relevant in the period of the historical event
    def is_relevant_in_period(self, y, period):
        current_year = 2014
        recent_year = 1980
        for t in range(self.max_range):
            year = t + self.year_range[0]
            if y[t] > 0:
                if period[1] >= recent_year:
                    magic_year_max = 8
                    magic_year_min = 12
                    if period[0] - magic_year_min < year < period[1] + magic_year_max:
                        return y[t]
                else:
                    magic_year = 2
                    if period[0] < year < period[1] + magic_year:
                        return y[t]
        return 0

    # Get historical relevance for each method for a given word and time series
    def get_historical_relevance(self, word, word_info):
        initial_period = word_info[0].split('-')
        period = []
        for p in initial_period:
            if 'Present' in initial_period:
                period.append(2014)
            else:
                period.append(int(p))
        series = word_info[1]
        time_series = TimeSeries(word)
        series = time_series.get_modified_series(series)
        smoothing_series = time_series.smoothify_series(series, 2)

        relevance = []

        level_peak = LevelPeakDetector(smoothing_series)
        relevance.append(self.is_relevant_in_period(self.compute_relevance(level_peak.get_levels(1)), period))
        relevance.append(self.is_relevant_in_period(self.compute_relevance(level_peak.get_levels(2)), period))

        window_peak = WindowPeakDetector(series)
        relevance.append(self.is_relevant_in_period(self.compute_relevance(window_peak.compute_peaks(1)), period))
        relevance.append(self.is_relevant_in_period(self.compute_relevance(window_peak.compute_peaks(2)), period))
        relevance.append(self.is_relevant_in_period(self.compute_relevance(window_peak.compute_peaks(3)), period))

        double_peak = DoubleChangePeakDetector(smoothing_series)
        relevance.append(self.is_relevant_in_period(double_peak.compute_relevance(0.1), period))

        return relevance

    # Compute Kullback-Leibler divergence between original distribution and resulted distribution
    def get_divergence(self, word, series):
        divergence = []

        time_series = TimeSeries(word)
        series = time_series.get_modified_series(series)
        y = self.compute_relevance(series)
        smoothing_series = time_series.smoothify_series(series, 1)
        ys  = self.compute_relevance(smoothing_series)

        level_peak = LevelPeakDetector(series)
        y_level_1 = self.compute_relevance(level_peak.get_levels(1))
        divergence.append(KullbackLeibler(y, y_level_1).compute_divergence())
        y_level_2 = self.compute_relevance(level_peak.get_levels(2))
        divergence.append(KullbackLeibler(y, y_level_2).compute_divergence())

        window_peak = WindowPeakDetector(series)
        y_window_1 = self.compute_relevance(window_peak.compute_peaks(1))
        divergence.append(KullbackLeibler(y, y_window_1).compute_divergence())
        y_window_2 = self.compute_relevance(window_peak.compute_peaks(2))
        divergence.append(KullbackLeibler(y, y_window_2).compute_divergence())
        y_window_3 = self.compute_relevance(window_peak.compute_peaks(3))
        divergence.append(KullbackLeibler(y, y_window_3).compute_divergence())

        double_peak = DoubleChangePeakDetector(smoothing_series)
        y_double = double_peak.compute_relevance(0.1)
        divergence.append(KullbackLeibler(ys, y_double).compute_divergence())

        return divergence

    # Query period+time series for an event
    def query_wiki_article_info(self, event_dir):
        index_dir = os.path.join('data', 'WikiIndex')
        index_dir = os.path.join(index_dir, event_dir)
        event = event_dir.replace('_', ' ')

        article_info = {}

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
        query = QueryParser(Version.LUCENE_CURRENT, 'event', analyzer).parse(event)

        results = searcher.search(query, 10000)

        for hit in results.scoreDocs:
            doc = searcher.doc(hit.doc)
            word = doc.get('word')
            period = doc.get('period').rstrip()
            series = doc.get('series').split('\t')
            time_series = {}
            for string in series:
                string = string.split(':')
                if len(string) > 1:
                    time_series[int(string[0])] = float(string[1])
            article_info[word] = (period, time_series)
        reader.close()

        return article_info

    # Write word+relevance in a file corresponding to the event
    def write_to_file(self, summary_dir, relevant_words, filename):
        summary_dir = os.path.join(summary_dir, filename)
        f = open(summary_dir, 'w')
        for word in sorted(relevant_words, key=relevant_words.get, reverse=True):
            f.write(word + ',' + str(relevant_words[word]) + '\n')
        f.close()

    # Write the detected words that are common for all 6 methods
    def write_common_keywords(self, relevant_words, file_dir):
        file_dir = os.path.join(file_dir, 'keywords common.csv')
        f = open(file_dir, 'w')

        common_keywords = {}
        relevance = {}
        for r in range(self.num_methods):
            for word in relevant_words[r + 1]:
                if word not in common_keywords:
                    common_keywords[word] = 1
                    relevance[word] = [relevant_words[r + 1][word]]
                else:
                    common_keywords[word] += 1
                    relevance[word].append(relevant_words[r + 1][word])

        for word in relevance:
            avg_relevance = sum(relevance[word]) / self.num_methods
            relevance[word] = int(avg_relevance)

        magic_number = self.num_methods - 1
        for word in sorted(relevance, key=relevance.get, reverse=True):
            if common_keywords[word] >= magic_number:
                f.write(word + ',' + str(relevance[word]) + '\n')
        f.close()

    # Detect all words that are unique for an event (can't be found in other articles)
    def write_uncommon_words(self, relevant_words, file_dir):
        summary_dir = os.path.join(os.path.join('data', 'keywords'), 'all common.csv')
        file_dir = os.path.join(file_dir, 'keywords uncommon.csv')

        all_common = []
        f = open(summary_dir, 'r')
        for line in f:
            all_common.append(line.rstrip())
        f.close()

        uncommon_keywords = {}
        relevance = {}
        for r in range(self.num_methods):
            for word in relevant_words[r + 1]:
                if word not in all_common:
                    if word not in uncommon_keywords:
                        uncommon_keywords[word] = 1
                        relevance[word] = [relevant_words[r + 1][word]]
                    else:
                        uncommon_keywords[word] += 1
                        relevance[word].append(relevant_words[r + 1][word])

        for word in relevance:
            avg_relevance = sum(relevance[word]) / self.num_methods
            relevance[word] = int(avg_relevance)

        magic_number = self.num_methods - 1
        f = open(file_dir, 'w')
        for word in sorted(relevance, key=relevance.get, reverse=True):
            if uncommon_keywords[word] >= magic_number:
                f.write(word + ',' + str(relevance[word]) + '\n')
        f.close()

    # Get words that can be found in more than one article
    def get_all_common_words(self):
        all_common = {}
        index_dir = os.listdir(os.path.join('data', 'WikiIndex'))
        for event_dir in index_dir:
            relevance = self.summarize_methods(event_dir)
            for r in range(self.num_methods):
                for word in relevance[r + 1]:
                    if word not in all_common:
                        all_common[word] = 1
                    else:
                        all_common[word] += 1

        summary_dir = os.path.join(os.path.join('data', 'keywords'), 'all common.csv')
        magic_number = self.num_methods
        f = open(summary_dir, 'w')
        for word in sorted(all_common, key=all_common.get, reverse=True):
            if all_common[word] > magic_number:
                f.write(word + '\n')
        f.close()

    # Compute divergence for all words in an article
    def get_total_divergence(self, event_dir, relevant_words):
        article_info = self.query_wiki_article_info(event_dir)

        total_divergence = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        counts = [0 for _ in range(self.num_methods)]
        for r in range(self.num_methods):
            for word in relevant_words[r + 1]:
                total_divergence[r + 1] += self.get_divergence(word, article_info[word][1])[r]
                counts[r] += 1
        for r in range(self.num_methods):
            if counts[r] > 0:
                total_divergence[r + 1] = total_divergence[r + 1] / counts[r]
            else:
                total_divergence[r + 1] = float(sys.maxint)

        return total_divergence

    # Get the words from all articles that define 'war', in decreasing order of the historical relevance
    def get_war_keywords(self):
        keywords_dir = os.path.join('data', 'keywords')
        keywords_art = os.listdir(keywords_dir)
        keywords = {}
        for event_dir in keywords_art:
            path = os.path.join(keywords_dir, event_dir)
            if os.path.isdir(path):
                file_path = os.path.join(path, 'keywords uncommon.csv')
                f = open(file_path, 'r')
                for line in f:
                    word = line.split(',')[0]
                    relevance = line.split(',')[1].rstrip()
                    keywords[word] = relevance
                f.close()
        keywords_dir = os.path.join(keywords_dir, 'war.csv')
        f = open(keywords_dir, 'w')
        for word in sorted(keywords, key=keywords.get, reverse=True):
            f.write(word + ',' + keywords[word] + '\n')
        f.close()

    # Get the divergence for each method
    def get_best_method(self):
        keywords_dir = os.path.join('data', 'keywords')
        keywords_art = os.listdir(keywords_dir)
        methods = [0.0 for _ in range(self.num_methods)]
        for event_dir in keywords_art:
            file_path = os.path.join(keywords_dir, event_dir)
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, 'divergence.csv')
                f = open(file_path, 'r')
                count = 0
                for line in f:
                    methods[count] += float(line.split(', ')[1])
                    count += 1
                f.close()

        keywords_dir = os.path.join(keywords_dir, 'general divergence.csv')
        f = open(keywords_dir, 'w')
        for i in range(self.num_methods):
            methods[i] /= len(keywords_art)
            if i <= 1:
                method_name = 'level LD '
                if i == 0:
                    method_name += '1'
                else:
                    method_name += '2'
            elif i > 1 and i <= 4:
                method_name = 'sliding window SW '
                if i == 2:
                    method_name += '1'
                elif i == 3:
                    method_name += '2'
                else:
                    method_name += '3'
            else:
                method_name = 'double change'
            f.write(method_name + ', ' + '{0:.4}'.format(methods[i]) + '\n')
        f.close()

    # Get words that are relevant and sort them in decreasing order by relevance
    def summarize_methods(self, event_dir):
        article_info = self.query_wiki_article_info(event_dir)

        relevant_words = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}

        for word in article_info:
            relevance = self.get_historical_relevance(word, article_info[word])
            for r in range(self.num_methods):
                if relevance[r] > 0:
                    relevant_words[r + 1][word] = relevance[r]

        unique_relevant_words = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
        for r in range(self.num_methods):
            for word in relevant_words[r + 1]:
                if word != word.lower():
                    if word in relevant_words[r + 1] and word.lower() in relevant_words[r + 1]:
                        unique_relevant_words[r + 1][word.lower()] = relevant_words[r + 1][word.lower()]
                    else:
                        unique_relevant_words[r + 1][word] = relevant_words[r + 1][word]
                else:
                    unique_relevant_words[r + 1][word] = relevant_words[r + 1][word]

        sorted_relevant_words = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
        for r in range(self.num_methods):
            for word in sorted(unique_relevant_words[r + 1], key=unique_relevant_words[r + 1].get, reverse=True):
                sorted_relevant_words[r + 1][word] = unique_relevant_words[r + 1][word]

        return sorted_relevant_words

    # Get keywords for an event for each method
    def summarize_single_article(self, summary_dir, event_dir):
        relevance_words = self.summarize_methods(event_dir)
        total_divergence = self.get_total_divergence(event_dir, relevance_words)

        event = event_dir.replace('_', ' ')
        summary_dir = os.path.join(summary_dir, event)
        if not os.path.exists(summary_dir):
            os.makedirs(summary_dir)

        methods = ['level LD1', 'level LD2', 'window SW1', 'window SW2', 'window SW3', 'double']
        f = open(os.path.join(summary_dir, 'divergence.csv'), 'w')
        for r in range(self.num_methods):
            filename = 'keywords ' + methods[r] + '.csv'
            self.write_to_file(summary_dir, relevance_words[r + 1], filename)
            divergence = "{0:.4}".format(total_divergence[r + 1])
            f.write(methods[r] + ', ' + str(divergence) + '\n')
        f.close()

        self.write_common_keywords(relevance_words, summary_dir)
        self.write_uncommon_words(relevance_words, summary_dir)

    # Get keywords for all war events
    def summarize(self, event=None):
        index_dir = os.listdir(os.path.join('data', 'WikiIndex'))
        summary_dir = os.path.join('data', 'keywords')
        if event != None:
            for directory in index_dir:
                if event == directory.replace('_', ' '):
                    event_dir = directory
            self.summarize_single_article(summary_dir, event_dir)
        else:
            for event_dir in index_dir:
                self.summarize_single_article(summary_dir, event_dir)

if __name__ == "__main__":
    relevance = HistoricalRelevance()
    relevance.get_all_common_words()
    #relevance.summarize('American Civil War')
    relevance.summarize()
    relevance.get_best_method()
    relevance.get_war_keywords()