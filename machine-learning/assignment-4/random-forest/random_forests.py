from sklearn.ensemble import RandomForestRegressor as RF
from sklearn.neighbors import KNeighborsRegressor as KNN
from sklearn import cross_validation as cv, tree
import matplotlib.pyplot as plt
import skimage as skim
from PIL import Image
import numpy as np
get_ipython().magic(u'matplotlib inline')

MONA_PATH = "data/mona_lisa.jpg"

mona = Image.open(MONA_PATH)
plt.imshow(mona)

# b
width, height = mona.size

TRAIN_COORDINATES = []
while len(TRAIN_COORDINATES) < 5000:
    rand_point = (np.random.randint(width), np.random.randint(height))
    if not rand_point in TRAIN_COORDINATES:
        TRAIN_COORDINATES.append(rand_point)

# c
# weighted grayscale converter
def rgb_to_grayscale(R, G, B):
    return R * 0.2989 + G * 0.5870 + B * 0.1140
# built in grayscale conversion
gray_mona = mona.convert('LA')
plt.imshow(gray_mona)

# not necessary
# RESCALED_PIXELS = np.array(POST_PIXELS) / 255

# using our rgb_to_grayscale function
# mona_pixels = mona.load()
# POST_PIXELS = []
# for pixel in TRAIN_COORDINATES:
#     r, g, b = mona_pixels[pixel[0], pixel[1]]
#     POST_PIXELS.append(rgb_to_grayscale(r, g, b))

mona_pixels_gray = gray_mona.load()
POST_PIXELS = []
for pixel in TRAIN_COORDINATES:
    grayscale, pixel_range = mona_pixels_gray[pixel[0], pixel[1]]
    POST_PIXELS.append(grayscale)

TEST = [(y, x) for x in range(height) for y in range(width)]

def rand_forest(num_trees, depth):    
    rf = RF(n_estimators=num_trees, max_depth=depth)
    rf.fit(TRAIN_COORDINATES, POST_PIXELS)
    prediction = rf.predict(TEST)
    a = np.array(prediction).reshape(height, width)
    print num_trees, " decision trees with max depth ", depth
    plt.imshow(a, cmap="gray")
    plt.show()

rand_forest(10, None)

max_depths = [1,2,3,5,10,15]
for max_depth in max_depths:
    rand_forest(1, max_depth)

num_trees = [1, 3, 5, 10, 100]
for num_tree in num_trees:
    rand_forest(num_tree, 7)

knn = KNN(n_neighbors=1)
knn.fit(TRAIN_COORDINATES, POST_PIXELS)
prediction_knn = knn.predict(TEST)

a = np.array(prediction_knn).reshape(height, width)
plt.imshow(a, cmap="gray")

rand_forest(10, 15)
rand_forest(100, None)

# cross validation, k = 10 for pruning
prune_trees = [10, 25, 50, 100, 1000]
prune_depth = [10, 25, 50, 100, None]
best_accuracy = -1
best_prune = (-1, -1)

for tree in prune_trees:
    for depth in prune_depth:
        rf = RF(n_estimators=tree, max_depth=depth)
        score = cv.cross_val_score(rf, TRAIN_COORDINATES, POST_PIXELS, cv=10).mean()
        print (tree, depth), score
        if score > best_accuracy:
            best_accuracy = score
            best_prune = (tree, depth)

print "Highest Consistent Accuracy: {0} with {1}".format(best_accuracy, best_prune)

# saving random decision tree
rf = RF(n_estimators=100, max_depth=None)
rf.fit(TRAIN_COORDINATES, POST_PIXELS)
with open('decision_tree.dot', 'w') as my_file:
    my_file = tree.export_graphviz(rf.estimators_[0], out_file = my_file)
