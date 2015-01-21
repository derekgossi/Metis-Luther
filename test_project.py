#GET /1.1/users/search.json?q=Anna%20Kendrick HTTP/1.1
#Authorization:
#OAuth oauth_consumer_key="DC0sePOBbQ8bYdC8r4Smg",
#oauth_signature_method="HMAC-SHA1",
#oauth_timestamp="1421785641",
#oauth_nonce="3486956767",
#oauth_version="1.0",
#oauth_token="2815366039-fDBncJHWLiMT8xvCHlbttBcGgY1vgqQiN9ZNPue",
#oauth_signature="OngaLZmH4VVcATAmkY%2BE%2Bcj1iEk%3D"
#Host:
#api.twitter.com
#X-Target-URI:
#https://api.twitter.com
#Connection:
#Keep-Alive

import urllib2
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime


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


### FIND ACTRESSES AND ACTORS

urls = ["http://boxofficemojo.com/people/?view=Actor&pagenum=1&sort=person&order=ASC&p=.htm",
			"http://boxofficemojo.com/people/?view=Actor&pagenum=2&sort=person&order=ASC&p=.htm",
			"http://boxofficemojo.com/people/?view=Actor&pagenum=3&sort=person&order=ASC&p=.htm"]

queries = ["\./chart/\?view=Actor&id=amyadams", 
			"\./chart/\?view=Actor&id=hughjackman",
			"\./chart/\?view=Actor&id=danielradcliffe"]

people_sum_dict = {}

# Returns a dictionary of actresses and actors with fields: total gross, # movies, avg gross, top gross
for num, url in enumerate(urls):
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page, 'html5lib')

	#Make a query to some content in the first cell of the table
	query = soup.find(href = re.compile(queries[num]))

	# Find the tr which contains this query
	current_tr = find_current_tr(soup, query)

	# Get the rest of the rows
	next_row = current_tr
	while next_row is not None:
		# Make a list of the current row
		td_list = get_td_list_from_tr(soup, next_row)

		# Add the actresses as a key in the dict
		people_sum_dict[td_list[0].text] = []
		people_sum_dict[td_list[0].text].append(money_to_float(td_list[1].text))
		people_sum_dict[td_list[0].text].append(int(td_list[2].text))
		people_sum_dict[td_list[0].text].append(money_to_float(td_list[3].text))
		people_sum_dict[td_list[0].text].append(money_to_float(td_list[5].text))

		# Get the next row
		next_row = find_next_row(soup, next_row)

# Convert dict to a pandas dataframe (we didn't start with this for practice!)
actress_data = pd.DataFrame.from_dict(people_sum_dict, orient='index')
actress_data.columns = ['TotalGross', 'NumMovies', "AvgGross", "TopGross"]


### GET ADDITIONAL FEATURES BITCH! (THIS TIME FROM WIKIPEDIA)

# List we will put the ages into
actress_ages = []

row_iterator = actress_data.iterrows()
last = row_iterator.next()
for name, row in row_iterator:
	# Get the wiki url we need to go to for the age
	url = get_wiki_url_by_name(name)
	print url

	# Get the age of the actress and append to list
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page, 'html5lib')
	if not soup:
		continue
	age = find_wiki_age(soup)
	print age
	actress_ages.append(age)

	# Next row
	last = row

print actress_ages








