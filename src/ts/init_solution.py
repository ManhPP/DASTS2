import numpy as np
from sklearn.cluster import KMeans


def init(inp, config):
    solution = []
    coordinates_matrix = np.loadtxt(config.data_path, skiprows=2)[:, :2]

    C1 = inp["C1"]
    X = []
    for i in C1:
        X.append(coordinates_matrix[i])

    num_cluster = min(config.params.num_staff, max(2, config.params.num_staff / 2))
    if 2 <= num_cluster <= len(C1):
        kmeans = KMeans(n_clusters=num_cluster, random_state=0).fit(np.array(X))
        clusters = kmeans.labels_
    else:
        clusters = [0] * len(C1)

    cus2lab = {}
    for i in range(1, inp['num_cus'] + 1):
        cus2lab[i] = inp['tau'][0, i]

    sorted_cus = [i for i, _ in sorted(cus2lab.items(), key=lambda x: x[1])]

    return solution
