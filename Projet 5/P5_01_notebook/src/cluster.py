from tkinter import N
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn import cluster
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn import preprocessing
from sklearn import metrics
from sklearn.neighbors import kneighbors_graph


class dataHelper:
    def __init__(self, df, limit=None):
        if limit is not None:
            self.dataframe = df.sample(n=limit, ignore_index=True).copy()
        else:
            self.dataframe = df.copy()
        self.data_scaled = None
        self.data_reduced = None
        self.scaler = None
        self.pca = None
        self.cluster_helper = []

    ###############################################################################
    # SCALER
    ###############################################################################
    def get_data_scaled(self):
        if self.scaler is None or self.data_reduced is None:
            self.scale()
        return self.data_scaled

    def get_scaler(self):
        if self.scaler is None or self.data_reduced is None:
            self.scale()
        return self.scaler

    def scale(self):
        self.scaler = StandardScaler()
        self.data_scaled = self.scaler.fit_transform(self.dataframe)

    ###############################################################################
    # PCA
    ###############################################################################
    def get_data_reduced(self):
        if self.pca is None or self.data_reduced is None:
            self.reduce_dim()
        return self.data_reduced

    def get_pca(self):
        if self.pca is None or self.data_reduced is None:
            self.reduce_dim()
        return self.pca

    def reduce_dim(self, dim=2):
        self.pca = PCA(n_components=dim)
        self.data_reduced = self.pca.fit_transform(self.get_data_scaled())


