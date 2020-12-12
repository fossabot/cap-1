import re

from crawler.crawlerCommon import (
    CrawlerCommon,
    GoogleSearch,
    call
)
from utils.logger import setup_logger

logger = setup_logger()


class Avsox(CrawlerCommon):

    def __init__(self, number, cfg):
        super().__init__(cfg)
        # test
        logger.debug(f'search {number} by avsox')
        self.number = number
        google = GoogleSearch(cfg)
        url = google.search(self.number, 'avsox.website')
        if url is not None:
            self.html = self.get_parser_html(url)
        else:
            self.html = self.search_url()

    def search_url(self):
        transit_html = self.get_parser_html('https://tellme.pw/avsox')
        home_page_url = transit_html.xpath('//div[@class="container"]/div/a/@href', first=True)
        search_url = home_page_url + '/cn/search/' + self.number
        xpath = [
            '//div[@id="waterfall"]',
            'div/a/div/span/date/text()',
            'div/a/@href'
        ]
        real_url = self.search(self.number, search_url, xpath[0], xpath[1], xpath[2])
        if real_url:
            return self.get_parser_html(real_url)

    def title(self):
        """
        title
        """
        title = str(self.html.xpath('//div[@class="container"]/h3/text()')[0])
        try:
            self.data.title = re.sub(r'[\D|\d]+[-|_]?[\D|\d]+', '', title)
        except AttributeError:
            self.data.title = title

    @call
    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
        """

        info = self.html.xpath('//div[@class="col-md-3 info"]')

    # def cover(self):
    #     """
    #     cover
    #     """
    # self.data.cover = self.html.xpath('//a[@class="bigImage"]/@href')[0]

    # def outline(self) -> str:
    #     self.data.outline = self.html.xpath("string(//div[contains(@class,'mg-b20 lh4')])").replace('\n', '')
    #
    # def cid(self):
    #     string = self.html.xpath("//a[contains(@class,'sample-box')][1]/@href")[
    #         0].replace('https://pics.dmm.co.jp/digital/video/', '')
    #     self.data.cid = re.sub('/.*?.jpg', '', string)


class AvsoxBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Avsox(number, cfg)
            for method in dir(self._instance):
                fun = getattr(self._instance, method)
                if getattr(fun, "is_callable", False):
                    fun()
        return self._instance.data


if __name__ == "__main__":
    # for test
    # pass
    from utils.config import get_cfg_defaults

    #
    cfgs = get_cfg_defaults()
    jav = Avsox("111720_001", cfgs)
    print(jav.data)
