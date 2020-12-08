import re
from urllib.parse import urljoin

from lxml import etree

from crawler.crawlerCommon import CrawlerCommon
from utils.logger import Logger

logger = Logger()


class Javbus(CrawlerCommon):
    _url = ["https://www.fanbus.us/",
            "https://www.javbus.com/"
            ]

    def __init__(self, number, cfg):
        super().__init__(cfg)
        for url in self._url:
            try:
                logger.info(f'using javbus searching: {number}, using link {url}')

                self._response = self.response(urljoin(url, number)).text
                break
            # except HTTPError:
            finally:
                continue
        self.html = etree.fromstring(self._response, etree.HTMLParser())

    def title(self):
        """
        title
        """
        title = str(self.html.xpath('//div[@class="container"]/div/div[1]/a/img/@title'))
        try:
            self.data.title = re.sub('n\d+-', '', title)
        except AttributeError:
            self.data.title = title

    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
        """

        info = self.html.xpath('//div[@class="col-md-3 info"]')
        for i in info:
            # number
            self.data.id = str(i.xpath('//p[1]/span[2]/text()'))
            runtime = i.xpath('//p[position()>1 and position()<4]/text()')
            # release
            self.data.release = runtime[0]
            # runtime
            self.data.runtime = runtime[1].replace('分鐘', '')
            ret4 = i.xpath('ul/div/li//div[@class="star-name"]/a/text()')
            # print(ret4)
            # actor
            self.data.actor = ret4 if ret4 else ''

            ret3 = i.xpath('p/a/text()')
            ret5 = i.xpath('p/span/text()')
            if '導演:' in ret5:
                # director
                self.data.director = str(ret3[0])
                # studio
                self.data.studio = str(ret3[1])
                # label
                self.data.label = str(ret3[2])
            else:
                self.data.director = ""
                self.data.studio = str(ret3[0])
                # self.data.label = str(ret3[1]).strip(" ['']")
            if '系列:' in ret5:
                # serise
                self.data.serise = str(ret3[-1])
            else:
                self.data.serise = ""
            # genre
            self.data.genre = i.xpath('p[position()<last()]/span[@class="genre"]/a/text()')

    def cover(self):
        """
        cover
        """
        self.data.cover = self.html.xpath('//a[@class="bigImage"]/@href')[0]

    # def outline(self) -> str:
    #     self.data.outline = self.html.xpath("string(//div[contains(@class,'mg-b20 lh4')])").replace('\n', '')
    #
    # def cid(self):
    #     string = self.html.xpath("//a[contains(@class,'sample-box')][1]/@href")[
    #         0].replace('https://pics.dmm.co.jp/digital/video/', '')
    #     self.data.cid = re.sub('/.*?.jpg', '', string)


class JavbusBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Javbus(number, cfg)
        return self._instance.get_data(Javbus)


if __name__ == "__main__":
    # for test
    pass
    # from core.cli import get_cfg_defaults
    #
    # cfgs = get_cfg_defaults()
    # jav = Javbus("ABP-454", cfgs)
    # data = jav.get_data(Javbus)
    # print(data.title)
