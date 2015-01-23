
import urllib2
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime
import pickle


### FUNCTION DEFINITIONS

# Checks if an object is an int
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

# Finds and returns the current beautiful soup tr a soup string is in
def find_current_tr(soup, inside_stuff):
	current_level = inside_stuff
	if current_level is not None:
		if current_level.name == 'tr':
			return current_level
		else:
			while current_level.name != 'body':
				current_level = current_level.findParent()
				if current_level.name == 'tr':
					return current_level

# Given a beautiful soup tr, returns td
def get_td_list_from_tr(soup, tr):
	assert tr is not None, 'Not given anything'
	assert tr.name == 'tr', 'Not given a tr'

	# Find all the cells
	cells = tr.findChildren('td')
	return cells

# Given a tr, finds next tr if it exists
def find_next_row(soup, tr):
	assert tr is not None, 'Not given anything'
	assert tr.name == 'tr', 'Not given a tr'

	next_row = tr.findNextSibling()

	# Check if it exists and is a row
	if next_row is not None:
		if next_row.name == 'tr':
			return next_row
		else: return None
	else: return None

# Convert a dollar string to a float
def money_to_float(moneystring):
	if 'k' in moneystring:
		return float(moneystring.replace('$','').replace(',','').replace('k','')) / 1000
	else:
		return float(moneystring.replace('$','').replace(',',''))

# Given the name of a person, guess the wikipedia url
def get_wiki_url_by_name(name):
	first_last_name = name.split()
	if len(first_last_name) > 0:
		url = "http://en.wikipedia.org/wiki/" + str(first_last_name[0])
		for i in range(len(first_last_name) - 1):
			url += "_" + str(first_last_name[i+1])
		return url
	else: return None

# Check if a list contains a year, month, and day, and if so returns a datetime objet
def does_list_contain_date(list):
	months = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, 
				"September":9, "October":10, "November":11, "December":12}

	# Get year, month, day
	day = False; month = False; year = False

	for i in range(len(list)):
		current_term = list[i]
		if current_term in months.keys():
			month = months[current_term]
		elif is_int(current_term):
			if int(current_term) > 1800:
				year = int(current_term)
			elif int(current_term) >= 1 and int(current_term) <= 31:
				day = int(current_term)
		else: continue

	# If we found a year, month, and day, return date
	if month and year and day:
		new_born_string = str(day) + " " + str(month) + " " + str(year)
		born_datetime = datetime.strptime(new_born_string, "%d %m %Y")
		return born_datetime
	else: return None

# Given two datetimes, get the age (distance) in years
def get_age_from_datetimes(date1, date2):
	return (date1.year - date2.year)

# Guess what the age of someone is (on their wikipedia) given a beautiful soup object
def find_wiki_age(soup):
	born_string = soup.find(id = "mw-content-text").findChildren('p')[0].find(text = re.compile("born"))
	if born_string is None and len(soup.find(id = "mw-content-text").findChildren('p')) > 1:
		born_string = soup.find(id = "mw-content-text").findChildren('p')[1].find(text = re.compile("born"))
	if born_string is None: return None

	born_string_clipped = born_string.replace(" (born ","").replace(")","").replace("(born ","").replace(",","")
	born_string_clipped_split = born_string_clipped.split()
	birth_date = does_list_contain_date(born_string_clipped_split)

	if birth_date is not None:
		return get_age_from_datetimes(datetime.today(), birth_date)
	else: return None

def get_twi_search_url_from_name(name):
	query = urllib2.quote(name)
	return "https://api.twitter.com/1.1/users/search.json?q=" + query

def twi_factors_from_search_response(json_data):
	returned = json.loads(json_data)

	# Iterate through all search results and choose the most likely one (if any)
	# 	We will determine this by choosing the highest verified account in the results
	# 	if a verified one exists. If no verified, we assume no twitter.
	returnVal = (None, None, None)
	for i in range(len(returned)):
		if str(returned[i]['verified']) == 'True':
			followers = returned[i]['followers_count']
			tweets = returned[i]['statuses_count']
			years_on_twi = int(datetime.today().year) - int(str(returned[i]['created_at'])[-4:])
			returnVal = (followers, tweets, years_on_twi)
			break
		else:
			continue
	return returnVal


