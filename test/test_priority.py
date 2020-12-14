import itertools
from bisect import insort


class PriorityQueue:
    """
    """

    def __init__(self):
        self._pq = []
        self._entry_map = {}
        self._counter = itertools.count()
        self.priority = staticmethod(lambda p: -int(p or 0))

    def add(self, task, priority=None):
        # 如果 task 在 map 中，将原 entry 从 pq中移出
        if task in self._entry_map:
            old_entry = self._entry_map.pop(task)
            self._pq.remove(old_entry)
        # 队列由列表形式构成
        entry = [self.priority(priority), next(self._counter), task]
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


def test_priority():
    pq = PriorityQueue()
    # 相当于初始化
    pq.add('task1', 0)
    pq.add('task2', 0)
    pq.add('task3', 0)
    pq.add('task4', 0)
    # 相当于重新整理
    pq.add('task2', 1)
    pq.add('task1', 2)

    while not pq.empty():
        assert pq.pop() == 'task1'
        assert pq.pop() == 'task2'
        assert pq.pop() == 'task3'
        assert pq.pop() == 'task4'
