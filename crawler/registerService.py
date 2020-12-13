from importlib import import_module
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger()


def auto_register_service():
    """
    auto register website service
    Returns:

    """
    service = WebProviderRegister()
    # 搜索二级目录中 py 文件 （Path.cwd()似乎得到的是main文件地址）
    modules = sum(
        [list(folder.glob("*.py"))
         for folder in Path(__file__).parent.iterdir()], []
    )
    for module in modules:
        # eg. crawler.javbus.javbus
        module_object = import_module(
            "crawler." + module.parent.name + "." + module.stem
        )
        # eg. <class 'crawler.javbus.javbus.JavbusBuilder'>
        try:
            module_class = getattr(
                module_object, module.stem.capitalize() + "Builder")
            service.register_service(module.stem, module_class())
        except AttributeError as e:
            logger.error(f"error import builder class:{e}")
    return service


class WebProviderRegister:
    def __init__(self):
        self._services = {}

    def register_service(self, key, builder):
        self._services[key] = builder

    def create(self, key, *args, **kwargs):
        builder = self._services.get(key)
        if not builder:
            raise ValueError(key)
        return builder(*args, **kwargs)

    def get(self, service_id, *args, **kwargs):
        return self.create(service_id, *args, **kwargs)
