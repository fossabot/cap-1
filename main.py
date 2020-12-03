from core.cli import (
    load_config,
    check_input
)
from core.cap import Cap


def main():
    """main entry"""
    # get command input, load config file
    cfg = load_config()
    target = check_input(cfg)
    cap = Cap(target, cfg)
    cap.process()


if __name__ == "__main__":
    main()
