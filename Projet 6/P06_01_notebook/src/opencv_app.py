import pandas as pd
import cv2
import numpy as np
from tqdm.notebook import tqdm
from sklearn import cluster, manifold, metrics, preprocessing
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
from .base_app import BaseImageWrapper, BaseModelWrapper, BaseApp


class ColorConverter:
    def __init__(self, color):
        self._color=color

    def apply(self, image):
        return cv2.cvtColor(image, self._color)


class NoiseFilter:
    def __init__(self, noise_type, noise_size):
        self._noise_type=noise_type
        self._noise_size=noise_size

    def apply(self, image):
        return cv2.medianBlur(image, self._noise_size)


class OpencvImageWrapper(BaseImageWrapper):
    # TODO Try with a noise filter
    _filters = [
        ColorConverter(cv2.COLOR_BGR2GRAY),
        cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)),
    ]

    def __init__(self, id, filename, label):
        self._id = id
        self._filename = filename
        self._label = label
        self._image = None

    def get_image(self):
        if self._image is None:
            _img = cv2.imread(str(self))
            assert(_img is not None)
            self._image = _img
        return self._image

    def get_filtered_image(self):
        _img = self.get_image()
        for _filter in self._filters:
            _img = _filter.apply(_img)
        return _img


class SiftWrapper(BaseModelWrapper):
    _sift = cv2.SIFT_create()
    
    def __init__(self, image_wrapper):
        self.image_wrapper = image_wrapper
        self._kp = None
        self._des = None
        self._hist = None

    def get_sift_features(self, with_filters=True):
        if self._kp is None:
            if with_filters:
                _img = self.image_wrapper.get_filtered_image()
            else:
                _img = self.image_wrapper.get_image()
            self._kp, self._des = self._sift.detectAndCompute(_img, None)
        return self._kp, self._des

    def get_histogram(self, model):
        _cls = model.predict(self._des)
        _n_features = len(self._kp)
        _unique_cls, _count_cls = np.unique(_cls, return_counts=True)
        self._hist = np.zeros(model.n_clusters, np.float32)
        for i in range(len(_unique_cls)):
            self._hist[_unique_cls[i]] = _count_cls[i] / _n_features
        return self._hist


