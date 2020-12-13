import random

from crawler.crawlerComm import (
    CrawlerBase,
    GoogleSearch,
    call
)
from utils.logger import setup_logger

logger = setup_logger()


class Javdb(CrawlerBase):
    _url = ["https://javdb.com",
            "https://javdb4.com",
            "https://javdb6.com"
            ]

    def __init__(self, number, cfg):
        super().__init__(cfg)

        logger.debug(f'search {number} by javdb')
        self.base_url = random.choice(self._url)
        self.headers = {
            'Cookie': cfg.request.javbd_cookie,
            'referer': 'https://javdb.com/'
        }
        self.number = number
        google = GoogleSearch(cfg)
        url = google.search(self.number, self.base_url.replace('https://', ''))
        if url is not None:
            self.html = self.get_parser_html(url, headers=self.headers)
        else:
            self.html = self.search_url()

    def search_url(self):
        search_url = self.base_url + '/search?q=' + self.number + '&f=all'
        xpath = [
            '//div[@class="grid-item column"]',
            '//a/div[@class="uid"]/text()',
            '//a/@href'
        ]
        real_url = self.search(self.number, search_url, xpath[0], xpath[1], xpath[2])
        if real_url:
            return self.get_parser_html(self.base_url + real_url)

    @call
    def smallcover(self):
        pass

    # def cover(self):
    #     try:
    # self.data.cover = self.html.xpath('//img[@class="video-cover"]/@src')
    # except IndexError:
    #     self.data.cover = ""
    @call
    def outline(self):
        pass

    @call
    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
        """
        (self.data.title,) = self.html.xpath('//h2[@class="title is-4"]/strong/text()')

        parents = self.html.xpath('//nav[@class="panel video-panel-info"]', first=True)
        print(parents)
        self.data.id = parents.xpath('//div[1]/a/@data-clipboard-text', first=True)

        for element in parents.xpath('//div'):
            if element.xpath('//strong[contains(., "日期")]'):
                self.data.release = element.xpath('//span/text()', first=True)
            if element.xpath('//strong[contains(., "時長")]'):
                self.data.runtime = element.xpath('//span/text()', first=True).replace("分鍾", '')
            if element.xpath('//strong[contains(., "導演")]'):
                self.data.director = element.xpath('//span/a/text()', first=True)
            if element.xpath('//strong[contains(., "片商")]'):
                self.data.maker = element.xpath('//span/a/text()', first=True)
            if element.xpath('//strong[contains(., "系列")]'):
                self.data.series = element.xpath('//span/a/text()', first=True)
            if element.xpath('//strong[contains(., "類別")]'):
                self.data.tags = element.xpath('//span/a/text()')
            if element.xpath('//strong[contains(., "演員")]'):
                self.data.actor = element.xpath('//span/a/text()')


class JavdbBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Javdb(number, cfg)
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
    jav = Javdb("ABP-454", cfgs)
    # print(data)
    # cap = Javdb()
