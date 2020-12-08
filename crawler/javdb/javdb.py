from urllib.parse import urljoin

from defusedxml import etree
from requests import RequestException

from crawler.crawlerCommon import CrawlerCommon
from utils.logger import Logger

logger = Logger()


class Javdb(CrawlerCommon):
    _url = ["https://javdb.com/",
            "https://javdb4.com/"
            ]

    def __init__(self, number, cfg):
        super().__init__(cfg)
        # self.number = number
        for url in self._url:
            logger.info(f'\nusing javbus searching: {number}, using ling {url}')
            # url = urljoin(url, 'search?q=', number, '&f=all')
            url += 'search?q=' + number + '&f=all'
            try:
                self.query = self.response(url).text
                break
            except RequestException as exc:
                logger.error(f'request error: {exc}')
                continue
        self.query_html = etree.fromstring(self.query, etree.HTMLParser())
        urls = self.query_html.xpath('//div[@class="grid-item column"]/a/@href')
        ids = self.query_html.xpath('//div[@class="grid-item column"]/a/div[contains(@class, "uid")]/text()')
        real_url = urls[ids.index(number)]
        _real_url = urljoin(self._url[0], real_url)
        self._response = self.response(_real_url).text
        self.html = etree.fromstring(self._response, etree.HTMLParser())

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


class JavdbBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Javdb(number, cfg)
        return self._instance.get_data(Javdb)


if __name__ == "__main__":
    # for test
    pass
    # from core.cli import get_cfg_defaults
    #
    # cfgs = get_cfg_defaults()
    # jav = Javdb("FC2-1591505", cfgs)
    # data = jav.get_data()
    # print(data.released)
