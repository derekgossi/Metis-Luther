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


def findCurrentTr(soup, inside_stuff):
	current_level = inside_stuff
	if current_level is not None:
		if current_level.name == 'tr':
			return current_level
		else:
			while current_level.name != 'body':
				current_level = current_level.findParent()
				if current_level.name == 'tr':
					return current_level

def getTdListFromTr(soup, tr, expected_width):
	assert tr is not None, 'Not given anything'
	assert tr.name == 'tr', 'Not given a tr'
	assert type(expected_width) is int, 'Expected width is not int'

	# Find all the cells
	cells = tr.findChildren('td')
	return cells

def findNextRow(soup, tr):
	assert tr is not None, 'Not given anything'
	assert tr.name == 'tr', 'Not given a tr'

	next_row = tr.findNextSibling()

	# Check if it exists and is a row
	if next_row is not None:
		if next_row.name == 'tr':
			return next_row
		else:
			return None
	else:
		return None

## Find people
url = "http://boxofficemojo.com/people/"
page = urllib2.urlopen(url)
soup = BeautifulSoup(page, 'html5lib')

#Make a query to some content in the first cell of the table
query = soup.find(text = re.compile("\./chart/\?view=Actor\&id\=amyadams"))
print query

# # Find the tr which contains this query
# current_tr = findCurrentTr(soup, query)

# # Get the rest of the rows
# people_summary_dict = {}
# next_row = current_tr
# while next_row is not None:
# 	# Make a list of the current row
# 	td_list = getTdListFromTr(soup, next_row, 6)

# 	# Add it to the dict
# 	for cell in td_list:
# 		print cell.text

# 	# Get the next row
# 	next_row = findNextRow(soup, next_row)



# df2 = pd.DataFrame({ 'A' : 1.,
# 	'B' : pd.Timestamp('20130102'),
# 	'C' : pd.Series(1,index=list(range(4)),dtype='float32'),
# 	'D' : np.array([3] * 4,dtype='int32'),
# 	'E' : pd.Categorical(["test","train","test","train"]),
# 	'F' : 'foo' })

# print df2






	


#<a href="./chart/?view=Actor&amp;id=amyadams.htm"><b>Amy Adams</b></a>
		


# def find_first_row_of_table(soup, upper_left_header):
#     all_rows = soup.find_all('tr')
#     for i in all_rows:
        

# print find_first_row_of_table(soup, ):
# 	text=re.compile()


