import heapq
import json
import random
import re
import shutil
from collections import defaultdict
from http.cookiejar import LWPCookieJar
from pathlib import Path
from urllib.parse import quote_plus, urlparse, parse_qs, quote
from urllib.request import getproxies

import requests
from requests.adapters import HTTPAdapter
from requests_html import HTML
from requests_html import HTMLResponse
from requests_html import HTMLSession
from urllib3.util.retry import Retry

from utils.logger import setup_logger

logger = setup_logger()


def call(fun):
    fun.is_callable = True
    return fun


class RequestHandler:
    """
    RequestHandler
    # https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    """

    def __init__(self, cfg):
        """
        Instantiates a new request handler object.
        """
        self.status_forcelist = cfg.request.status_forcelist
        self.timeout = cfg.request.timeout
        self.total = cfg.request.total
        self.backoff_factor = cfg.request.backoff_factor
        self.delay = cfg.request.delay
        self.cfg = cfg

    @property
    def proxy_strategy(self):
        # proxy in config file
        if self.cfg.proxy.enable:

            if self.cfg.proxy.type in self.cfg.proxy.support:
                proxy = "{}://{}".format(self.cfg.proxy.type,
                                         self.cfg.proxy.host)
                return {"http": proxy, "https": proxy}
        # logger.debug('using system proxy')
        return getproxies()

    @property
    def retry_strategy(self) -> Retry:
        """
        Using Transport Adapters we can set a default timeout for all HTTP calls
        Add a retry strategy to your HTTP client is straightforward.
        We create a HTTPAdapter and pass our strategy to the adapter.
        """
        return Retry(
            total=self.total,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor,
        )

    @property
    def session(self) -> HTMLSession:
        """
        Often when using a third party API you want to verify that the returned response is indeed valid.
        Requests offers the shorthand helper raise_for_status()
        which asserts that the response HTTP status code is not a 4xx or a 5xx,
        """
        session = HTMLSession()
        adapter = HTTPAdapter(max_retries=self.retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        assert_status_hook = (
            lambda response, *args, **kwargs: response.raise_for_status()
        )
        # the requests library offers a 'hooks' interface
        # where you can attach callbacks on certain parts of the request process.
        session.hooks["response"] = [assert_status_hook]
        return session

    @property
    def rebuild_proxies(self) -> dict:
        # noinspection PyBroadException
        try:
            free_proxy_pool = self.cfg.proxy.free_proxy_pool
            return random.choice(free_proxy_pool)
        except Exception:
            pass

    def get(self, url: str, **kwargs) -> HTMLResponse:
        """
        Returns the GET request encoded in `utf-8`.
        """
        try:
            response = self.session.get(
                url, timeout=self.timeout, proxies=self.proxy_strategy, **kwargs
            )
            response.encoding = "utf-8"
            return response
        except requests.exceptions.ProxyError as exc:
            logger.warning(f"ProxyError: {exc}")
            response = self.session.get(
                url, timeout=self.timeout, proxies=self.rebuild_proxies, **kwargs
            )
            response.encoding = "utf-8"
            return response
        except requests.exceptions.RequestException as exc:
            logger.warning(f"RequestError: {exc}")

    def post(self, url, data, **kwargs):
        try:
            return self.session.post(
                url,
                timeout=self.timeout,
                proxies=self.proxy_strategy,
                data=data,
                **kwargs,
            )
        except requests.exceptions.ProxyError as exc:
            logger.warning(f"ProxyError: {exc}")
            return self.session.post(
                url,
                timeout=self.timeout,
                proxies=self.rebuild_proxies,
                data=data,
                **kwargs,
            )
        except requests.exceptions.RequestException as exc:
            logger.warning(f"RequestError: {exc}")


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
            proxies=self.rebuild_proxies,
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


class GoogleTranslate(RequestHandler):
    # https://github.com/lushan88a/google_trans_new
    # 直接简化自此项目
    def __init__(self, cfg):
        super().__init__(cfg)
        self.url = (
            "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute"
        )

    @staticmethod
    def package_rpc(text, target):
        parameter = [[text.strip(), "auto", target, True], [1]]
        escaped_parameter = json.dumps(parameter, separators=(",", ":"))
        rpc = [
            [[random.choice(["MkEWBc"]), escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(",", ":"))
        return f"f.req={quote(espaced_rpc)}&"

    @staticmethod
    def extract(decoded):
        try:
            response = json.loads((decoded + "]"))
            response = json.loads(list(response)[0][2])
            response = list(response)[1][0]
            if len(response) == 1:
                if len(response[0]) > 5:
                    sentences = response[0][5]
                else:
                    sentences = response[0][0]
                return "".join("".join(d[0].strip()) for d in sentences)
            return "".join(s[0] for s in response)

        except Exception as exc:
            logger.warning(f"warn: {exc}")

    def translate(self, text, target="zh-cn"):
        if len(text) == 0:
            return
        freq = self.package_rpc(text, target)
        headers = {
            "Referer": "http://translate.google.com/",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = self.post(self.url, freq, headers=headers)
        for line in response.iter_lines(chunk_size=1024):
            decoded = line.decode("utf-8")
            if "MkEWBc" in decoded:
                return self.extract(decoded)


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        """
        队列由 (priority, index, item)形式的元祖构成
        Args:
            item:
            priority:
        """
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def empty(self):
        return bool(not self._queue)

    def arrange(self, item, priority):
        """
        用了个蠢办法实现，手动升级优先级的方法，
        因为要实现后进后出，用了index， 但是删除时也不知道index，又是一大开销啊
        Args:
            item:
            priority:
        """
        for i in self._queue:
            if i[2] == item:
                _index = i[1]
                _priority = i[0]
                self._queue.remove((_priority, _index, item))
        heapq.heapify(self._queue)
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1


class WebsitePriority(PriorityQueue):
    def __init__(self, sources):
        """
        初始化优先级队列，按照列表中的先后顺序排列
        Args:
            sources:
        """
        super().__init__()
        _gen = (d for d in sources)
        while True:
            try:
                self.push(next(_gen), 0)
            except StopIteration:
                break

    def sort_website(self, number):
        """
        按照特定 id 重新排序
        Args:
            number:
        """
        if re.match(r"^\d{5,}", number) or "heyzo" in number.lower():
            self.arrange("avsox", 1)
        elif re.match(r"\d+[a-zA-Z]+-\d+", number) or "siro" in number.lower():
            self.arrange("mgstage", 1)
        elif (
            re.match(r"\D{2,}00\d{3,}", number)
            and "-" not in number
            and "_" not in number
        ):
            self.arrange("dmm", 1)
        elif re.search(r"\D+\.\d{2}\.\d{2}\.\d{2}", number):
            self.arrange("javdb", 1)
        elif "fc2" in number.lower():
            self.arrange("fc2", 1)
        elif "rj" in number.lower():
            self.arrange("dlsite", 1)