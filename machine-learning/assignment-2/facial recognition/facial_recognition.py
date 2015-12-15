# Note: converted from .ipynb format
from matplotlib import pylab as plt
from sklearn import linear_model
import matplotlib.cm as cm
from scipy import misc
import numpy as np
import scipy as sp
get_ipython().magic(u'matplotlib inline')

TRAIN_PATH = "data/train.txt"
TEST_PATH = "data/test.txt"

def parse_data(data_set_path):
    data, labels = [], []
    for line in open(data_set_path):
        im = misc.imread(line.strip().split()[0])
        data.append(im.reshape(2500,))
        labels.append(line.strip().split()[1])
    data, labels = np.array(data, dtype=float), np.array(labels, dtype=int)
    return (data, labels)

def display_image(image):
    plt.imshow(image.reshape(50,50), cmap = cm.Greys_r)
    plt.show()

# B. Download and parse the train and test data sets
train_data, train_labels = parse_data(TRAIN_PATH)
test_data, test_labels = parse_data(TEST_PATH)

# Display an aribitrary image from the data set
display_image(train_data[19, :])

# C. Compute and display the average face
sum_face = np.sum(train_data, axis=0)
total_faces = len(train_data)
average_face = np.divide(sum_face, total_faces)

display_image(average_face)

# D. Compute mean subtraction
def get_mean_sub(data_set, average_face):
    mean_sub = []
    for x in data_set:
        mean_sub.append(np.diff([x,average_face], axis=0).flatten())
    return mean_sub

train_mean_sub = get_mean_sub(train_data, average_face)
test_mean_sub = get_mean_sub(test_data, average_face)

display_image(train_mean_sub[19]) # display arbitrary image

# E. Compute Eigenfaces
u, s, v = sp.linalg.svd(np.asmatrix(train_mean_sub))

# Display first 10 Eigenfaces
for eig in v[:10]: display_image(eig)

def rank_r_approx(u, s, v, r):
    sigma = sp.linalg.diagsvd(s, len(u), len(v)) # Reconstruct sigma from singular value
    x = (u[:,:r]).dot(sigma[:r,:r]).dot(v[:r,:])
    return x

low_rank_approx = {}
for r in range(1,201):
    low_rank_approx[r] = rank_r_approx(u, s, v, r)

def compute_approx_error(x, xr):
    return np.linalg.norm(np.subtract(x, xr))

approx_error = {}
for r in range(1,201):
    approx_error[r] = compute_approx_error(train_mean_sub, low_rank_approx[r])

def plot_approx_error(r, error):
    plt.scatter(r, error, c='g', alpha=0.5)
    plt.title('Rank r Approximation Error')
    plt.xlabel('r')
    plt.ylabel('Frobenius Norm')
    plt.show()
    return

plot_approx_error(approx_error.keys(), approx_error.values())

# G. Eigenface Feature
def eigdenface_feature(x, v, r):
    vt = np.transpose(v[:r,:])
    f = x.dot(vt)
    return f

f_train, f_test = {}, {}

for r in range(1,201):
    f_train[r] = eigdenface_feature(np.asmatrix(train_mean_sub), v, r)
    f_test[r] = eigdenface_feature(np.asmatrix(test_mean_sub), v, r)

def classify(f_train, train_labels, f_test, test_labels, r):    
    # Fit the model using logistic regression
    lr = linear_model.LogisticRegression(random_state=1).fit(f_train, train_labels)
    
    # Predict using test set
    predicted_values = lr.predict(f_test)
    accuracy = (predicted_values == test_labels).sum() / float(len(test_labels))    
    return accuracy

accuracy = {}
for r in range(1,201):
    accuracy[r] = classify(f_train[r], train_labels, f_test[r], test_labels, r)

def plot_prediction_accuracy(x, y):
    plt.scatter(x, y, c='g', alpha=0.5)
    plt.title('Logistic Regression')
    plt.xlabel('r')
    plt.ylabel('Prediction Accuracy')
    plt.xlim(0,200)
    plt.show()

plot_prediction_accuracy(accuracy.keys(), accuracy.values())
