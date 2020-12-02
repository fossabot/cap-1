from core.cli import (
    load_config,
    check_input
)
from core.cap import Cap
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

_UI_LOCK = Lock()
_workers = ThreadPoolExecutor(max_workers=2)


def main():
    """main entry"""
    # get command input, load config file
    cfg = load_config()
    target = check_input(cfg)
    cap = Cap(target, cfg)
    cap.process()


if __name__ == "__main__":
    main()
