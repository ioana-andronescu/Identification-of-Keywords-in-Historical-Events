------------------------------------------------------------------------------------
																				   
Identification of Keywords in Historical Events								   	   
																				   
	Ioana Andronescu															   
------------------------------------------------------------------------------------

1. Source Files
-> ngram_indexer.py
	- used to index all google ngrams by first letter of the ngram
-> tfidf.py
	- computes tf-idf for a word in a document
-> series.py
	- computes time series for a word
	- smoothify time series within a given window size
-> wiki_text_parser.py
	- extracts event columns from a Wikipedia article
	- parses an article and keeps nouns and verbs
-> wiki_words_indexer.py
	- indexes time series+words from historical events (wars) described in Wikipedia articles
-> double_change_peak.py
	- finds peaks using the double change method
-> window_peak.py
	- finds peaks using the sliding window methods (three functions)
-> level_peak.py
	- finds peaks using the level difference methods (two functions)
-> divergence.py
	- computes Kullback-Leibler divergence between the original distribution of the time series of a certain word
	and the approximated distribution after applying the peak detection algorithms
-> historical_relevance.py
	- gets the keywords for each of the war events
	- computes the divergence for every word that appears in a Wikipedia article describing an event
	- gets the common words discovered by all six methods
	- gets the unique words that describe the event
-> plotter.py
	- plots peaks or relevant words
-> test.py
	- tests results for given events

2. Data
-> NgramsIndex
	- indexed Google Books Ngrams
-> wiki
	- txt files containing words from Wikipedia articles
-> WikiIndex
	- indexed words+time series for certain events referring to "war"
-> keywords
	- directories for each historical event: keywords identified using each of the 6 methods,
	divergence, common words (methods), uncommon words (unique words that don't appear in other articles)
