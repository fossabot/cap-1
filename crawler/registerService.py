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
    # 搜索二级目录中 py 文件
    modules = sum([list(folder.glob('*.py')) for folder in Path.cwd().iterdir()], [])
    for module in modules:
        # eg. crawler.javbus.javbus
        module_object = import_module('crawler.' + module.parent.name + '.' + module.stem)
        # eg. <class 'crawler.javbus.javbus.JavbusBuilder'>
        try:
            module_class = getattr(module_object, module.stem.capitalize() + 'Builder')
            service.register_builder(module.stem, module_class())
        except AttributeError as e:
            logger.error(f'error import builder class:{e}')
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