### FIND ACTRESSES AND ACTORS

# urls = ["http://boxofficemojo.com/people/?view=Actor&pagenum=1&sort=person&order=ASC&p=.htm",
# 			"http://boxofficemojo.com/people/?view=Actor&pagenum=2&sort=person&order=ASC&p=.htm",
# 			"http://boxofficemojo.com/people/?view=Actor&pagenum=3&sort=person&order=ASC&p=.htm"]

# queries = ["\./chart/\?view=Actor&id=amyadams", 
# 			"\./chart/\?view=Actor&id=hughjackman",
# 			"\./chart/\?view=Actor&id=danielradcliffe"]

# people_sum_dict = {}

# # Returns a dictionary of actresses and actors with fields: total gross, # movies, avg gross, top gross
# for num, url in enumerate(urls):
# 	page = urllib2.urlopen(url)
# 	soup = BeautifulSoup(page, 'html5lib')

# 	#Make a query to some content in the first cell of the table
# 	query = soup.find(href = re.compile(queries[num]))

# 	# Find the tr which contains this query
# 	current_tr = find_current_tr(soup, query)

# 	# Get the rest of the rows
# 	next_row = current_tr
# 	while next_row is not None:
# 		# Make a list of the current row
# 		td_list = get_td_list_from_tr(soup, next_row)

# 		# Add the actresses as a key in the dict
# 		people_sum_dict[td_list[0].text] = []
# 		people_sum_dict[td_list[0].text].append(money_to_float(td_list[1].text))
# 		people_sum_dict[td_list[0].text].append(int(td_list[2].text))
# 		people_sum_dict[td_list[0].text].append(money_to_float(td_list[3].text))
# 		people_sum_dict[td_list[0].text].append(money_to_float(td_list[5].text))

# 		# Get the next row
# 		next_row = find_next_row(soup, next_row)

# # Convert dict to a pandas dataframe (we didn't start with this for practice!)
# actress_data = pd.DataFrame.from_dict(people_sum_dict, orient='index')
# actress_data['Names'] = list(actress_data.index)
# actress_data.columns = ['TotalGross', 'NumMovies', "AvgGross", "TopGross", "Names"]


# ### GET AGE OF ACTRESS OR ACTOR

# # List we will put the ages into
# actress_ages = []

# row_iterator = actress_data.iterrows()
# last = row_iterator.next()
# row_iterator = actress_data.iterrows()

# counter = 0

# for name, row in row_iterator:
# 	counter += 1

# 	# Get the wiki url we need to go to for the age
# 	url = get_wiki_url_by_name(name)

# 	# Get the age of the actress and append to list
# 	try: page = urllib2.urlopen(url)
# 	except: 
# 		actress_ages.append(None)
# 		continue
# 	try: soup = BeautifulSoup(page, 'html5lib')
# 	except: 
# 		actress_ages.append(None)
# 		continue
# 	age = find_wiki_age(soup)
# 	actress_ages.append(age)
# 	print str(counter) + " out of " + str(len(actress_data))

# 	# Next row
# 	last = row

# print str(len(actress_data)), str(len(actress_ages))
# actress_data['Age'] = actress_ages
# print actress_data.head()

# with open('current_movies_df.p','wb') as picklefile:
# 	pickle.dump(actress_data,picklefile)


### GET TWITTER DATA OF ACTRESS OR ACTOR

# import oauth2 as oauth
# import json

# # Oauth2 for Twitter API data
# CONSUMER_KEY = "AeeP8XqdVn4JKkFe1taObuLo7"
# CONSUMER_SECRET = "BAzTezf78LneLG0zVXVaIeG6bXOaCnJ12ennEXZVVNK1plCiwc"
# ACCESS_KEY = "2815366039-1HLdZHBjOf3A2ZStoi2GJPZx8OsobTU5FtAQzON"
# ACCESS_SECRET = "coXCsBzu7T38rU3RQYh9BLGQkQLHXtMqcal1rNYHkqk6e"

# consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
# access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
# client = oauth.Client(consumer, access_token)

# # Load pickledata for data frame
# with open('current_movies_df.p','rb') as picklefile:
#  	actress_data = pickle.load(picklefile)

