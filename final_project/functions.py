
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
	returnVal = (None, None, None, None)
	for i in range(len(returned)):
		if str(returned[i]['verified']) == 'True':
			followers = returned[i]['followers_count']
			tweets = returned[i]['statuses_count']
			user_name = returned[i]['screen_name']
			years_on_twi = int(datetime.today().year) - int(str(returned[i]['created_at'])[-4:])
			returnVal = (followers, tweets, years_on_twi, user_name)
			break
		else:
			continue
	return returnVal


