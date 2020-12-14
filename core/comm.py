"""
对应 argument， 这里放每一个视频都会运行的函数
"""
import re
import shutil
from pathlib import Path

from utils.logger import setup_logger

logger = setup_logger()


def move(src: Path, dest: Path, flag: str = None):
    """
    移动文件
    Args:
        src:
        dest:
        flag: faild or successfull
    """
    assert src.exists()
    try:
        shutil.move(src, dest)
        logger.info(f"move {src.name} to {flag} folder")
    except Exception as exc:
        logger.error(f"fail to move file: {str(exc)}")


def mkdir(src: Path):
    """
    创建文件夹，并返回已创建的文件夹
    Args:
        src:

    Returns:

    """
    assert src.exists()
    try:
        src.mkdir()
        logger.info(f"succeed create folder: {src.as_posix()}")
        return src
    except Exception as exc:
        logger.error(f"fail to create folder: {str(exc)}")


def symlink():
    raise NotImplementedError()


def create_folder(search_path: Path, needed_create: str):
    """
    根据相对路径和绝对路径创建文件夹
    Args:
        search_path:
        needed_create:

    Returns:

    """
    folder = Path(needed_create).resolve()
    if not folder.is_absolute():
        created = search_path.parent.joinpath(needed_create)
        return mkdir(created)
    return mkdir(folder)


def replace_date(data, location_rule: str) -> str:
    """
    replace path or name with the metadata
    Returns:
        str:
    """
    # 需要替换的数据名称列表
    replace_data_list = [i for i in data.keys() if i in location_rule]
    for s in replace_data_list:
        location_rule = location_rule.replace(s, data[s])
    # Remove illegal characters
    location_rule = re.sub(r'[/\\?%*:|"<>]', "_", location_rule)
    return location_rule.encode("ASCII", "ignore").decode()


def check_name_length(name, max_title_len) -> str:
    """
    check if the length of folder name or file name does exceed the limit
    try manual entry
    (Is there a limit now? It’s too long to look good, right?)
    Args:
        max_title_len:  length of name in config user defining
        name: name from website

    Returns: input name

    """
    # Remove the space on the right side of folder name or file name
    name = name.rstrip()
    if len(name) > max_title_len:
        logger.info(f"folder name is too long: {name}\ntry manual entry：\n")
        choice = input("automatic clip name(y), or try manual entry: \n")
        if choice.lower() == "y":
            return name[:max_title_len]
        check_name_length(choice, max_title_len)
    return name
