from core.cap import Cap
from core.cli import (
    load_config,
    check_input
)


def main():
    """main entry"""
    # get command input, load config file
    cfg = load_config()
    target = check_input(cfg)
    cap = Cap(target, cfg)
    metadata = cap.start()
    # 测试数据获取
    # for i, k in metadata.items():
    #     print(i)
    #     print(k)


if __name__ == "__main__":
    main()
