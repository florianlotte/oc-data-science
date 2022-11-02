from tqdm.notebook import tqdm


class BaseImageWrapper:
    _path = './data/Flipkart/Images/'

    def get_image(self):
        raise NotImplementedError

    def __str__(self):
        return self._path + self._filename

    @classmethod
    def from_dict(cls, image_list, label_list):
        _res = {}
        _ids = list(image_list.keys())
        for i in tqdm(range(len(_ids))):
            _id = _ids[i]
            _filename = image_list[_id]
            _label = label_list[_id]
            try:
                _cls = cls(_id, _filename, _label)
                _res[_id] = _cls
            except Exception as e:
                print("error:", _id, _filename)
        return _res


class BaseModelWrapper:
    @classmethod
    def from_dict(cls, image_wrapper_dict, *args, **kwargs):
        _res = {}
        _ids = list(image_wrapper_dict.keys())
        for i in tqdm(range(len(_ids))):
            _id = _ids[i]
            _image_wrapper = image_wrapper_dict[_id]
            try:
                _cls = cls(_image_wrapper, *args, **kwargs)
                _res[_id] = _cls
            except Exception as e:
                print("error:", str(_image_wrapper))
        return _res


class BaseApp:
    _image_wrapper_class = None

    def __init__(self, images, labels) -> None:
        print('Loading images...')
        self.images_wrapper = self._image_wrapper_class.from_dict(images, labels)

    def make_clustering(self):
        raise NotImplementedError