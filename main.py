import time

from core.cap import Cap
from core.cli import (
    load_config,
    check_input
)


def main():
    """main entry"""
    # get command input, load config file
    start_time = time.perf_counter()
    cfg = load_config()
    target = check_input(cfg)
    cap = Cap(target, cfg)
    cap.start()
    end_time = time.perf_counter()
    print(f'search video in {end_time - start_time} seconds')


if __name__ == "__main__":
    main()
