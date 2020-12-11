import asyncio
import time

from core.cap import capture


def main():
    """main entry"""
    start_time = time.perf_counter()

    asyncio.run(capture())

    end_time = time.perf_counter()
    print(f'search video in {end_time - start_time} seconds')


if __name__ == "__main__":
    main()
