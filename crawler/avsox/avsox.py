import re

from crawler.crawlerCommon import CrawlerCommon
from utils.logger import Logger

logger = Logger()


class Avsox(CrawlerCommon):

    def __init__(self, number, cfg):
        super().__init__(cfg)
        # 搜寻 avsox 首页地址
        # transit_url = 'https://tellme.pw/avsox'
        # transit_html = self.get_parser_html(transit_url)
        # home_page_url = transit_html.xpath('//div[@class="container"]/div/a/@href')[0]
        self.number = number
        search_url = 'https://avsox.website' + '/cn/search/' + number
        parents_xpath = '//div[@id="waterfall"]'
        id_xpath = 'div/a/div/span/date/text()'
        url_xpath = 'div/a/@href'
        res = self.search(number, search_url, parents_xpath, id_xpath, url_xpath)
        if res is not None:
            self.html = res
        else:
            self.html = None

    def title(self):
        """
        title
        """
        title = str(self.html.xpath('//div[@class="container"]/h3/text()')[0])
        try:
            self.data.title = re.sub(r'[\D|\d]+[-|_]?[\D|\d]+', '', title)
        except AttributeError:
            self.data.title = title

    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
        """

        info = self.html.xpath('//div[@class="col-md-3 info"]')
        # for i in info:
        #     self.data.id = str(i.xpath('//p[1]/span[2]/text()'))
        #     runtime = i.xpath('//p[position()>1 and position()<4]/text()')
        #
        #     self.data.release = runtime[0]
        #     self.data.runtime = runtime[1].replace('分鐘', '')
        #     ret4 = i.xpath('ul/div/li//div[@class="star-name"]/a/text()')
        #     self.data.actor = ret4 if ret4 else ''
        #
        #     ret3 = i.xpath('p/a/text()')
        #     ret5 = i.xpath('p/span/text()')
        #     if '導演:' in ret5:
        #         self.data.director = str(ret3[0])
        #         self.data.studio = str(ret3[1])
        #         self.data.label = str(ret3[2])
        #     else:
        #         self.data.director = ""
        #         self.data.studio = str(ret3[0])
        #         # self.data.label = str(ret3[1]).strip(" ['']")
        #     if '系列:' in ret5:
        #         self.data.serise = str(ret3[-1])
        #     else:
        #         self.data.serise = ""
        #     self.data.genre = i.xpath('p[position()<last()]/span[@class="genre"]/a/text()')

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
    def get_data(self, instance):
        """
        运行类中所有不带下划线的方法，返回数据
        """
        for _key, _fun in instance.__dict__.items():
            if type(_fun).__name__ == 'function' and "_" not in _key:
                _fun(self)
        return self.data


class AvsoxBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        if not self._instance:
            self._instance = Avsox(number, cfg)
        return self._instance.get_data(Avsox)


if __name__ == "__main__":
    # for test
    # pass
    from core.cli import get_cfg_defaults

    cfgs = get_cfg_defaults()
    jav = Avsox("062218-690", cfgs)
    data = jav.get_data(Avsox)
    print(data.title)
