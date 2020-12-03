from importlib import import_module
from pathlib import Path
from utils.logger import Logger
logger = Logger()


def auto_register_service():
    """
    auto register website service
    Returns:

    """
    service = WebProvider()
    cwd = Path.cwd()
    # 获取二级目录地址
    folder_path_list = [path for path in cwd.iterdir() if path.is_dir()]
    # 搜索二级目录中 py 文件
    modules = sum([list(folder.glob('*.py')) for folder in folder_path_list], [])
    for module in modules:
        # 文件名称，去除后缀
        module_name = module.name.split('.')[0]
        # eg. crawler.javbus.javbus
        module_object = import_module('crawler.' + module.parent.name + "." + module_name)
        # eg. <class 'crawler.javbus.javbus.JavbusBuilder'>
        try:
            module_class = getattr(module_object, module_name.capitalize() + 'Builder')
            service.register_builder(module_name, module_class())
        except AttributeError as e:
            logger.error('error import builder class:{}'.format(e))
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
