import re

from crawler.crawlerCommon import CrawlerCommon
from utils.logger import setup_logger

logger = setup_logger()


class Javstore(CrawlerCommon):
    """
    for fc2

    """
    _url = ["https://javstore.net/"]

    def __init__(self, number, cfg):
        super().__init__(cfg)

        res = self.search_link_by_google(number, self._url[0])
        if res is not None:
            self.html = res
        else:
            search_url = self._url[0] + 'search?q=' + number + '&f=all'
            self.html = self.search(number, search_url, '', '', '')

    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
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
                self.data.publisher = re.sub(r'[販売日|\s]', '', i)
            if '再生時間' in i:
                self.data.runtime = re.sub(r'[再生時間|\s]', '', i)

    def get_data(self, instance):
        """
        运行类中所有不带下划线的方法，返回数据
        """
        for _key, _fun in instance.__dict__.items():
            if type(_fun).__name__ == 'function' and "_" not in _key:
                _fun(self)
        return self.data


class JavstoreBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Javstore(number, cfg)
        return self._instance.get_data(Javstore)


if __name__ == "__main__":
    # for test
    # pass
    from core.cli import get_cfg_defaults

    cfgs = get_cfg_defaults()
    jav = Javstore("FC2-749704", cfgs)
    data = jav.get_data(Javstore)
    print(data.title)
    print(data.img_url)
    print(data.text)
