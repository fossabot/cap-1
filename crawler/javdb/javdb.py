import random

from crawler.crawlerComm import CrawlerBase, call_func
from crawler.search import GoogleSearch
from utils.logger import setup_logger

logger = setup_logger()


class Javdb(CrawlerBase, GoogleSearch):
    _url = ["https://javdb.com", "https://javdb4.com", "https://javdb6.com"]

    def __init__(self, number, cfg):
        super().__init__(cfg)

        logger.debug(f"search {number} by javdb")
        self.base_url = random.choice(self._url)
        self.headers = {
            "Cookie": cfg.request.javbd_cookie,
            "referer": self.base_url,
        }
        self.number = number

        url = self.google_search(
            self.number, self.base_url.replace("https://", ""))

        if url is not None:
            self.html = self.get_parser_html(url, headers=self.headers)
        else:
            self.html = self.search_url

    @property
    def search_url(self):
        """

        Returns: parser html

        """
        search_url = self.base_url + "/search?q=" + self.number + "&f=all"
        # 瀑布流 xpath
        # 番号 xpath
        # 链接 xpath
        xpath = [
            '//div[@class="grid-item column"]',
            '//a/div[@class="uid"]/text()',
            "//a/@href",
        ]
        real_url = self.search(self.number, search_url,
                               xpath[0], xpath[1], xpath[2], headers=self.headers)
        if real_url:
            return self.get_parser_html(self.base_url + real_url, headers=self.headers)

    @call_func
    def smallcover(self):
        pass

    # def cover(self):
    #     try:
    # self.data.cover = self.html.xpath('//img[@class="video-cover"]/@src')
    # except IndexError:
    #     self.data.cover = ""
    @call_func
    def outline(self):
        pass

    @call_func
    def info(self):
        """
        number, release, length, actor, director, studio, label, serise, genre
        """
        self.data.title = self.html.xpath(
            '//h2[@class="title is-4"]/strong/text()', first=True
        )

        parents = self.html.xpath(
            '//nav[@class="panel video-panel-info"]', first=True)
        self.data.id = parents.xpath(
            "//div[1]/a/@data-clipboard-text", first=True)

        # for element in parents.xpath('//div'):
        #     if element.xpath('//div/strong[contains(., "日期")]'):
        self.data.release = parents.xpath(
            '//div/strong[contains(., "日期")]/../span/text()', first=True
        )
        self.data.runtime = parents.xpath(
            '//div/strong[contains(., "時長")]/../span/text()', first=True
        ).replace("分鍾", "")
        self.data.director = parents.xpath(
            '//div/strong[contains(., "導演")]/../span/a/text()', first=True
        )
        self.data.maker = parents.xpath(
            "//div/span/a/text()/span/a/text()", first=True)
        self.data.series = parents.xpath(
            '//div/strong[contains(., "系列")]/../span/a/text()', first=True
        )
        self.data.tags = parents.xpath(
            '//div/strong[contains(., "類別")]/../span/a/text()'
        )
        self.data.actor = parents.xpath(
            '//div/strong[contains(., "演員")]/../span/a/text()'
        )


class JavdbBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, number, cfg):
        """
        传入参数，新建一个实例，运行带有 is_callable 属性的方法（即带有 call_func 装饰器的）
        Args:
            number:
            cfg:

        Returns: data 属性，抓取的数据都在这个字典里

        """
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
    jav = JavdbBuilder()
    j = jav("ABP-454", cfgs)
    print(j)
