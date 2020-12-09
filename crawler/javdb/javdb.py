import random

from requests import Response

from crawler.crawlerCommon import CrawlerCommon
from utils.logger import Logger

logger = Logger()


class Javdb(CrawlerCommon):
    _url = ["https://javdb.com/",
            "https://javdb4.com/",
            "https://javdb6.com/"
            ]

    def __init__(self, number, cfg):
        super().__init__(cfg)

        res = self.search_link_by_google(number, self._url)
        if res is not None:
            self.html = res
        else:
            url = random.choice(self._url)
            search_url = url + 'search?q=' + number + '&f=all'
            url_xpath = '//div[@class="grid-item column"]/a/@href'
            id_xpath = '//div[@class="grid-item column"]/a/div[contains(@class, "uid")]/text()'
            self.html = self.search(number, search_url, '', url_xpath, id_xpath)

    def _get(self, url: str, params: dict = None, **kwargs) -> Response:
        self.session.headers.update(
            {
                'Cookie': self.cfg.request.javbd_cookie,
                'referer': 'https://javdb.com/'
            }
        )
        response = self.session.get(url, timeout=self.timeout, params=params, **kwargs)
        response.encoding = 'utf-8'
        return response

    def title(self):
        """
        title
        """
        self.data.title = str(self.html.xpath('//h2[@class="title is-4"]/strong/text()'))

    def smallcover(self):
        pass

    def cover(self):
        try:
            self.data.cover = self.html.xpath('//img[@class="video-cover"]/@src')[0]
        except IndexError:
            self.data.cover = ""

    def outline(self):
        pass

    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
        """

        parents = self.html.xpath('//nav[@class="panel video-panel-info"]/div')

        for ret in parents:
            ret1 = ret.xpath('strong/text()')
            ret2 = ret.xpath('span//text()')
            # print(ret1)
            if "番號" in str(ret1):
                self.data.id = ret.xpath('a/@data-clipboard-text')[0]
            elif "日期" in str(ret1):
                self.data.release = ret2[0]
            elif "時長" in str(ret1):
                self.data.runtime = ret2[0].replace("分鍾", '')
            elif "導演" in str(ret1):
                self.data.director = ret2[0]
            elif "片商" in str(ret1):
                self.data.maker = ret2[0]
            elif "發行" in str(ret1):
                self.data.publisher = ret2[0]
            elif "系列" in str(ret1):
                self.data.series = ret2[0]
            elif "類別" in str(ret1):
                self.data.tags = ret2
            elif "演員" in str(ret1):
                self.data.actor = ret2

    def get_data(self, instance):
        """
        运行类中所有不带下划线的方法，返回数据
        """
        for _key, _fun in instance.__dict__.items():
            if type(_fun).__name__ == 'function' and "_" not in _key:
                _fun(self)
        return self.data


class JavdbBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Javdb(number, cfg)
        return self._instance.get_data(Javdb)


if __name__ == "__main__":
    # for test
    # pass
    from core.cli import get_cfg_defaults

    cfgs = get_cfg_defaults()
    jav = Javdb("ABP-454", cfgs)
    data = jav.get_data(Javdb)
    print(data.title)
