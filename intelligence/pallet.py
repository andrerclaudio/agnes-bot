# Added modules
import numpy as np
import scipy
from sklearn.cluster import KMeans
from concurrent.futures import ProcessPoolExecutor
# from functools import lru_cache
from sklearn.metrics import silhouette_score
from PIL import Image

NUM_WORKERS = 2  # Number of parallel workers


# Use KMeans instead of MiniBatchKMeans for faster approximate clustering

def calculate_optimal_clusters(data, min_clusters=5, max_clusters=10):
    scores = []
    for n_clusters in range(min_clusters, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters, random_state=1000, n_init=3)
        kmeans.fit(data)
        score = silhouette_score(data, kmeans.labels_)
        scores.append((n_clusters, score))
    return scores


# @lru_cache(maxsize=None)  # Cache the dominant_colors function results
def dominant_colors(image_path, min_clusters=5, max_clusters=10, target_size=(150, 150)):
    image = Image.open(image_path)  # Open the image from the path

    # Resize the image to the target size
    image = image.resize(target_size)

    ar = np.asarray(image)
    shape = ar.shape
    ar = ar.reshape(np.prod(shape[:2]), shape[2]).astype(float)

    # Calculate optimal number of clusters in parallel
    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        results = [executor.submit(calculate_optimal_clusters, ar, min_clusters, max_clusters) for _ in
                   range(NUM_WORKERS)]

    final_scores = []
    for result in results:
        final_scores.extend(result.result())

    best_clusters = max(final_scores, key=lambda x: x[1])[0]

    kmeans = KMeans(
        n_clusters=best_clusters,
        init="k-means++",
        random_state=1000,
        n_init=3
    ).fit(ar)
    codes = kmeans.cluster_centers_

    vecs, _dist = scipy.cluster.vq.vq(ar, codes)  # assign codes
    counts, _bins = np.histogram(vecs, len(codes))  # count occurrences

    colors = []
    for index in np.argsort(counts)[::-1]:
        colors.append(tuple([int(code) for code in codes[index]]))

    return colors  # returns colors in order of dominance
