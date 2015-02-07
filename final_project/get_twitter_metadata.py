
### GET TWITTER DATA OF ACTRESS OR ACTOR

import oauth2 as oauth
import json

# Oauth2 for Twitter API data
CONSUMER_KEY = "AeeP8XqdVn4JKkFe1taObuLo7"
CONSUMER_SECRET = "BAzTezf78LneLG0zVXVaIeG6bXOaCnJ12ennEXZVVNK1plCiwc"
ACCESS_KEY = "2815366039-1HLdZHBjOf3A2ZStoi2GJPZx8OsobTU5FtAQzON"
ACCESS_SECRET = "coXCsBzu7T38rU3RQYh9BLGQkQLHXtMqcal1rNYHkqk6e"

consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
client = oauth.Client(consumer, access_token)

# Load pickledata for data frame
actress_data = pd.read_pickle('current_movies_df.p')

# Reset the index to integers
actress_data.index = range(len(actress_data))

# Iterate through names in our data frame, query twitter for follower count, tweets, 
# 	and date twitter account started

# Load current twitter data
with open('twitter_data.p','rb') as picklefile:
 	list_length, names, followers_all, num_tweets_all, years_on_twi_all, user_names_all = pickle.load(picklefile)

# Initialize twitter data if needed
# list_length = 0
# names = []
# followers_all = []
# num_tweets_all = []
# years_on_twi_all = []
# user_names_all = []

row_iterator = actress_data.iterrows()
last = row_iterator.next()
row_iterator = actress_data.iterrows()

# We need to keep track of the queries we have already made bc of rate limiting
for i in range(list_length):
	last = row_iterator.next()

# Make queries to twitter API
counter = 0
for name, row in row_iterator:
	counter += 1

	twi_url_request = get_twi_search_url_from_name(str(row['Names']))
	twi_response, twi_data = client.request(twi_url_request)

	# Check rate limit
	queries_left = int(twi_response['x-rate-limit-remaining'])
	if queries_left > 1:
		followers, num_tweets, years_on_twi, user_name = twi_factors_from_search_response(twi_data)
		followers_all.append(followers)
		num_tweets_all.append(num_tweets)
		years_on_twi_all.append(years_on_twi)
		user_names_all.append(user_name)
		names.append(str(row['Names']))
	else: 
		# Write what we have to the file
		with open('twitter_data.p','wb') as picklefile:
			# What is the current length of the lists
			list_length = len(followers_all)
			print (list_length, names, followers_all, num_tweets_all, years_on_twi_all, user_names_all)
 			pickle.dump((list_length, names, followers_all, num_tweets_all, years_on_twi_all, user_names_all), picklefile)

 		break

	# Next row
	last = row

# Write to file
with open('twitter_data.p','wb') as picklefile:
	# What is the current length of the lists
	list_length = len(followers_all)
 	pickle.dump((list_length, names, followers_all, num_tweets_all, years_on_twi_all, user_names_all), picklefile)

# Open twitter data file and append to main dataframe
with open('current_movies_df.p','rb') as picklefile:
 	actress_data = pickle.load(picklefile)

with open('twitter_data.p','rb') as picklefile:
	list_length, names, followers_all, num_tweets_all, years_on_twi_all = pickle.load(picklefile)

actress_data['NumFollowers'] = followers_all
actress_data['NumTweets'] = num_tweets_all
actress_data['YrsOnTwitter'] = years_on_twi_all
actress_data['NumTweetsPerYr'] = actress_data['NumTweets'] / actress_data['YrsOnTwitter']

# Write to file
with open('df_w_twitter.p','wb') as picklefile:
 	pickle.dump(actress_data, picklefile)

