import re

from crawler.crawlerCommon import (
    CrawlerCommon,
    GoogleSearch,
    call
)
from utils.logger import setup_logger

logger = setup_logger()


class Javstore(CrawlerCommon):
    """
    for fc2

    """
    _url = "https://javstore.net"

    def __init__(self, number, cfg):
        super().__init__(cfg)
        # test
        logger.debug(f'search {number} by javstore')
        google = GoogleSearch(cfg)
        url = google.search(number, self._url.replace('https://', ''))

        if url is not None:
            self.html = self.get_parser_html(url)
        else:
            ...
            # search_url = self._url[0] + '/search?q=' + number + '&f=all'
            # self.html = self.search(number, search_url, '', '', '')

    @call
    def info(self):
        """
        number, release, length, director, studio
        """

        parents = self.html.xpath('//div[@class="news"]')[0]

        self.data.title = parents.xpath('div[@class="Recipepod"]/img/@title')
        self.data.cover = parents.xpath('div[@class="Recipepod"]/img/@src')

        texts = parents.xpath('text()')
        st = [t.strip() for t in texts if re.search(r'[\S]', t)]
        for i in st:
            if '販売日' in i:
                self.data.release = re.sub(r'[販売日|\s]', '', i)
            if '販売者' in i:
                self.data.publisher = re.sub(r'[販売者|\s]', '', i)
            if '再生時間' in i:
                self.data.runtime = re.sub(r'[再生時間|\s]', '', i)


class JavstoreBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Javstore(number, cfg)
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
    jav = Javstore("FC2-749704", cfgs)
    print(jav.data)
