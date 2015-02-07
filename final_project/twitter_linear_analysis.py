import numpy as np
import pickle
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.formula.api as sm
from sklearn.linear_model import Ridge
from sklearn.preprocessing import normalize
from sklearn import cross_validation

# Load dataframe
with open('df_w_celeb_dist.p','rb') as picklefile:
	actress_data = pickle.load(picklefile)

# Drop NaN values
actress_data = actress_data.dropna()
actress_data = actress_data[actress_data['CelebDist'] > 0]

# Add log features
actress_data['ln_NumFollowers'] = np.log(actress_data['NumFollowers'])
actress_data['ln_NumTweetsPerYr'] = np.log(actress_data['NumTweetsPerYr'])
actress_data['ln_AvgGross'] = np.log(actress_data['AvgGross'])
actress_data['ln_TotalGross'] = np.log(actress_data['TotalGross'])
actress_data['ln_Age'] = np.log(actress_data['Age'])
actress_data['ln_CelebDist'] = np.log(actress_data['CelebDist'])
actress_data['Ones'] = 1.0

# Set data for training
X = actress_data[['NumTweetsPerYr', 'YrsOnTwitter', 'Age', 'TopGross', 
					'AvgGross', 'NumMovies', 'CelebDist', 'Ones']]
y = actress_data['ln_NumFollowers']

# Initialize linear ridge model
linear_model = Ridge(alpha=1.0)

# Get cross validation splits and fit model
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.75, random_state=0)
fitted_model = linear_model.fit(X_train,y_train)
scores = cross_validation.cross_val_score(linear_model, X, y, cv=4)

# Print sumamary statistics
print scores
print scores.mean()
print scores.std()
print fitted_model.coef_
print fitted_model.intercept_


