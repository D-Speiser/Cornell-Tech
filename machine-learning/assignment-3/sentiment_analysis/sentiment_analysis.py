# Note: converted from .ipynb format
from sklearn import cluster, preprocessing as pre, linear_model as lm, cross_validation as cv, decomposition as decomp, metrics
import matplotlib.pyplot as plt
from scipy import spatial
import pandas as pd
import numpy as np
import random
import sys
import re
get_ipython().magic(u'matplotlib inline')

DATA_SET = {
    "amazon": "data/amazon_cells_labelled.txt",
    "imdb": "data/imdb_labelled.txt",
    "yelp": "data/yelp_labelled.txt"
}

# A. Parse data sets
amazon = pd.read_csv(DATA_SET['amazon'], sep="\t", header=None, names=['Sentence', 'Label']).dropna()
imdb = pd.read_csv(DATA_SET['imdb'], sep="\t(?=[01])", header=None, names=['Sentence', 'Label'], engine='python').dropna()
yelp = pd.read_csv(DATA_SET['yelp'], sep="\t", header=None, names=['Sentence', 'Label']).dropna()

parsed_data = dict(zip(DATA_SET.keys(), [amazon, imdb, yelp]))

def get_label_ratio (data_set):
    label_0 = sum(data_set['Label'] == 0)
    label_1 = sum(data_set['Label'] == 1)
    return (label_0, label_1)

# Print ratio of different labels per data set
for k, data in parsed_data.items():
    label_0, label_1 = get_label_ratio(data)
    print k.upper()
    print "Label 0: ", label_0
    print "Label 1: ", label_1, "\n\n"

# B. Preprocessing
def preprocess (data):    
    stopwords = set(["the", "and", "or", "a"]) # add some more later!
    for i in range(len(data)):
        data[i] = re.sub("[^a-zA-Z]", " ", data[i])
        data[i] = data[i].lower().strip()
        temp = [word for word in data[i].split() if word not in stopwords]
        data[i] = " ".join(temp)
    return data

for k, data in parsed_data.items():
    parsed_data[k]['Sentence'] = preprocess(data['Sentence'].values)

# C. Split training and testing data
def split_data (data):
    zeros = data.loc[data['Label'] == 0]
    ones = data.loc[data['Label'] == 1]
    train, test = pd.concat([zeros[:400], ones[:400]]), pd.concat([zeros[400:], ones[400:]])
    return (train, test)

train_dict, test_dict = {}, {}
for k, data in parsed_data.items():
    train_dict[k], test_dict[k] = split_data(data)
    
train = pd.concat(train_dict, ignore_index=True)
test = pd.concat(test_dict, ignore_index=True)

# D. Bag of words
def get_bag (data):
    bag = []
    for sentence in data:
        for word in sentence.split():
            bag.append(word)
    return np.unique(bag)

bag = get_bag(train['Sentence'])

# N = 1 is same as str.split()
def n_grams (sentence, n):
    bag = []
    words = sentence.split()
    for i in range(len(words)-n+1):
        bag.append(" ".join(words[i:i+n]))
    return bag

def get_feature_vectors (bag, data, n=1):
    features, labels = [], []
    for i in range(len(data)):
        f = []
        s = n_grams(data['Sentence'][i], n)
        l = data['Label'][i]
        for word in bag:
            f.append(s.count(word))
        features.append(f)
        labels.append(l)
    return pd.DataFrame({"feature": features, "label": labels}, dtype="float64")

train_features = get_feature_vectors(bag, train)
test_features = get_feature_vectors(bag, test)

def print_rand_features (data):
    plt.title("Random Feature Vector Freq.")
    plt.xlabel("Labels")
    plt.ylabel("Frequencies")
    plt.hist(data, range=[0,np.max(data)])
    plt.xticks(range(0,np.max(data)+1))
    plt.show()
    return

