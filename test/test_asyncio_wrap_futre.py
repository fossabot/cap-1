"""
## asyncio.Future vs concurrent.futures.Future
One final thing to mention is that a concurrent.futures.Future object is different from an asyncio.Future.
An asyncio.Future is intended to be used with the asyncio’s event loop, and is awaitable.
A concurrent.futures.Future is not awaitable.
Using the .run_in_executor() method of an event loop will provide the necessary interoperability
between the two future types by wrapping the concurrent.futures.Future type in a call to asyncio.wrap_future
Since Python 3.5 we can use asyncio.wrap_future to convert a concurrent.futures.Future to an asyncio.Future
"""

import asyncio
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps


def threadpool(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return asyncio.wrap_future(ThreadPoolExecutor(5).submit(f, *args, **kwargs))

    return wrap


class CapBase:
    def __init__(self, file):
        self.file = file

    @classmethod
    def parameter(cls, file):
        return cls(file)


class Cap(CapBase):
    def get_data(self):
        print(f"{self.file} start get data")
        i = random.randint(0, 10)
        time.sleep(i)
        print(f"{self.file} end get data")
        return i

    def download(self, tm):
        print(f"{self.file} start download No. {tm} ")
        time.sleep(tm)
        print(f"{self.file} end download No. {tm} ")

    @threadpool
    def start(self):
        print(f"{self.file}: start")
        res = self.get_data()
        for i in range(3):
            self.download(i)
        print(f"{self.file}: end")
        return res


async def run():
    files = ["task a", "task b", "task c"]
    tasks = []
    for file in files:
        tasks.append(Cap.parameter(file).start())

    res = await asyncio.gather(*tasks)
    return res


if __name__ == "__main__":
    a = asyncio.run(run())
    print(a)