# # Reset the index to integers
# actress_data.index = range(len(actress_data))

# # Iterate through names in our data frame, query twitter for follower count, tweets, 
# # 	and date twitter account started

# # Load current twitter data
# with open('twitter_data.p','rb') as picklefile:
#  	list_length, names, followers_all, num_tweets_all, years_on_twi_all = pickle.load(picklefile)

# # Initialize twitter data if needed
# # list_length = 0
# # names = []
# # followers_all = []
# # num_tweets_all = []
# # years_on_twi_all = []

# row_iterator = actress_data.iterrows()
# last = row_iterator.next()
# row_iterator = actress_data.iterrows()

# # We need to keep track of the queries we have already made bc of rate limiting
# for i in range(list_length):
# 	last = row_iterator.next()

# # Make queries to twitter API
# counter = 0
# for name, row in row_iterator:
# 	counter += 1

# 	twi_url_request = get_twi_search_url_from_name(str(row['Names']))
# 	twi_response, twi_data = client.request(twi_url_request)

# 	# Check rate limit
# 	queries_left = int(twi_response['x-rate-limit-remaining'])
# 	if queries_left > 0:
# 		followers, num_tweets, years_on_twi = twi_factors_from_search_response(twi_data)
# 		followers_all.append(followers)
# 		num_tweets_all.append(num_tweets)
# 		years_on_twi_all.append(years_on_twi)
# 		names.append(str(row['Names']))
# 	else: 
# 		# Write what we have to the file
# 		with open('twitter_data.p','wb') as picklefile:
# 			# What is the current length of the lists
# 			list_length = len(followers_all)
# 			print (list_length, names, followers_all, num_tweets_all, years_on_twi_all)
#  			pickle.dump((list_length, names, followers_all, num_tweets_all, years_on_twi_all), picklefile)

#  		break

# 	print str(counter)

# 	# Next row
# 	last = row

# # Write to file
# with open('twitter_data.p','wb') as picklefile:
# 	# What is the current length of the lists
# 	list_length = len(followers_all)
# 	print (list_length, names, followers_all, num_tweets_all, years_on_twi_all)
#  	pickle.dump((list_length, names, followers_all, num_tweets_all, years_on_twi_all), picklefile)

# Open twitter data file and append to dataframe
# with open('current_movies_df.p','rb') as picklefile:
#  	actress_data = pickle.load(picklefile)

# with open('twitter_data.p','rb') as picklefile:
# 	list_length, names, followers_all, num_tweets_all, years_on_twi_all = pickle.load(picklefile)

# actress_data['NumFollowers'] = followers_all
# actress_data['NumTweets'] = num_tweets_all
# actress_data['YrsOnTwitter'] = years_on_twi_all
# actress_data['NumTweetsPerYr'] = actress_data['NumTweets'] / actress_data['YrsOnTwitter']

# # Write to file
# with open('df_w_twitter.p','wb') as picklefile:
#  	pickle.dump(actress_data, picklefile)

### REGRESSION MODEL
import statsmodels.formula.api as sm
import math

with open('df_w_twitter.p','rb') as picklefile:
 	actress_data = pickle.load(picklefile)

# Reset the index to integers
actress_data.index = range(len(actress_data))

# Log transform dependent variable
actress_data['ln_NumFollowers'] = np.log(actress_data['NumFollowers'])
actress_data['ln_NumTweetsPerYr'] = np.log(actress_data['NumTweetsPerYr'])
actress_data['ln_AvgGross'] = np.log(actress_data['AvgGross'])
actress_data['ln_Age'] = np.log(actress_data['Age'])

# Remove NaN and outliers
actress_data_subset = actress_data.dropna()[actress_data['NumFollowers'] <= 1000000]

X = actress_data_subset[['ln_NumTweetsPerYr', 'ln_AvgGross', 'ln_Age']]
Y = actress_data_subset['ln_NumFollowers']

linmodel = sm.OLS(Y,X).fit()

print linmodel.summary()

plt.plot(Y, linmodel.predict(X), 'go')
plt.plot(Y, Y, 'm--', label = 'Ideal Prediction')
plt.show()








