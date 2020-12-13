# import random

from crawler.crawlerComm import (
    CrawlerBase,
    # GoogleSearch,
    call
)
from utils.logger import setup_logger

logger = setup_logger()


class Rarbg(CrawlerBase):
    _url = []

    def __init__(self, number, cfg):
        super().__init__(cfg)

    def search_url(self):
        ...

    @call
    def smallcover(self):
        ...

    @call
    def outline(self):
        ...

    @call
    def info(self):
        ...


class RarbgBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Rarbg(number, cfg)
            for method in dir(self._instance):
                fun = getattr(self._instance, method)
                if getattr(fun, "is_callable", False):
                    fun()
        return self._instance.data


if __name__ == "__main__":
    # for test
    # pass
    from utils.config import get_cfg_defaults

    cfgs = get_cfg_defaults()
    jav = RarbgBuilder()
    j = jav("ABP-454", cfgs)
    print(j)
