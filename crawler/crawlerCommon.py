import heapq
import re
import shutil
from collections import defaultdict

from googlesearch import search
from lxml import etree

from crawler.requestHandler import RequestHandler
from utils.logger import Logger

logger = Logger()


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
            return ''

    def __setattr__(self, key, value):
        self[key] = value


class CrawlerCommon(RequestHandler):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.data = Metadata()

    def get_parser_html(self, url: str, **kwargs):
        """
        Return the GET request response of object.
        """
        res = self.get(url, **kwargs).text
        return etree.HTML(res)

    def search_link_by_google(self, number, site):
        """
        偷懒耍滑之 google search
        Args:
            number:
            site:

        Returns:

        """
        res = search(number + '+site:' + site, stop=5)
        num = re.search(r'-(\d+)', number).group(1)
        for u in res:
            if re.findall('img', u):
                continue
            searchobj = re.search(num, u)
            if searchobj:
                return self.get_parser_html(u)
            return

    def search(self, number, search_link, parents_xpath, id_xpath, url_xpath):
        """
        无法通过 numer 定位网页，使用 search 的方法
        Args:
            number:
            search_link:
            parents_xpath: 获取所有单个项目列表的 xpath
            id_xpath: 以 parents_xpath 为基础寻找 id 的 xpath
            url_xpath: 以 parents_xpath 为基础寻找 url 的 xpath
        Returns:

        """
        # 获取搜索页面转换为 XML tree
        tree = self.get_parser_html(search_link)
        # 进一步使用 xpath 获得该页面所有结果的id，和 id 比较，使用正则？还是相似度呢？
        # 先获取所有结果的父节点列表, 以此为根节点，搜寻 id， 和 number 比较，如果对应，再以此父节点搜寻链接
        parents = tree.xpath(parents_xpath)

        part = re.split(r'[-|_]', number)
        for d in parents:
            num = d.xpath(id_xpath)[0]
            if re.match(part[0] + r'[-|_]?' + part[1], num):
                url = d.xpath(url_xpath)[0]
                return self.get_parser_html(url)
            return

    def download(self, url, file_name):
        r = self.get(url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(file_name, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            logger.info(f'sucessfully download: {file_name}')
        logger.warning(f'fail download: {file_name}')


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
        return True if not self._queue else False

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
        if re.match(r'^\d{5,}', number) or "heyzo" in number.lower():
            self.arrange("avsox", 1)
        elif re.match(r'\d+[a-zA-Z]+-\d+', number) or "siro" in number.lower():
            self.arrange("mgstage", 1)
        elif re.match(r'\D{2,}00\d{3,}', number) and '-' not in number and '_' not in number:
            self.arrange('dmm', 1)
        elif re.search(r'\D+\.\d{2}\.\d{2}\.\d{2}', number):
            self.arrange('javdb', 1)
        elif "fc2" in number.lower():
            self.arrange("fc2", 1)
        elif "rj" in number.lower():
            self.arrange("dlsite", 1)

