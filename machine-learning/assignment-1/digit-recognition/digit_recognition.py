# Note: Converted from ipynb format
from matplotlib import pylab as plt, image as img
from sklearn import metrics, cross_validation
from operator import itemgetter
from scipy import spatial
import sklearn as sk
import pandas as pd
import numpy as np
import KNN
import sys
get_ipython().magic(u'matplotlib inline')

# file paths
TRAIN_PATH = "data/train.csv"
TEST_PATH = "data/test.csv"

# read in the datasets from the respective CSV files
train_data = pd.read_csv(TRAIN_PATH)
test_data = pd.read_csv(TEST_PATH)

# store as numpy arrays
train_digits = train_data.ix[:,1:].values
train_labels = train_data['label'].values
test_digits = test_data.values

def get_digit_info (labels):
    digit_flag, digit_freq, first_instance_idx = np.zeros(10), np.zeros(10), {}
    for i, label in enumerate(labels):
        digit_freq[labels[i]] += 1
        if digit_flag[label] == False:
            digit_flag[label] = True
            first_instance_idx[label] = i
    return (first_instance_idx, dict(zip(range(10), digit_freq / sum(digit_freq))))

# display MNIST digits
def display_digit (digit, label):
    d = digit.reshape(28,28)
    plt.matshow(d, cmap='gray_r')
    img.imsave('digit_' + str(label), d, cmap="gray_r")
    return

# get frequencies of each digit and first instance index
indices, frequencies = get_digit_info(train_labels)

# print one of each
for i in range(len(indices)):
    display_digit(train_digits[indices[i]], i)

# build normalized histogram
def build_normalized_histogram(digit_freq, labels):
    fig = plt.figure()
    plt.hist(digit_freq.keys(), weights=digit_freq.values())
    plt.title('Normalized Histogram')
    plt.xlabel('Digit #')
    plt.ylabel('Frequency')
    plt.gca().set_xlim([0, 9])
    fig.savefig('norm_hist.png')
    return
    
build_normalized_histogram(frequencies, train_labels)

# find the best matches
def find_best_matches(first_instance, digits, labels):
    best_fits = [(sys.maxint, -1)] * 10 # best fit array containing a tuple (distance, idx) for each digit
    for idx, digit in enumerate(digits): # for each matrix of pixels
        if idx != first_instance[labels[idx]]: # if not first instance of this digit
            L2 = spatial.distance.euclidean(digits[first_instance[labels[idx]]], digit) # Distance = euclidean(first_instance_matrix, pixel_matrix[idx])
            if L2 < best_fits[labels[idx]][0]: # if current distance < current smallest distance
                best_fits[labels[idx]] = (L2, idx) # set new distance as smallest 
    return best_fits

best_fits = find_best_matches(indices, train_digits, train_labels)

for digit, fit in enumerate(best_fits):
        print "L2 distance between sample {0} and nearest neighbor: {1} pixels".format(digit, fit[0])

# get pairwise distance and plot histograms
def get_pairswise_distance (digits, labels):
    binary_classifier = {"zeros": [], "ones": []}

    for idx, digit in enumerate(digits):
        # Only concerned with digits 0 and 1
        if labels[idx] > 1:
            continue
        elif labels[idx] == 0:
            binary_classifier['zeros'].append(digit)
        else:
            binary_classifier['ones'].append(digit)

    # Genuine values
    genuine_zero = metrics.pairwise.pairwise_distances(binary_classifier['zeros']).flatten()
    genuine_one = metrics.pairwise.pairwise_distances(binary_classifier['ones']).flatten()
    genuine_total = np.concatenate((genuine_zero, genuine_one))

    # Imposter values
    imposter_zero = metrics.pairwise.pairwise_distances(binary_classifier['zeros'], binary_classifier['ones']).flatten()
    imposter_one = metrics.pairwise.pairwise_distances(binary_classifier['ones'], binary_classifier['zeros']).flatten()
    imposter_total = np.concatenate((imposter_zero, imposter_one))

    return (genuine_total, imposter_total)

def plot_pairwise_distance (genuine, imposter):
    fig = plt.figure()
    plt.hist(genuine, alpha=0.5, label='Genuine')
    plt.hist(imposter, alpha=0.5, label='Imposter')
    plt.title('Pairwise Distance Histogram')
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.legend(loc='upper right')
    fig.savefig('pw_distance.png')
    return

genuine, imposter = get_pairswise_distance(train_digits, train_labels)
plot_pairwise_distance(genuine, imposter)

# plot ROC Curve
def plot_roc_curve (genuine, imposter):
    zeros = np.zeros(len(genuine))
    ones = np.ones(len(imposter))
    y_true = np.concatenate((zeros, ones))
    y_score = np.concatenate((genuine, imposter))
    
    # Remember - lower distance is a higher score! 
    # To account for that, subtract all distances from max distance and plot
    m = max(y_score)
    for i in range(len(y_score)):
        y_score[i] = np.float(m - y_score[i])
        
    fpr, tpr, thresholds = metrics.roc_curve(y_true, y_score, pos_label=0)
    roc_auc = sk.metrics.auc(fpr, tpr)
    
    fig = plt.figure()
    plt.title('Receiver Operating Characteristic')
    plt.plot(fpr, tpr, 'b', label='AUC = %0.2f'% roc_auc)
    plt.legend(loc='lower right')
    plt.plot([0,1],[0,1],'r--')
    plt.plot([1,0], 'g--')
    plt.xlim([-0.1,1.2])
    plt.ylim([-0.1,1.2])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    fig.savefig('roc_curve.png')
    return (fpr, tpr)

fpr, tpr = plot_roc_curve(genuine, imposter)

# cross validation
def cross_validate (folds, digits, labels):
    cv = cross_validation.KFold(len(digits),  n_folds=folds)
    results = []
    for train_idx, test_idx in cv:
        # Divide into buckets
        x_train = digits[train_idx]
        y_train = labels[train_idx]
        x_test = digits[test_idx]
        y_test = labels[test_idx]
        
        # Fit and predict
        kNN = KNN.KNNeighborsClassifier(3, x_train, y_train, x_test)
        prediction = kNN.predict(x_test)
        accuracy = (prediction == y_test).sum() / float(len(y_test))
        confusion_matrix = metrics.confusion_matrix(y_test, prediction)
        results.append((prediction, accuracy, confusion_matrix))  
    return results

results = cross_validate(3, train_digits, train_labels)

# print results of cross validation
predictions, accuracy, confusion_matrix = [], [], []
s = 0
for p, a, c in results:
    s += len(p)
    predictions.append(p)
    accuracy.append(a)
    confusion_matrix.append(c)
    
print "Number of digits: ", s
print "Number of folds: ", "3"
print "Mean accuracy: ", np.mean(accuracy)
print "Confusion Matrix: \n", sum(confusion_matrix)

cf_matrix = pd.DataFrame(sum(confusion_matrix))
file_name = "confusion_matrix_" + str(s) + '.csv' 
cf_matrix.to_csv(file_name)

# fit and predict using our KNN Classifier
kNN = KNN.KNNeighborsClassifier(3, train_digits, train_labels, test_digits)
predicted_values = kNN.predict(test_digits)
id = range(1, len(predicted_values)+1)      

submission = pd.DataFrame({'ImageId': id, 'Label': predicted_values})
file_name = "digit_recogition_submission_" + str(len(predicted_values)) + '.csv' 
submission.to_csv(file_name, index=False)