class SiftApp(BaseApp):
    _image_wrapper_class = OpencvImageWrapper
    _model_wrapper_class = SiftWrapper

    def __init__(self, images, labels) -> None:
        super().__init__(images, labels)
        self.embedding_matrix = None
        self.kmean_model = None
        self.sift_wrapper = None
        self._n_clusters = len(set(labels.values()))
        print("number of images :", len(images), ", number of class :", self._n_clusters)

    def create_embedding_matrix(self, with_filters=True):
        print('Create sift wrapper...')
        self.sift_wrapper = self._model_wrapper_class.from_dict(self.images_wrapper)
        print('Detecting keypoints...')
        _ids = list(self.sift_wrapper.keys())
        self.embedding_matrix = np.empty((0, 128), np.float32)
        for i in tqdm(range(len(_ids))):
            _sift_wrapper = self.sift_wrapper[_ids[i]]
            _, _des = _sift_wrapper.get_sift_features(with_filters=True)
            self.embedding_matrix = np.append(self.embedding_matrix, _des, axis=0)

    def create_kmean_model(self, k=None, batch_size=None, verbose=False):
        if self.kmean_model is None:
            print('Creating kmean model...')
            if k is None:
                k = self._n_clusters * 10
            if batch_size is None:
                batch_size = max(len(self.sift_wrapper) * 3, 3072)
            print("k =", k, ", batch_size =", batch_size)
            self.kmean_model = cluster.MiniBatchKMeans(n_clusters=k, batch_size=batch_size, verbose=verbose)
            self.kmean_model.fit(self.embedding_matrix)

    def create_histogram(self):
        print('Make histogram...')
        _ids = list(self.sift_wrapper.keys())
        for i in tqdm(range(len(_ids))):
            _sift_wrapper = self.sift_wrapper[_ids[i]]
            _sift_wrapper.get_histogram(model=self.kmean_model)

    def get_histogram(self):
        return {k: v._hist for k, v in self.sift_wrapper.items()}

    def get_labels(self):
        return {k: v.image_wrapper._label for k, v in self.sift_wrapper.items()}

    def compute_ari(self, n_components=2, model=manifold.TSNE, model_kw={}):
        print(f"Computing ARI with {model.__name__}({n_components}d)...")
        _hist = pd.DataFrame.from_dict(self.get_histogram(), orient='index')
        _labels = pd.Series(self.get_labels(), name='labels')
        _n_labels = preprocessing.LabelEncoder().fit_transform(_labels.values)
        _reduc = model(n_components=n_components, **model_kw)
        _X = _reduc.fit_transform(_hist.values)
        _cls = cluster.KMeans(n_clusters=self._n_clusters, n_init=100, random_state=42)
        _cls.fit(_X)
        _ari = np.round(metrics.adjusted_rand_score(_n_labels, _cls.labels_), 4)
        print(f"ARI with {model.__name__}({n_components}): {_ari}")
        _res = pd.DataFrame(_X, columns=range(n_components), index=_hist.index)
        _res =_res.join(pd.Series(_cls.labels_, name='clusters', index=_hist.index))
        _res =_res.join(_labels)
        _res =_res.join(pd.Series(_n_labels, name='n_labels', index=_labels.index))
        return _res, _ari

    def plot_clustering(self, df, title=None):
        print('Plot clustering...')

        subplot_kw={}
        is_3d = 2 in df.columns
        subplot_kw['projection'] = '3d' if is_3d else None

        _, axs = plt.subplots(ncols=2, figsize=(30,15), subplot_kw=subplot_kw)

        cmap = ListedColormap(sns.color_palette("hls", self._n_clusters).as_hex())

        x = df.loc[:, 0].values
        y = df.loc[:, 1].values 
        c0 = df.loc[:, 'n_labels'].values
        c1 = df.loc[:, 'clusters'].values
        l0 = df[['labels', 'n_labels']].value_counts().reset_index().sort_values('n_labels')['labels'].to_list()
        
        if is_3d:
            z = df.loc[:, 2].values
            scatter0 = axs[0].scatter(xs=x, ys=y, zs=z, s=50, c=c0, cmap=cmap)
            scatter1 = axs[1].scatter(xs=x, ys=y, zs=z, s=50, c=c1, cmap=cmap)
        else:
            scatter0 = axs[0].scatter(x=x, y=y, s=50, c=c0, cmap=cmap)
            scatter1 = axs[1].scatter(x=x, y=y, s=50, c=c1, cmap=cmap)
        
        axs[0].legend(handles=scatter0.legend_elements()[0], labels=l0, loc="best", title="Categories")
        axs[0].set_title('Représentation des produits par catégories réelles')

        axs[1].legend(handles=scatter1.legend_elements()[0], labels=set(c1), loc="best", title="Labels")
        axs[1].set_title('Représentation des produits par clusters')

        if title:
            plt.suptitle(title, fontsize=20)
        plt.show()

    def plot_images(self, df, n_sample=25):
        print('Plot images with categories...')
        _df = df.sample(n=n_sample)
        _ids = list(_df.index)
        img_size = len(_ids)
        fig = plt.figure(figsize=(30, 30))
        for i in tqdm(range(img_size)):
            _id = _ids[i]
            _img = self.sift_wrapper[_id].image_wrapper._image
            _label = self.sift_wrapper[_id].image_wrapper._label
            _cluster = df.loc[_id, 'clusters']
            ax = fig.add_subplot(img_size//5+1, 5, (i+1))
            ax.imshow(_img)
            ax.axis('off')
            ax.set_title(f'{_label} ({_cluster})', fontsize=20)
        plt.show()

    
    def make_clustering(self, n_components=2, model=manifold.TSNE, model_kw={'perplexity': 30, 'n_iter': 2000, 'init': 'random', 'learning_rate': 200, 'random_state': 42}):
        print('Make clustering...')
        _df = self.compute_tsne_ari(n_components=n_components, model=model, model_kw=model_kw)
        self.plot_clustering_tsne(_df)
        self.plot_clustering_grid(_df)
