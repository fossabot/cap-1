#!/usr/bin/env python
# author Luke
# version : 0.0.1
import asyncio
import time

from core.cap import capture
from utils.logger import setup_logger

logger = setup_logger()


def main():
    """main entry"""
    start_time = time.perf_counter()

    asyncio.run(capture())

    end_time = time.perf_counter()
    logger.debug(f'search video in {end_time - start_time} seconds')


if __name__ == "__main__":
    main()
