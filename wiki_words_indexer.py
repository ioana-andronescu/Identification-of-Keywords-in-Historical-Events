# coding: utf-8
import xml.etree.cElementTree as cET
import sys, os, re
import wikipedia
import lucene
from org.apache.lucene.store import *
from org.apache.lucene.analysis.standard import *
from org.apache.lucene.util import *
from org.apache.lucene.index import *
from org.apache.lucene.document import *
from org.apache.lucene.queryparser.classic import *
from org.apache.lucene.search import *
from java.io import *
from wiki_text_parser import WikiTextParser
from text.blob import TextBlob
from tfidf import TfIdf
from series import TimeSeries

'''
    Get words (nouns + verbs) from Wikipedia articles.
'''

class WikiPage():

    def __init__(self, article, wiki_path):
        self.article        = article
        self.wiki_path      = wiki_path
        self.index_words    = os.path.join('data', 'WordsIndex')
        self.index_wiki     = os.path.join('data', 'WikiIndex')
        self.file_name      = article.replace(' ', '_') + '.csv'
        self.wiki_parser    = WikiTextParser(self.article, self.wiki_path)

    # Get page by title
    def get_page(self, link):
        # Get an iterable
        context = cET.iterparse(self.wiki_path, events=('start', 'end'))

        # Get the root element
        event, root = context.next()
        ns = root.tag.split('}')[0] + '}'

        found = False
        title = ''
        cnt = 0
        for event, elem in context:
            if event == 'end' and elem.tag == (ns + 'title'):
                title = elem.text
                root.clear()
            if event == 'end' and elem.tag == (ns + 'text'):
                if title == link:
                    found = True
                    return elem.text
                cnt += 1
                root.clear()
        if found == False:
            return None

    # Write content of an article to file given the title
    def save_titles(self, path, titles, data_link):
        for title in titles:
            try:
                content = wikipedia.page(title, redirect=True).content
            except wikipedia.exceptions.DisambiguationError as e:
                count   = 0
                titles  = []
                for option in e.options:
                    if title in option and title != option and count < 2:
                        titles.append(option)
                        count += 1
                self.save_titles(path, titles, data_link)
                break
            text = self.wiki_parser.extract_words(content)
            filename    = title.replace(' ', '_') + '.txt'
            file_path   = os.path.join(path, filename)
            f = open(file_path, 'w')
            f.write(data_link[1] + '\n' + data_link[2] + '\n')
            f.write(text)
            f.close()

    # Write all war events to file
    def print_wiki_titles(self, subtitle):
        path = os.path.join('data', self.file_name)
        data_links = self.wiki_parser.get_event_links(self.get_page(self.article))
        f = open(path, 'w')
        for data_link in data_links:
            line = data_link[0] + ',' + data_link[1] + ',' + data_link[2] + '\n'
            f.write(line)
        f.close()

        path = os.path.join('data', 'wiki')

        for data_link in data_links:
            if data_link[0] == subtitle:
                titles = wikipedia.search(data_link[1], results=1)
                if len(titles) < 1:
                    continue
                self.save_titles(path, titles, data_link)

    # Compute tf-idf for each war article - not used
    def process_texts(self):
        relevant_words = []
        path = os.path.join('data', 'wiki')
        file_names = os.listdir(path)
        documents = []
        for file_name in file_names:
            file_path = os.path.join(path, file_name)
            f = open(file_path)
            documents.append((file_name, TextBlob(str.decode(f.read(), 'UTF-8', 'ignore'))))
            f.close()

        tfidf = TfIdf(documents)
        for file_name, document in documents:
            print file_name
            scores = {word: tfidf.compute_tfidf(word, document) for word in document.words}
            selected_scores = {}
            for word in scores:
                similars = sorted(self.get_similar(scores.keys(), word))
                selected_scores[similars[-1]] = scores[word]
            sorted_words = sorted(selected_scores.items(), key=lambda x: x[1], reverse=True)
            for word, score in sorted_words[:10]:
                if word not in relevant_words:
                    relevant_words.append(word)
        return set(relevant_words)

    # Get words that are similar (case insensitive) - not used
    def get_similar(self, words, word):
        similars = []
        for w in words:
            if w.lower() == word.lower():
                similars.append(w)
        return similars

    # Index words with highest tf-idf - not used
    def build_words_index(self):
        relevant_words = self.process_texts()

        # Initialize lucene and JVM
        lucene.initVM()

        # Get the analyzer
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

        # Get index storage
        store = SimpleFSDirectory(File(self.index_words))

        # Get index writer
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        writer = IndexWriter(store, config)

        try:
            for word in relevant_words:
                time_series = TimeSeries(word).get_series()
                series_str  = ''
                for t in time_series:
                    series_str += str(t) + ':' + str(time_series[t]) + '\t'
                doc = Document()
                # Add a fields to this document
                doc.add(Field('word', word, Field.Store.YES, Field.Index.ANALYZED))
                doc.add(Field('series', series_str, Field.Store.YES, Field.Index.ANALYZED))
                # Add the document to the index
                writer.addDocument(doc)
        except Exception, e:
            print "Failed in creating document to add to the index:", e
        writer.close()

    # Index a war article
    def build_wiki_index(self, file_name):
        # Initialize lucene and JVM
        lucene.initVM()

        # Get the analyzer
        analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

        # Get index storage
        path = os.path.join(self.index_wiki, file_name[:-4])
        if not os.path.exists(path):
            os.makedirs(path)
        store = SimpleFSDirectory(File(path))

        # Get index writer
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        writer = IndexWriter(store, config)

        try:
            file_path = os.path.join(os.path.join('data', 'wiki'), file_name)
            print file_path
            print path
            f = open(file_path, 'r')
            count = 0
            for line in f:
                if count == 0:
                    event = line
                elif count == 1:
                    period = line
                else:
                    text = list(set(line.split()))
                count += 1
            print event, period
            f.close()
            count = 0
            for word in text:
                time_series = TimeSeries(word, 0).get_series()
                if time_series != None:
                    series_str  = ''
                    for t in time_series:
                        series_str += str(t) + ':' + str(time_series[t]) + '\t'
                    doc = Document()
                    # Add fields to this document
                    doc.add(Field('event', event, Field.Store.YES, Field.Index.ANALYZED))
                    doc.add(Field('period', period, Field.Store.YES, Field.Index.ANALYZED))
                    doc.add(Field('word', word, Field.Store.YES, Field.Index.ANALYZED))
                    doc.add(Field('series', series_str, Field.Store.YES, Field.Index.ANALYZED))
                    # Add the document to the index
                    writer.addDocument(doc)
                    count += 1
        except Exception, e:
            print "Failed in creating document to add to the index:", e
        writer.close()

    # Index all war articles
    def index_articles(self):
        path = os.path.join('data', 'wiki')
        file_names = os.listdir(path)
        for file_name in file_names:
            self.build_wiki_index(file_name)

if __name__ == "__main__":
    wiki_path   = '/media/9200B2C100B2AC1B/WikiDump2014/enwiki-latest-pages-articles.xml'
    wiki = WikiPage(sys.argv[1], wiki_path)
    wiki.print_wiki_titles('Wars and armed conflicts')
    wiki.index_articles()