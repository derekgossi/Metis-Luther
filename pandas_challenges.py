from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dt

# Import movie data from csv into a pandas data frame
movie_data = pd.io.parsers.read_csv('2013_movies.csv')

## CHALLENGE #1

# Get the release dates in the proper format for plotting
release_date_datetimes = []
for i in movie_data['ReleaseDate']:
	release_date_datetimes.append(datetime.strptime(i, "%Y-%m-%d %H:%M:%S"))

# Plot domestic total gross over time
plt.plot_date(release_date_datetimes, movie_data['DomesticTotalGross'], tz=None, xdate=True, ydate=False)
plt.show()


## CHALLENGE #2

# Plot domestic total gross vs runtime
plt.scatter(movie_data['Runtime'], movie_data['DomesticTotalGross'])
plt.show()

## CHALLENGE #3

# Group data by rating and print
movie_data_ratings_sum = movie_data.groupby(['Rating'])['Runtime', 'DomesticTotalGross'].mean()
print movie_data_ratings_sum.head()

## CHALLENGE #4

# Get new data frames by ratings subsets, so we have a list of data frames for each rating
movie_data_subsets = []
unique_ratings = movie_data['Rating'].unique()

for rating in unique_ratings:
	movie_data_subsets.append(movie_data[movie_data['Rating'] == rating])

# Iterate through each rating subset and add as a subplot
for num, rating_subset in enumerate(movie_data_subsets):
	# Get the release dates in the proper format for plotting
	release_date_datetimes = []
	for i in rating_subset['ReleaseDate']:
		release_date_datetimes.append(datetime.strptime(i, "%Y-%m-%d %H:%M:%S"))

	plt.subplot(4, 1, num+1)
	plt.plot_date(release_date_datetimes, rating_subset['DomesticTotalGross'], tz=None, xdate=True, ydate=False)

# Show plot
plt.show()


## CHALLENGE #5

# Group data by director and get average movie gross
movie_data_director_avg_gross = movie_data.groupby(['Director'])['DomesticTotalGross'].mean()
df = pd.DataFrame(movie_data_director_avg_gross).sort(['DomesticTotalGross'],ascending=False)
print df.head()


## CHALLENGE #6





