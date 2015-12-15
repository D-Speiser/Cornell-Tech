# Note: converted from .ipynb format
import numpy as np
import pandas as pd
import pprint as pp
import itertools as it
from sklearn import cross_validation as cv, naive_bayes as nb, linear_model as lm

train_data = pd.read_json('data/train.json') # parse training set (given in .json format)
test_data = pd.read_json('data/test.json')   # parse testing set (given in .json format)

# B
ingredients_train = np.array(train_data['ingredients']) # save training ingredients
ingredients_test = np.array(test_data['ingredients'])   # save testing ingredients
cuisines_train = np.array(train_data['cuisine'])        # save training cuisines
# find unique cuisines and ingredients
unique_cuisine_train = np.unique(cuisines_train) # finds unique elements. can also be done using sets
# uses itertools chain method to append all sub-lists from a list of lists, and then find unique elements
unique_ingredients_train = np.unique(list(it.chain.from_iterable(ingredients_train)))

print "Number of samples in the training data set: {0}".format(len(train_data))
print "Number of unique cuisine catagories: {0}".format(len(unique_cuisine_train))
print "Number of unique ingredients in the training set: {0}".format(len(unique_ingredients_train))

# C
def binary_feature_vectorization(unique_ingredients, ingredient_lists):
    feature_vectors = [] # list to contain all feature vectors
    for ingredients in ingredient_lists:
        # create vector of length 'd', with each element instantiated to '0'
        bin_feat_vect= np.zeros(len(unique_ingredients))
        for ingredient in ingredients: # for each ingredient
            if ingredient in unique_ingredients: # if it is in the recipe
                # set this ingredient to '1', indicating its presence in the recipe
                bin_feat_vect[np.where(unique_ingredients == ingredient)[0][0]] = 1
        feature_vectors.append(bin_feat_vect) # add to list
    return np.array(feature_vectors)

feature_vectors_train = binary_feature_vectorization(unique_ingredients_train, ingredients_train)
feature_vectors_test = binary_feature_vectorization(unique_ingredients_train, ingredients_test)

# D, E, F
# use 3 different classifiers to fit the data, and perform 3 fold cross validation on each
gnb = nb.GaussianNB().fit(feature_vectors_train, cuisines_train) 
bnb = nb.BernoulliNB().fit(feature_vectors_train, cuisines_train)
lr = lm.LogisticRegression().fit(feature_vectors_train, cuisines_train)
# cross validation, k=3
scores_gauss = cv.cross_val_score(gnb, feature_vectors_train, cuisines_train, cv=3)
scores_bernoulli = cv.cross_val_score(bnb, feature_vectors_train, cuisines_train, cv=3)
scores_linear = cv.cross_val_score(lr, feature_vectors_train, cuisines_train, cv=3)

print "Number of folds: 3"
print "Mean accuracy Gaussian: ", scores_gauss.mean()
print "Mean accuracy Bernoulli: ", scores_bernoulli.mean()
print "Mean accuracy Linear: ", scores_linear.mean()

# G
# predict test cuisine labels using fitted training data
test_predict = lr.predict(feature_vectors_test)
# store predictions in a dataframe, and save it to a csv file in the required column format
submission = pd.DataFrame({'id': test_data['id'], 'cuisine': test_predict})[['id', 'cuisine']]
submission.to_csv('cuisine_submission.csv', index=False)
print submission
