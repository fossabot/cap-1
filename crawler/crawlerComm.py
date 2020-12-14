import re
import shutil
from collections import defaultdict

from requests_html import HTML

from crawler.requestHandler import RequestHandler
from utils.logger import setup_logger

logger = setup_logger()


def call_func(fun):
    fun.is_callable = True
    return fun


class Metadata(defaultdict):
    """
    A dictionary supporting dot notation. and nested access
    do not allow to convert existing dict object recursively
    """

    def __init__(self):
        super(Metadata, self).__init__(Metadata)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return ""

    def __setattr__(self, key, value):
        self[key] = value


class CrawlerBase(RequestHandler):
    def __init__(self, cfg):
        super().__init__(cfg)
        self._data = Metadata()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def get_parser_html(self, url: str, **kwargs):
        """
        Return the parser element
        """
        res = self.get(url, **kwargs).text
        return HTML(html=res)

    def search(self, number, search_url, parents_xpath, id_xpath, url_xpath, **kwargs):
        """
        通过常规搜索来确定详细页面链接，获取 html
        """
        # 搜索页面
        search_page = self.get_parser_html(search_url, **kwargs)
        # 一般搜索界面都是瀑布流，以此为根节点
        parents = search_page.xpath(parents_xpath)

        for element in parents:
            # 在父节点基础上，搜寻id
            num = element.xpath(id_xpath, first=True)
            # 如果id符合
            if re.match(
                    "".join(filter(str.isalnum, number)),
                    "".join(filter(str.isalnum, num)),
                    flags=re.I,
            ):
                return element.xpath(url_xpath, first=True)
            continue


class DownloadImg(RequestHandler):

    def download(self, url, file_name):
        r = self.get(url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(file_name, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            logger.info(f"sucessfully download: {file_name}")
        logger.warning(f"fail download: {file_name}")

    def download_all(self, img_url: dict, folder):
        for name, url in img_url.items():
            self.download(url, folder.joinpath(name + "jpg"))