# print 2 random feature vectors from training set
two_rand = random.sample(train_features['feature'].values, 2)
print "Random Training Sample Vector 1: \n", two_rand[0]
print "\nRandom Training Sample Vector 2: \n", two_rand[1]

for fv in two_rand:
    print_rand_features(fv)

# E. Postprocessing
def post_process (data):
    norm = []
    for features in data:
        mapped = map(float, features)
        norm.append(pre.normalize(mapped, norm='l2').flatten())
    return norm

train_features_post = zip(post_process(train_features['feature'].values), train_features['label'])
test_features_post = zip(post_process(test_features['feature'].values), test_features['label'])

train_df = pd.DataFrame(train_features_post, columns=["feature", "label"])
test_df = pd.DataFrame(test_features_post, columns=["feature", "label"])

cents, clusts, labs = KMeans(k_clusters = 2, max_iterations = 300).fit(train_df)

def plot_cent_freq (data):
    plt.hist(data)
    plt.title("Centroids Frequency")
    plt.yscale('log')
    plt.xlabel("Values")
    plt.ylabel("Log Frequency")
    plt.show()
    return

# Show distribution frequencies (log scale)
for c in cents:
    plot_cent_freq(c)

for idx, cent in enumerate(cents):
    print "Centroid {0}:\n{1}".format(idx, cent)

# accuracy was calculated using the 'purity' method, not NMI or RI
def get_km_accuracy(label_set):
    for idx, labels in enumerate(label_set):
        counts = np.bincount(labels)
        cluster_label = np.argmax(counts)
        print "Number of elements in cluster {0}: {1}".format(idx, len(labels))
        print "Accuracy (Purity) of cluster {0} with label {1}: {2}".format(idx, cluster_label, (labels == cluster_label).sum() / float(len(labels)))
    return

get_km_accuracy(labs)

# G. Logistic Regression
def logistic_regression (x_train, y_train, x_test, y_test, bag):
    # Fit model
    lr = lm.LogisticRegression(random_state=1).fit(x_train, y_train)

    # Cross validation
    scores = cv.cross_val_score(lr, x_train, y_train, cv=15)
    print "Cross validation: ", scores.mean()

    # Prediction and scoring
    predictions = lr.predict(x_test)
    accuracy = (predictions == y_test).sum() / float(len(y_test))
    print "Prediction accuracy: ", accuracy
    
    # Confusion matrix
    print "CONFUSION MATRIX:"
    print metrics.confusion_matrix(y_test, predictions)
    
    # most important weights/words
    weights = [(idx, val) for idx, val in enumerate(lr.coef_[0])]
    weights.sort(key=lambda tup: tup[1], reverse=True)
    num_important_words = 10
    important_positive, important_negative = [], []
    for i in range(num_important_words):
        important_positive.append(bag[weights[i][0]])
        important_negative.append(bag[weights[len(weights) - i - 1][0]])

    print "Top 10 Positive Important Words:\n", important_positive
    print "Top 10 Negative Important Words:\n", important_negative
    return

# G. Logistic Regression
x_train = train_df['feature'].values.tolist()
x_test = test_df['feature'].values.tolist()
y_train = train_df['label']
y_test = test_df['label']
logistic_regression(x_train, y_train, x_test, y_test, bag)


# Repeat Process Using N-Grams
# --------------------------

# Create bag of bi-grams (n=2)
bi_grams = np.unique(np.concatenate([n_grams(sentence, 2) for sentence in train['Sentence']]))

# Collect feature vectors for each sentence in data
bg_train_features = get_feature_vectors(bi_grams, train, 2)
bg_test_features = get_feature_vectors(bi_grams, test, 2)

# Print 2 random feature vectors from training set
bg_two_rand = random.sample(bg_train_features['feature'].values, 2)
print "Random Training Sample Vector 1: \n", bg_two_rand[0]
print "\nRandom Training Sample Vector 2: \n", bg_two_rand[1]

# Show distribution frequencies (log scale)
for fv in bg_two_rand:
    print_rand_features(fv)

