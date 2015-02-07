
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
actress_data['Names'] = list(actress_data.index)
actress_data.columns = ['TotalGross', 'NumMovies', "AvgGross", "TopGross", "Names"]


### GET AGE OF ACTRESS OR ACTOR

# List we will put the ages into
actress_ages = []

row_iterator = actress_data.iterrows()
last = row_iterator.next()
row_iterator = actress_data.iterrows()

counter = 0

for name, row in row_iterator:
	counter += 1

	# Get the wiki url we need to go to for the age
	url = get_wiki_url_by_name(name)

	# Get the age of the actress and append to list
	try: page = urllib2.urlopen(url)
	except: 
		actress_ages.append(None)
		continue
	try: soup = BeautifulSoup(page, 'html5lib')
	except: 
		actress_ages.append(None)
		continue
	age = find_wiki_age(soup)
	actress_ages.append(age)
	print str(counter) + " out of " + str(len(actress_data))

	# Next row
	last = row

print str(len(actress_data)), str(len(actress_ages))
actress_data['Age'] = actress_ages

with open('current_movies_df.p','wb') as picklefile:
	pickle.dump(actress_data,picklefile)

