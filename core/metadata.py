import itertools
import re
from bisect import insort
from pathlib import Path


class PriorityQueue:
    """
    """

    def __init__(self):
        self._pq = []
        self._entry_map = {}
        self._counter = itertools.count()

    def add(self, task, priority=None):
        # 如果 task 在 map 中，将原 entry 从 pq中移出
        if task in self._entry_map:
            old_entry = self._entry_map.pop(task)
            self._pq.remove(old_entry)
        # 队列由列表形式构成
        entry = [-priority, next(self._counter), task]
        self._entry_map[task] = entry
        insort(self._pq, entry)

    def pop(self):
        """移出并返回队列中最后一个值"""
        try:
            return self._pq.pop(0)[-1]
        except IndexError:
            pass

    def empty(self):
        return bool(not self._pq)


def sort_website(number, website):
    priority = PriorityQueue()
    for w in website:
        priority.add(w, 0)
    if re.match(r"^\d{5,}", number) or "heyzo" in number.lower():
        priority.add("avsox", 1)
    elif re.match(r"\d+[a-zA-Z]+-\d+", number) or "siro" in number.lower():
        priority.add("mgstage", 1)
    elif (
            re.match(r"\D{2,}00\d{3,}", number)
            and "-" not in number
            and "_" not in number
    ):
        priority.add("dmm", 1)
    elif re.search(r"\D+\.\d{2}\.\d{2}\.\d{2}", number):
        priority.add("javdb", 1)
    elif "fc2" in number.lower():
        priority.add("fc2", 1)
    elif "rj" in number.lower():
        priority.add("dlsite", 1)

    return priority


def check_data_state(data) -> bool:
    """
    check main metadata
    """
    if not data.title or data.title == "null":
        return False
    if not data.id or data.id == "null":
        return False
    return True


def extra_tag(file_path: Path, data):
    file_name = file_path.name
    # data.extra = {}
    if "流出" in file_name or "leaked" in file_name.lower():
        data.extra.leaked = "Leaked"

    if "-cd" in file_name.lower():
        searchobj = re.search(r"-cd\d", file_name, flags=re.I)
        if searchobj:
            data.extra.part = searchobj.group()

    if "-c" in file_name.lower() or "中文" in file_name or "字幕" in file_name:
        data.extra.sub = "-C"

    return data
