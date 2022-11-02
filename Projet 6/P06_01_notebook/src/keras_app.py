import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
from sklearn import cluster, manifold, metrics, preprocessing
from tensorflow import keras
from keras.preprocessing.image import load_img, img_to_array
from .base_app import BaseImageWrapper, BaseModelWrapper, BaseApp
import seaborn as sns
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt


class KerasImageWrapper(BaseImageWrapper):
    def __init__(self, id, filename, label):
        self._id = id
        self._filename = filename
        self._label = label
        self._image = None

    def get_image(self, target_size=None):
        if self._image is None:
            # load an image from file
            _img = load_img(str(self), target_size=target_size)
            assert(_img is not None)
            self._image = _img
        return self._image


class ModelWrapper(BaseModelWrapper):
    base_model = keras.applications.VGG16()
    model = None

    def __init__(self, image_wrapper):
        self.image_wrapper = image_wrapper
        self._resized_image = None
        self._features = None

    def get_resized_image(self, target_size=None):
        if self._resized_image is None:
            # get loadded image
            _img = self.image_wrapper.get_image(target_size=target_size)
            # convert the image pixels to a numpy array
            _img = img_to_array(_img)
            # reshape data for the model
            _img = _img.reshape((1, _img.shape[0], _img.shape[1], _img.shape[2]))
            # prepare the image for the VGG model
            _img = keras.applications.imagenet_utils.preprocess_input(_img)
            self._resized_image = _img
        return self._resized_image

    def get_features(self, force_reload=False):
        assert(self._resized_image is not None)
        if self._features is None or force_reload:
            self._features = self.model.predict(self._resized_image)
            self._features = self._features.flatten()
        return self._features

class VggWrapper(ModelWrapper):
    base_model = keras.applications.VGG16()
    model = keras.Model(inputs=base_model.inputs, outputs=base_model.layers[-2].output)


class InceptionWrapper(ModelWrapper):
    base_model = keras.applications.InceptionV3()
    model = keras.Model(inputs=base_model.inputs, outputs=base_model.layers[-2].output)


class ResNetWrapper(ModelWrapper):
    base_model = keras.applications.ResNet50V2()
    model = keras.Model(inputs=base_model.inputs, outputs=base_model.layers[-2].output)


class KerasApp(BaseApp):
    _image_wrapper_class = KerasImageWrapper

    def __init__(self, images, labels, model_wrapper_class) -> None:
        super().__init__(images, labels)
        self._n_clusters = len(set(labels.values()))
        self.model_wrapper = None
        self._model_wrapper_class = model_wrapper_class
        print("number of images :", len(images), ", number of class :", self._n_clusters)

    def preprocess_images(self, target_size=(224, 224)):
        print(f"Create {self._model_wrapper_class.__name__} wrapper...")
        self.model_wrapper = self._model_wrapper_class.from_dict(self.images_wrapper)
        print('Preprocess images...')
        _ids = list(self.model_wrapper.keys())
        for i in tqdm(range(len(_ids))):
            _model_wrapper = self.model_wrapper[_ids[i]]
            _model_wrapper.get_resized_image(target_size=target_size)

    def process_features(self, force_reload=False):
        print('Process features...')
        _ids = list(self.model_wrapper.keys())
        for i in tqdm(range(len(_ids))):
            _model_wrapper = self.model_wrapper[_ids[i]]
            _model_wrapper.get_features(force_reload=force_reload)

    def get_labels(self):
        return pd.Series({k: v.image_wrapper._label for k, v in self.model_wrapper.items()}, name='labels')

    def get_resized_images(self):
        return {k: v._resized_image for k, v in self.model_wrapper.items()}

    def get_model_features(self):
        return pd.DataFrame.from_dict({k: v._features for k, v in self.model_wrapper.items()}, orient='index')

    def make_base_clustering(self, verbose=False):
        print('Make clustering (without train model)...')
        _ids = list(self.model_wrapper.keys())
        for i in tqdm(range(len(_ids))):
            _model_wrapper = self.model_wrapper[_ids[i]]
            _res = _model_wrapper.base_model.predict(_model_wrapper._resized_image)
            from keras.applications.vgg16 import decode_predictions
            if verbose:
                print('Best :', decode_predictions(_res, top=1)[0])

    def compute_ari(self, n_components=2, model=manifold.TSNE, model_kw={}):
        print(f"Computing ARI with {model.__name__}({n_components}d)...")
        _feat = self.get_model_features()
        _labels = self.get_labels()
        _n_labels = preprocessing.LabelEncoder().fit_transform(_labels.values)
        _reduc = model(n_components=n_components, **model_kw)
        _X = _reduc.fit_transform(_feat.values)
        _cls = cluster.KMeans(n_clusters=self._n_clusters, n_init=100, random_state=42)
        _cls.fit(_X)
        _ari = np.round(metrics.adjusted_rand_score(_n_labels, _cls.labels_), 4)
        print(f"ARI with {model.__name__}({n_components}): {_ari}")
        _res = pd.DataFrame(_X, columns=range(n_components), index=_feat.index)
        _res =_res.join(pd.Series(_cls.labels_, name='clusters', index=_feat.index))
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
            _img = self.model_wrapper[_id].image_wrapper._image
            _label = self.model_wrapper[_id].image_wrapper._label
            _cluster = df.loc[_id, 'clusters']
            ax = fig.add_subplot(img_size//5+1, 5, (i+1))
            ax.imshow(_img)
            ax.axis('off')
            ax.set_title(f'{_label} ({_cluster})', fontsize=20)
        plt.show()
