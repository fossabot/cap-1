import re
from http.cookiejar import LWPCookieJar
from pathlib import Path
from urllib.parse import parse_qs, urlparse, quote_plus

from requests_html import HTML

from crawler.requestHandler import RequestHandler
from utils.logger import setup_logger

logger = setup_logger()


class GoogleSearch(RequestHandler):
    """
    偷懒耍滑之 google search
    主要还是用来减少访问目标站点的次数，应该是有更好的方法的
    并且检查google search得到的网页是否正确
    """

    def __init__(self, cfg):
        super().__init__(cfg)
        cookie = Path(__file__).parent.parent.joinpath(".google-cookie")
        if cookie.exists():
            self.cookie_jar = LWPCookieJar(cookie)
            # noinspection PyBroadException
            try:
                self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
            except Exception:
                pass
        else:
            self.cookie_jar = None
            self.get_page("https://www.google.com/")

    def get_page(self, url):
        """
        加载 cookie， 获取网页，之后保存
        Args:
            url: 搜索链接

        Returns:

        """
        response = self.session.get(
            url,
            timeout=self.timeout,
            proxies=self.proxy_strategy,
            cookies=self.cookie_jar,
        )
        response.encoding = "utf-8"
        html = response.text
        # noinspection PyBroadException
        try:
            self.cookie_jar.save(ignore_discard=True, ignore_expires=True)
        except Exception:
            pass
        return html

    @staticmethod
    def filter(link):
        """
        获得的原始 url
        """
        # 参考自 https://github.com/MarioVilas/googlesearch
        # noinspection PyBroadException
        try:
            if link.startswith("/url?"):
                link = parse_qs(urlparse(link, "http").query)["q"][0]
            url = urlparse(link, "http")
            if url.netloc and "google" not in url.netloc:
                return link
        except Exception:
            ...

    @staticmethod
    def extract(html, number):
        """
        从搜索页面提取标题和 url， 标题中含有番号则返回 url
        估计这个用xpath提取标题很容易失效
        Args:
            html:
            number:

        Returns:

        """
        html = HTML(html=html)
        link_content = html.xpath("//a")
        # 直接维护列表
        title_xpath = ["//h3/div/text()", "//h3/span/text()"]
        for content in link_content:
            for xpath in title_xpath:
                title = content.xpath(xpath, first=True)
                if not title:
                    continue
                if re.search(
                        "".join(filter(str.isalnum, number)),
                        "".join(filter(str.isalnum, title)),
                        flags=re.I,
                ):
                    link = content.xpath("//@href", first=True)
                    if link:
                        return link

    def search(self, number, site):
        """
        通过加 site 指定网站，语言使用 en，我试了一下，不然搜不出来
        Args:
            number:
            site:

        Returns:

        """
        query = quote_plus(number + "+site:" + site)
        html = self.get_page(
            f"https://google.com/search?hl=en&q={query}&safe=off")
        return self.filter(self.extract(html, number))