# N-gram post processing
bg_train_features_post = zip(post_process(bg_train_features['feature'].values), bg_train_features['label'])
bg_test_features_post = zip(post_process(bg_test_features['feature'].values), bg_test_features['label'])

bg_train_df = pd.DataFrame(bg_train_features_post, columns=["feature", "label"])
bg_test_df = pd.DataFrame(bg_test_features_post, columns=["feature", "label"])

# Perform K-Means
bg_cents, bg_clusts, bg_labs = KMeans(k_clusters = 2, max_iterations = 300).fit(bg_train_df)

# Print centroids
for idx, cent in enumerate(bg_cents):
    print "Centroid {0}:\n{1}".format(idx, cent)

# Accuracy
get_km_accuracy(bg_labs)

# Logistic regressin on bigram data
bg_x_train = bg_train_df['feature'].values.tolist()
bg_x_test = bg_test_df['feature'].values.tolist()
bg_y_train = bg_train_df['label']
bg_y_test = bg_test_df['label']
logistic_regression(bg_x_train, bg_y_train, bg_x_test, bg_y_test, bi_grams)

# I. PCA
def PCA(features, dimension):
    features -= np.array(features).mean(axis=0)
    u, s, v = np.linalg.svd(np.asmatrix(features))
    return features.dot(np.array(v[:dimension]).T)

dimensions = [10, 50, 100]
train_dfs_truncated = {}
test_dfs_truncated = {}
for dim in dimensions:
    train_dfs_truncated[dim] = pd.DataFrame(zip(PCA(x_train, dim), train_features['label']), columns=["feature", "label"])
    test_dfs_truncated[dim] = pd.DataFrame(zip(PCA(x_test, dim), test_features['label']), columns=["feature", "label"])

for dim in train_dfs_truncated:
    cents_post_pca, clusts_post_pca, labs_post_pca = KMeans(k_clusters = 2, max_iterations = 300).fit(train_dfs_truncated[dim])
    print "K-Means for features of dimension: ", dim
    for idx, cent in enumerate(cents_post_pca):
        print "Centroid {0}:\n{1}".format(idx, cent)
    get_km_accuracy(labs_post_pca)
    print "\n"

for dim in train_dfs_truncated:
    print "Logistic Regression for features of dimension: ", dim
    
    x_train = train_dfs_truncated[dim]['feature'].values.tolist()
    x_test = test_dfs_truncated[dim]['feature'].values.tolist()

    y_train = train_dfs_truncated[dim]['label']
    y_test = test_dfs_truncated[dim]['label']

    # Fit model
    lr_truncated = lm.LogisticRegression(random_state=1).fit(x_train, y_train)

    # Cross validation
    scores = cv.cross_val_score(lr_truncated, x_train, y_train, cv=15)
    print "Cross validation: ", scores.mean()

    # Prediction and scoring
    predictions = lr_truncated.predict(x_test)
    accuracy = (predictions == y_test).sum() / float(len(y_test))
    print "Prediction accuracy: ", accuracy

    # most important weights/words
    weights = [(idx, val) for idx, val in enumerate(lr_truncated.coef_[0])]
    weights.sort(key=lambda tup: tup[1], reverse=True)
    num_important_words = 10
    important_positive, important_negative = [], []
    for i in range(num_important_words):
        important_positive.append(bag[weights[i][0]])
        important_negative.append(bag[weights[len(weights) - i - 1][0]])

    print "Top 10 Positive Important Words:\n", important_positive
    print "Top 10 Negative Important Words:\n", important_negative

for dim in train_dfs_truncated:
    x_train = train_dfs_truncated[dim]['feature'].values.tolist()
    x_test = test_dfs_truncated[dim]['feature'].values.tolist()
    y_train = train_dfs_truncated[dim]['label']
    y_test = test_dfs_truncated[dim]['label']
    
    logistic_regression(x_train, y_train, x_test, y_test, bag)
    print "\n\n"
