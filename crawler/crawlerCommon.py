import heapq
import re
import shutil
from collections import defaultdict

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


# class Metadata(dict):
#     def __getattr__(self, key):
#         try:
#             return self[key]
#         except KeyError:
#             return ''
#
#     def __setattr__(self, key, value):
#         self[key] = value
#
#     # def __delattr__(self, key):
#     #     try:
#     #         del self[key]
#     #     except KeyError as k:
#     #         raise AttributeError(k)
#
#     def __repr__(self):
#         return dict.__repr__(self)


class CrawlerCommon(RequestHandler):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.data = Metadata()

    def response(self, url: str, **kwargs):
        """
        Return the GET request response of object.
        """
        return self.get(url, **kwargs)

    def search(self):
        pass

    def get_data(self, instance):
        for key, fun in instance.__dict__.items():
            if type(fun).__name__ == 'function' and "_" not in key:
                fun(self)
        return self.data

    def download(self, url, file_name):
        r = self.response(url, stream=True)
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
        # 队列由 (priority, index, item)形式的元祖构成
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def empty(self):
        return bool(self._queue)

    def arrange(self, item, priority):
        # 用了个蠢办法实现，手动升级优先级的方法，
        # 因为要实现后进后出，用了index， 但是删除时也不知道index，又是一大开销啊
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
        super().__init__()
        # 初始化优先级队列，按照列表中的先后顺序排列
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