class clusterHelper:
    def __init__(self, data):
        self.data = data
        self.models = {}

    ###############################################################################
    # Clustering
    ###############################################################################
    def make_clusters(self, nx, params={}):
        for n in nx:
            self.make_model(n, params)

    def make_model(self, n, params={}):
        raise NotImplementedError()

    def get_cluster_labels(self, n):
        if n not in self.models.keys():
            raise ValueError("Model not found")
        return np.array(self.models[n].labels_)

    def get_cluster_unique_labels(self, n):
        return np.unique(self.get_cluster_labels(n=n))

    def get_color_by_unique_labels(self, n):
        labels = self.get_cluster_labels(n)
        unique_labels = self.get_cluster_unique_labels(n)
        le = preprocessing.LabelEncoder()
        encoded_unique_labels = le.fit_transform(unique_labels)
        colors = cm.nipy_spectral(encoded_unique_labels.astype(float) / len(unique_labels))
        return colors

    def get_color_by_labels(self, n):
        labels = self.get_cluster_labels(n)
        unique_labels = self.get_cluster_unique_labels(n)
        le = preprocessing.LabelEncoder()
        encoded_labels = le.fit_transform(labels)
        colors = cm.nipy_spectral(encoded_labels.astype(float) / len(unique_labels))
        return colors

    ###############################################################################
    # Ploting
    ###############################################################################
    def plot_results(self, nx, ax=None, figsize=(25, 10)):
        for n in nx:
            self.plot_result(n=n, ax=ax, figsize=figsize)

    def plot_result(self, n, ax=None, figsize=(10, 10)):
        raise NotImplementedError()

    def plot_silhouette(self, n, ax=None, figsize=(10, 10)):
        data_scaled = self.data.get_data_scaled()
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        labels = self.get_cluster_labels(n)
        unique_labels = self.get_cluster_unique_labels(n)

        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax.set_xlim([-0.1, 1])
        # The (n+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax.set_ylim([0, len(data_scaled) + (len(unique_labels) + 1) * 10])

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(data_scaled, labels)
        print("For", n, "clusters, The average silhouette_score is :", silhouette_avg)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(data_scaled, labels)

        y_lower = 10
        colors = self.get_color_by_unique_labels(n)
        for i, k in enumerate(unique_labels):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = sample_silhouette_values[labels == k]
            ith_cluster_silhouette_values.sort()
            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            ax.fill_betweenx(
                np.arange(y_lower, y_upper),
                0,
                ith_cluster_silhouette_values,
                facecolor=colors[i],
                edgecolor=colors[i],
                alpha=0.7,
            )

            # Label the silhouette plots with their cluster numbers at the middle
            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, k)

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax.set_title("The silhouette plot for the various clusters.")
        ax.set_xlabel("The silhouette coefficient values")
        ax.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax.set_yticks([])  # Clear the yaxis labels / ticks
        ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    def plot_scatter(self, n, ax=None, figsize=(10, 10)):
        data_reduced = self.data.get_data_reduced()
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        # 2nd Plot showing the actual clusters formed
        colors = self.get_color_by_labels(n=n)
        ax.scatter(
            data_reduced[:, 0], data_reduced[:, 1], marker=".", s=30, lw=0, alpha=0.7, c=colors, edgecolor="k"
        )

        if hasattr(self.models[n], 'cluster_centers_'):
            # Labeling the clusters
            centers = self.models[n].cluster_centers_
            reduced_centers = self.data.get_pca().transform(centers)
            # Draw white circles at cluster centers
            ax.scatter(reduced_centers[:, 0], reduced_centers[:, 1], marker="o", c="white", alpha=1, s=200, edgecolor="k")

            for i, c in enumerate(reduced_centers):
                ax.scatter(c[0], c[1], marker="$%d$" % i, alpha=1, s=50, edgecolor="k")

        ax.set_title("The visualization of the clustered data.")
        ax.set_xlabel("Feature space for the 1st feature")
        ax.set_ylabel("Feature space for the 2nd feature")

    def plot_elbow(self, ax=None, figsize=(10, 10)):
        plt.figure(figsize=figsize)
        distortions = []
        for n in self.models.keys():
            distortions.append(self.models[n].inertia_)
            print("For n_clusters =", n, "The average distortion is :", self.models[n].inertia_)
        plt.plot(self.models.keys(), distortions, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method showing the optimal k')

    def plot_relationship(self, n, columns=None, ax=None, figsize=(10, 10)):
        _df = pd.DataFrame(data=self.data.get_data_scaled(), columns=self.data.dataframe.columns)
        _df['labels'] = self.get_cluster_labels(n=n)
        sns.pairplot(_df, hue='labels', diag_kind='hist', palette='tab10', height=5)


class kmeanHelper(clusterHelper):
    model_class = cluster.KMeans

    ###############################################################################
    # Clustering
    ###############################################################################
    def make_clusters(self, nx, params={'random_state': 0}):
        super(kmeanHelper, self).make_clusters(nx=nx, params=params)

    def make_model(self, n, params={'random_state': 0}):
        print("Making clusters:", n)
        self.models[n] = self.model_class(n_clusters=n, **params).fit(self.data.get_data_scaled())

    ###############################################################################
    # Ploting
    ###############################################################################
    def plot_result(self, n, ax=None, figsize=(25, 10)):
        if ax is None:
            _, axs = plt.subplots(1, 2, figsize=figsize)

        self.plot_silhouette(n=n, ax=axs[0])
        self.plot_scatter(n=n, ax=axs[1])

        plt.suptitle(
            "Silhouette analysis for KMeans clustering on data with n_clusters = %d"
            % n, fontsize=14, fontweight="bold",
        )


class dbscanHelper(clusterHelper):
    model_class = cluster.DBSCAN

    ###############################################################################
    # Clustering
    ###############################################################################
    def make_clusters(self, nx, params={}):
        super(dbscanHelper, self).make_clusters(nx=nx, params=params)

    def make_model(self, n, params={}):
        print("Making clusters:", n)
        self.models[n] = self.model_class(**params).fit(self.data.get_data_scaled())
        # Number of clusters in labels, ignoring noise if present.
        labels = self.get_cluster_labels(n=n)
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise_ = list(labels).count(-1)
        print("For", n, "clusters, Estimated number of clusters: %d" % n_clusters_)
        print("For", n, "clusters, Estimated number of noise points: %d" % n_noise_)

    ###############################################################################
    # Specific Ploting
    ###############################################################################
    def plot_result(self, n, ax=None, figsize=(25, 10)):
        if ax is None:
            _, axs = plt.subplots(1, 2, figsize=figsize)

        self.plot_silhouette(n=n, ax=axs[0])
        self.plot_scatter(n=n, ax=axs[1])

        plt.suptitle(
            "Silhouette analysis for %s clustering"
            % n, fontsize=14, fontweight="bold",
        )


class agglomerativeClusturingHelper(clusterHelper):
    model_class = cluster.AgglomerativeClustering

    ###############################################################################
    # Clustering
    ###############################################################################
    def make_clusters(self, nx, params={}):
        super(agglomerativeClusturingHelper, self).make_clusters(nx=nx, params=params)

    def make_model(self, n, params={}):
        print("Making clusters:", n)
        self.models[n] = self.model_class(n_clusters=n, **params).fit(self.data.get_data_scaled())

    ###############################################################################
    # Specific Ploting
    ###############################################################################
    def plot_result(self, n, ax=None, figsize=(25, 10)):
        if ax is None:
            _, axs = plt.subplots(1, 2, figsize=figsize)

        self.plot_silhouette(n=n, ax=axs[0])
        self.plot_scatter(n=n, ax=axs[1])

        plt.suptitle(
            "Silhouette analysis for AgglomerativeClustering clustering on data with n_clusters = %d"
            % n, fontsize=14, fontweight="bold",
        )
    
    def plot_dendrogram(self, n=0, ax=None, figsize=(10, 10)):
        model = self.models[n]

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        # create the counts of samples under each node
        counts = np.zeros(model.children_.shape[0])
        n_samples = len(model.labels_)
        for i, merge in enumerate(model.children_):
            current_count = 0
            for child_idx in merge:
                if child_idx < n_samples:
                    current_count += 1  # leaf node
                else:
                    current_count += counts[child_idx - n_samples]
            counts[i] = current_count

        linkage_matrix = np.column_stack(
            [model.children_, model.distances_, counts]
        ).astype(float)

        # Plot the corresponding dendrogram
        dendrogram(linkage_matrix, truncate_mode="level", p=3)
