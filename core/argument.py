"""
这里放程序运行，只会运行一次的函数
"""

import argparse
import re
import textwrap
from pathlib import Path

import requests

from core.number_parser import number_parser
from utils.config import get_cfg_defaults
from utils.logger import setup_logger

logger = setup_logger()


def set_argparse():
    parser = argparse.ArgumentParser(
        prog="\n\n|> ./cap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.indent(
            """\

    🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞🔞
    ------------------------------------
    ¶ search for video files in the path of the executable file and its folder
    > ./cap

    ¶ folder path (or define in config.yaml)

    > ./cap folder_path

    ¶ please take your number if single file, use the arrows to point to number
    > ./cap file->number

    ¶ specifying configuration files is no problem either.
    > ./cap -c configuration_file

    """,
            "+",
            lambda line: True,
        ),
    )
    parser.add_argument(
        "p", default="G:/a/ARA-460.mp4->ARA-460", nargs="?", help="file->number"
    )
    parser.add_argument("-c", default="config.yaml",
                        help="configuration file path")
    parser.add_argument("-d", default=False, help="setting global logger")

    return parser.parse_args()


def merge_config(cfg, path):
    """
    将用户配置 merge 进默认配置
    Args:
        cfg:
        path:
    """
    try:
        cfg.merge_from_file(path)
        logger.info("load config, start searching")
    except Exception as e:
        logger.error(f"config file error:{e}")


def load_config(parser_config):
    """
    load default config and merge user config
    Returns:

    """
    # parser = set_argparse()
    # load config file
    cfg = get_cfg_defaults()
    config_file = Path(__file__).parent.parent.joinpath("config.yaml")

    assert isinstance(
        parser_config, str), "input must single file->id or single folder"

    if parser_config:
        merge_config(cfg, parser_config)

    elif config_file.exists():
        merge_config(cfg, str(config_file))

    else:
        logger.info("use defalt config")
    return cfg


def get_video_path_list(search_path, cfg):
    """
    search video according to path, exclude excluded folder
    Args:
        search_path: 需要搜寻的文件夹
        cfg: config

    Returns: 文件地址列表

    """
    file_type = cfg.common.file_type
    # 完整排除文件夹的路径
    excluded = [search_path.joinpath(e) for e in cfg.exclude.folders]
    # suffix 获取后缀
    # parents 获取所有父级文件夹
    # 如果在需要搜索的文件中，文件符合格式后缀，且该文件的所有父级文件夹不在排除文件夹中，则为需要的文件
    # （感觉这个写法开销是很大的，需要改进，且有滥用列表生成式的问题）
    return [
        f for f in search_path.rglob("*")
        if f.suffix in file_type
           and not
           [n for n in excluded if n in f.parents]
    ]


def check_number_parser(target):
    """
    搜索之后，检查番号，可通过手动输入的方式，纠正番号提取
    Args:
        target:

    Returns:

    """
    logger.info("file pointing number", extra={"dict": target})
    flag = input("change number(c) or continue(enter) \n")
    if flag.lower() == "c":
        file_id = input("use [ <Serial_number><space>number ], eg 4 ABP-454\n")
        try:
            file = list(target.keys())[file_id.split()[0] - 1]
            target[file] = file_id.split()[1]
            check_number_parser(target)
        except KeyError:
            logger.error(f"Syntax error: {file_id}  Check once")
        check_number_parser(target)
    return target


def check_file(obj, cfg):
    """
    检查单个视频

    """
    file = Path(obj[0])
    if file.is_file():
        logger.info(
            f"The following video: {obj[0]}  {obj[1]} will be searched soon"
        )
        return file, [file], [obj[1]], cfg
    logger.error(f"file path error: {obj[0]}")


def check_folder(obj, cfg):
    """
    搜索视频，提取番号

    """
    path = Path(obj[0]).resolve()
    if path.is_dir():
        files = get_video_path_list(path, cfg)
        if len(files) > 0 and cfg.deubg.enable:
            logger.info(
                f"the videos in folder: {obj[0]} will be searched soon:",
                extra={"list": files},
            )
        number = [number_parser(f) for f in files]
        assert isinstance(number, list)
        return path, files, number, cfg
    logger.error(f"folder path error: {str(path)}")


def load_argument():
    """
    加载配置和命令行输入，处理之后提交给主函数
    Returns:
    """
    parser = set_argparse()
    assert isinstance(
        parser.p, str), "input must single file-id or single folder"
    cfg = load_config(parser.c)
    if parser.d is not False:
        cfg.deubg.enable = True
    if cfg.request.enable_free_proxy_pool:
        # https://github.com/jhao104/proxy_pool
        # 测试地址, 一次获取所有，存储在 cfg 中，以便后续调用
        all_proxy = requests.get("http://118.24.52.95/get_all/").json()
        cfg.proxy.free_proxy_pool = [p.get("proxy") for p in all_proxy]
    # split means pointing number
    obj = re.split(r"->", parser.p)
    assert len(obj) >= 2
    if len(obj) == 2:
        return check_file(obj, cfg)
    else:
        return check_folder(obj, cfg)
