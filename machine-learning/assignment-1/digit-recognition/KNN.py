# implement KNN Classifier
class KNNeighborsClassifier:
    def __init__(self, k_neighbors, train_data, labels, test_data):
        self.k_neighbors = k_neighbors
        self.train_data = train_data
        self.labels = labels
        self.test_data = test_data
        return

    def get_neighbors(self, X):
        neighbors = []
        for idx1, point1 in enumerate(X): # for each matrix of pixels
            distances = []
            [distances.append((spatial.distance.euclidean(point1, point2), idx2)) for idx2, point2 in enumerate(X)]
            distances.sort(key=itemgetter(0)) # sort list of tuples based on key 0, or distance!
            nearest_neighbors = distances[1:self.k_neighbors+1] # remove 0 distance while comparing the same value
            neighbors.append(nearest_neighbors)
        return neighbors
    
    def get_neighbors(self, k, train, test_inst):
        neighbors = []
        for idx, point in enumerate(train):
            neighbors.append((spatial.distance.euclidean(point, test_inst), idx))
        neighbors.sort(key=itemgetter(0))
        return neighbors[:k]
    
    def classifier(self, nearest_neighbors, digit_labels):
        possible_classes = []
        for neighbor in nearest_neighbors:
            possible_classes.append(digit_labels[neighbor[1]])

        return max(set(possible_classes), key=possible_classes.count)

    def predict(self, test_data):
        predicted_digits = []
        for test_instance in test_data:
            neighbors = self.get_neighbors(self.k_neighbors, self.train_data, test_instance)
            predicted_digits.append(self.classifier(neighbors, self.labels))
        return predicted_digits     
