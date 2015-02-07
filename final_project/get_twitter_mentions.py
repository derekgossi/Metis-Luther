
### GET SAMPLE OF TWITTER MENTIONS FOR EACH ACTRESS AND ACTOR IN DATASET 

import oauth2 as oauth
import json
from stemming.porter2 import stem
from random import shuffle
import time

# Oauth2 for Twitter API data
CONSUMER_KEY = "AeeP8XqdVn4JKkFe1taObuLo7"
CONSUMER_SECRET = "BAzTezf78LneLG0zVXVaIeG6bXOaCnJ12ennEXZVVNK1plCiwc"
ACCESS_KEY = "2815366039-1HLdZHBjOf3A2ZStoi2GJPZx8OsobTU5FtAQzON"
ACCESS_SECRET = "coXCsBzu7T38rU3RQYh9BLGQkQLHXtMqcal1rNYHkqk6e"

consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
client = oauth.Client(consumer, access_token)

# Open twitter words dict
with open('twitter_mention_words.p','rb') as picklefile:
	twitter_dict = pickle.load(picklefile)

# Initialize counter
counter = 0

# Attempt to query Twitter API 100 times
while counter < 100:
	# Increment counter
	counter += 1

	print "Iteration " + str(counter) + " of 100"

	# Get rate limit
	query = "https://api.twitter.com/1.1/search/tweets.json?q=taylorswift13"
	twi_response, twi_data = client.request(query)
	rate_limit = int(twi_response['x-rate-limit-remaining'])

	if(rate_limit > 175):
		# Get shuffled keys
		keys_to_shuffle = twitter_dict.keys()
		shuffle(keys_to_shuffle)
		shuffled_keys = keys_to_shuffle[0:170]

		# Get results for each key
		for screen_name in shuffled_keys:
			# Query twitter
			query = "https://api.twitter.com/1.1/search/tweets.json?q=" + screen_name + "&count=100"
			twi_response, twi_data = client.request(query)
			twi_data_json = json.loads(twi_data)

			# Strip, stem, and put all words into the dict
			for i in range(len(twi_data_json["statuses"])):
				for j in range(len(twi_data_json["statuses"][i]["text"].split())):
					word = twi_data_json["statuses"][i]["text"].split()[j]
					word_stripped = re.sub('[^A-Za-z0-9]+', '', word)
					twitter_dict[screen_name]["words"].append(stem(word_stripped))

		# Write to the file
		with open('twitter_mention_words_nan.p','wb') as picklefile:
			pickle.dump(twitter_dict,picklefile)

		# Print results
		total_words = 0
		for i in twitter_dict:
			total_words += len(twitter_dict[i]["words"])
		print total_words / float(len(twitter_dict))

	else:
		time.sleep(300)

