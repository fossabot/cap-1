import re
import heapq
import shutil

from crawler.requestHandler import RequestHandler
from utils.logger import Logger

logger = Logger()


class Metadata(dict):
    def __init__(self, **kwargs):
        super(Metadata, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            return ''


class CrawlerCommon(RequestHandler):

    def __init__(self, cfg):
        super().__init__(cfg)
        # self.__handler = RequestHandler()

    # @property
    # def _handler(self):
    #     """
    #     Return the `RequestHandler` of object.
    #     """
    #     return self.__handler

    def response(self, url: str, **kwargs):
        """
        Return the GET request response of object.
        """
        return self.get(url, **kwargs)

    def search(self):
        pass

    def download(self, url, file_name):
        r = self.response(url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(file_name, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            logger.info('sucessfully download: {}'.format(file_name))
        else:
            logger.info('fail download: {}'.format(file_name))


class PriorityQueue:

    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, _priority):
        heapq.heappush(self._queue, (-_priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def qsize(self):
        return len(self._queue)

    def empty(self):
        return True if not self._queue else False


class WebsitePriority(PriorityQueue):
    def __init__(self, sources):
        super().__init__()
        _gen = (d for d in sources)
        while True:
            try:
                self.push(next(_gen), 0)
            except StopIteration:
                break

    def sort_website(self, number):
        if re.match(r"^\d{5,}", number) or "heyzo" in number.lower():
            self.push("avsox", 1)
        if re.match(r"\d+\D+", number) or "siro" in number.lower():
            self.push("mgstage", 1)
        if "fc2" in number.lower():
            self.push("fc2", 1)
        if "rj" in number.lower():
            self.push("dlsite", 1)
