import numpy as np
import pickle
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
import operator
import pandas as pd
import networkx as nx
import json

# Open twitter words dict
with open('../twitter_mention_words.p','rb') as picklefile:
	twitter_words = pickle.load(picklefile)

with open('../twitter_data.p','rb') as picklefile:
	count, names, followers, followings, years, handles = pickle.load(picklefile)

# Make a dict with metadata on each artist
twitter_meta = {}
for i in range(len(handles)):
	if handles[i] in twitter_words.keys():
		twitter_meta[handles[i]] = [ names[i], followers[i], years[i] ]

# Make a new dict with all of the words joined for a given actress
twitter_words_docs = {}
for i in twitter_words:
	twitter_words_docs[i] = ' '.join(twitter_words[i]["words"])

# Stop words
stopWords = stopwords.words('english')

# Make a count frequency matrix of all terms used
from sklearn.feature_extraction.text import CountVectorizer

count_vec = CountVectorizer(stop_words = stopWords)
tfidf = count_vec.fit_transform(twitter_words_docs.values())

# Choose top features for use in model
features = count_vec.get_feature_names()
counts = tfidf.sum(axis=0).tolist()[0]

features_count_dict = {}
for i in range(len(features)):
	features_count_dict[features[i]] = counts[i]

sorted_feat_count_dict = sorted(features_count_dict.items(), key=operator.itemgetter(1), reverse=True)
vocabulary = sorted_feat_count_dict[0:5000]
vocabulary = [i[0] for i in vocabulary]

# Make a tfidf vectorizer with limited dictionary
from sklearn.feature_extraction.text import TfidfVectorizer

new_count_vec = TfidfVectorizer(stop_words = stopWords, vocabulary=vocabulary)
new_tfidf = new_count_vec.fit_transform(twitter_words_docs.values())

# Compute cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
cosine_similarities = cosine_similarity(new_tfidf)

# Create network nodes and edges
return_dict = {}	
return_dict["nodes"] = []
return_dict["edges"] = []

for i in range(len(cosine_similarities)):
	actor_name = twitter_words_docs.keys()[i]
	metadata = twitter_meta[actor_name] 
	return_dict["nodes"].append([(i+1), {
					"followers" : metadata[1],
					"name" : metadata[0] 
					} ])

threshold = 0.1

for i in range(len(cosine_similarities)):
	for j in range(i+1, len(cosine_similarities)):
		if cosine_similarities[i][j] >= threshold:
			# Create an edge
			return_dict["edges"].append([[i+1, j+1], {"weight" : cosine_similarities[i][j]}])

# Save the json file
with open('network_data.json', 'w') as outfile:
	json.dump(return_dict, outfile)


