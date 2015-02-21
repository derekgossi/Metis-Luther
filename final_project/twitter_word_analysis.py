import numpy as np
import pickle
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
import operator
import pandas as pd

# Open twitter words dict
with open('twitter_mention_words.p','rb') as picklefile:
	twitter_words = pickle.load(picklefile)

with open('twitter_mention_words_nan.p','rb') as picklefile:
	twitter_words_nan = pickle.load(picklefile)

for i in twitter_words_nan:
	twitter_words[i] = twitter_words_nan[i]

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

# Choose top 100 features for use in model
features = count_vec.get_feature_names()
counts = tfidf.sum(axis=0).tolist()[0]

features_count_dict = {}
for i in range(len(features)):
	features_count_dict[features[i]] = counts[i]

sorted_feat_count_dict = sorted(features_count_dict.items(), key=operator.itemgetter(1), reverse=True)
vocabulary = sorted_feat_count_dict[0:70]
vocabulary = [i[0] for i in vocabulary]

# Make a tfidf vectorizer with limited dictionary
from sklearn.feature_extraction.text import TfidfVectorizer

new_count_vec = TfidfVectorizer(stop_words = stopWords, vocabulary=vocabulary)
new_tfidf = new_count_vec.fit_transform(twitter_words_docs.values())

# Compute cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
cosine_similarities = cosine_similarity(new_tfidf)

# MDS analysis
from sklearn.manifold import MDS

mdser = MDS()
mdsft = mdser.fit_transform(new_tfidf)

#colors = [0,0,0,1] + [0]*int(len(mdsft) - 4)

plt.scatter(mdsft[:, 0], mdsft[:, 1])
plt.show()

# Make a new dict with mds combined with keys
from sklearn.metrics import pairwise_distances
ed = pairwise_distances(new_tfidf, metric='cosine')

ed_bey = [ed[i][3] for i in range(len(ed))]

return_dict = {}
for num, key in enumerate(twitter_words_docs.keys()):
	return_dict[key] = ed_bey[num]

# Append to twitter words dict by screen name
for i in return_dict:
	twitter_words[i]["dist"] = return_dict[i]

# Open dataframe for analysis
actress_data = pd.read_pickle('df_w_twitter.p')

names = [twitter_words[i]["name"] for i in twitter_words]
dist = [twitter_words[i]["dist"] for i in twitter_words]

# Update dataframe with distances
for i in range(len(names)):
	actress_data.ix[actress_data["Names"]==names[i], "CelebDist"] = dist[i]

# Pickle dataframe
with open('df_w_celeb_dist_w_non_twitter.p','wb') as picklefile:
	pickle.dump(actress_data, picklefile)


