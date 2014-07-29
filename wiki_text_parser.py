# coding: utf-8
import re
import mwparserfromhell
from bs4 import BeautifulSoup, Comment
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from textblob_aptagger import PerceptronTagger

'''
    Parse a historical article and get the event links. Parse the events articles.
'''

class WikiTextParser():

    def __init__(self, article, wiki_path):
        self._minlen_   = 2
        self.article    = article
        self.file_name  = article.replace(' ', '_') + '.txt'
        self.event_type = ['Event', 'Name', 'Disaster', 'Description', 'Incident']
        self.period_type= ['From', 'To', 'Date']
        self.wiki_path  = wiki_path

    # Get events links (columns from the table)
    def get_event_links(self, filetext):
        data_links = []
        text = re.split('== ', filetext, flags=re.IGNORECASE)
        if len(text) < self._minlen_:
            text = re.split('==', filetext, flags=re.IGNORECASE)
            text = [t.strip() for t in text]
        for para in text:
            section = re.split(' ==', para, flags=re.IGNORECASE)
            if len(section) < self._minlen_:
                section = re.split('==', para, flags=re.IGNORECASE)
            subtitle = ''
            if len(section) >= self._minlen_:
                # Get the subtitles from article
                subtitle = section[0]
                section[1] = re.split('\\|-\n\\|', section[1])
                table = False
                event_col = 0
                period_col = []
                num_cols = 0
                # Extract the columns from the table
                for fragment in section[1]:
                    if table == False:
                        fragment = filter(None, re.split('\n', fragment))
                        for line in fragment:
                            if line[0] == '!':
                                line = re.sub('!\s\w+="?\w+:\d+%;"?', '', line)
                                header = filter(None, line.split('|'))
                                for hcol in header:
                                    for etype in self.event_type:
                                        if etype in hcol:
                                            event_col = num_cols
                                    for ptype in self.period_type:
                                        if ptype in hcol:
                                            period_col.append(num_cols)
                                    num_cols += 1
                                table = True
                    else:
                        fragment = re.split('(\|\|)', fragment)
                        if len(fragment) < num_cols:
                            if len(fragment) >= self._minlen_:
                                fragment = [fragment[0]] + re.split('(\n)', fragment[-1])
                            else:
                                fragment = re.split('(\n)', fragment[-1])
                        cols = filter(None, fragment)
                        cols = [c for c in cols if c != '\n' and c != '||']
                        pattern = re.compile('\w?\[\[(.+?)\]\]')
                        event = ''
                        for c in range(len(cols)):
                            cols[c] = re.sub('({{)?', '', cols[c])
                            cols[c] = re.sub('(}})?', '', cols[c])
                        for p in pattern.findall(cols[event_col]):
                            event += p + '|'
                        event = re.split('#|\|(\|)?', event)
                        event = filter(None, event)
                        for e in range(len(event)):
                            event[e] = re.sub('\(.*\)\s?', '', event[e]).strip()
                        event = list(set(event))
                        period = ''
                        if len(period_col) == self._minlen_:
                            period += cols[period_col[0]].strip() + '-' + cols[period_col[1]].strip()
                        else:
                            period = re.sub('\|}|}|(dts|)', '', cols[period_col[0]].strip())
                            period = re.sub('\||.*\s', '', period.strip())
                        if len(event) > 0:
                            for e in event:
                                try:
                                    year = int(period.split('-')[0])
                                    if year > 1500:
                                        # Select events occurred after year 1500
                                        data_links.append((subtitle, e, period))
                                except ValueError:
                                    print 'Error in extracting time period'
        return data_links

    # Get valid words
    def is_valid_word(self, word):
        if len(word) < 3:
            return False
        for w in word:
            if w.isalpha() is False:
                return False
        return True

    # Extract words from an event article
    def extract_words(self, text):
        parsetext = mwparserfromhell.parse(text)
        for template in parsetext.filter_templates():
            temp = ''
            template = str(template)
            for t in template:
                if str(t).isalnum() == False:
                    temp += '\\'
                if str(t).isspace():
                    temp += 's'
                else:
                    temp += t
            text = re.sub(temp + '\\n*', '', text)

        text = re.sub('\[\[File\:.*\]\]|\[\[Category\:.*\]\]', ' ', text)
        text = re.sub('\*(\s)?.*|\#(\s)*|\&nbsp\;|\s?\&amp\;\s?|<.*\/>|\{\{.*\}\}', ' ', text)

        soup = BeautifulSoup(text)
        for tag in soup.findAll(True):
            tag.replaceWith('')
        for comment in soup.findAll(text=lambda text:isinstance(text, Comment)):
            comment.extract()
        text = str(soup)

        text = re.sub('\=+.*\=+', '', text)
        text = re.sub('\[\[|\|.*\]\]|\]\]', '', text)
        text = re.sub('\(.*\)|\{.*\}|\'|\-|\[|\]|\{|\}|\(|\)|\_|\*|\||\—|\=|\–', ' ', text)

        stoplist = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'do', 'did']

        # Initialize POS Tagger
        blob = TextBlob(text, pos_tagger=PerceptronTagger())
        tags = blob.tags

        filtered_text = []
        # Initialize WordNet Lemmatizer
        lemmatizer = WordNetLemmatizer()
        for tag in tags:
            if self.is_valid_word(tag[0]):
                # Keep only nouns and verbs
                if 'VB' in tag[1] or 'NN' in tag[1]:
                    word = tag[0]
                    if 'NN' in tag[1]:
                        # Lemmatize only the nouns
                        word = lemmatizer.lemmatize(tag[0])
                    # Remove stopwords
                    if word not in stoplist:
                        filtered_text.append(word)
        return ' '.join(filtered_text)

if __name__ == "__main__":
    article     = 'List of wars and anthropogenic disasters by death toll'
    # Here goes the path to Wikipedia dump
    wiki_path   = '/media/9200B2C100B2AC1B/WikiDump2014/enwiki-latest-pages-articles.xml'
    text = WikiTextParser(article, wiki_path)