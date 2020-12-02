import os
import importlib


def auto_register_service():
    """
    auto register website service
    Returns:

    """
    service = WebProvider()
    # get path of crawler folder
    crawler_path = os.path.dirname(__file__)
    # get list of subdirectories name
    for folder_name in next(os.walk(crawler_path))[1]:
        folder_path_list = os.listdir(os.path.join(crawler_path, folder_name))
        modules = [x for x in folder_path_list if x.endswith('.py')]
        for module in modules:
            # import according folder name
            module_name = module.split('.', 1)[0]
            module_object = importlib.import_module(
                'crawler.' + folder_name + "." + module_name)
            # register module when class has 'title' attr
            module_class = getattr(module_object, module_name.capitalize())
            if hasattr(module_class, "title"):
                service.register_builder(module_name, module_class())
    return service


class WebProvider:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)

    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


# class WebProvider(ObjectFactory):
#     def get(self, service_id, *args):
#         return self.create(service_id, *args)
