class KMeans:   
    
    def __init__(self, k_clusters = 2, max_iterations = 1000):
        self.k_clusters = k_clusters
        self.max_iterations = max_iterations
        return
        
    def fit(self, X):
        self.X = X
        centroids = self.get_initial_centroids(X)
        old_centroids = []
        
        iteration = 0
        while not np.array_equal(centroids, old_centroids) and iteration < self.max_iterations:
            old_centroids = centroids.copy() # must copy list, not assign
            # cluster points to nearest centroid
            clusters, labels = self.clusters(centroids)
            # update centroid
            centroids = self.update_centroids(centroids, clusters)
            iteration += 1            
        return centroids, clusters, labels

    def get_initial_centroids(self, X):
        centroids = []
        for i in range(0, self.k_clusters):
            centroids.append(X['feature'][np.random.randint(0, len(X))])
        return np.array(centroids)
    
    # creates clusters of points nearest to centroids
    def clusters (self, centroids):
        clusters = [[] for i in range(self.k_clusters)]
        labels = [[] for i in range(self.k_clusters)]
        for idx, x in self.X.iterrows():
                min_dist = sys.maxint
                kth_idx = -1
                for idx2, centroid in enumerate(centroids):
                    dist = spatial.distance.euclidean(x['feature'], centroid)
                    if dist < min_dist:
                        min_dist = dist
                        kth_idx = idx2
                clusters[kth_idx].append(x['feature'])
                labels[kth_idx].append(x['label'])
        return clusters, labels

    def update_centroids(self, centroids, clusters):
        for idx, cluster in enumerate(clusters):
            if cluster == []:
                raise Exception('Empty cluster, try different centroid initialization')
            centroids[idx] = np.array(cluster).sum(axis=0) / float(len(cluster))
        return centroids
