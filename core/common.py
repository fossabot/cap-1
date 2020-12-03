import os
import re
import shutil
import sys
from pathlib import Path

import requests
# from dataclasses import asdict
from lxml.etree import Element, SubElement, ElementTree

from utils.logger import Logger

logger = Logger()


def free_proxy_pool(cfg):
    """
    https://github.com/jhao104/proxy_pool
    get free proxy
    store proxy to config
    Args:
        cfg:
    Returns:

    """
    all_proxy = requests.get("http://118.24.52.95/get_all/").json()
    proxy = []
    for p in all_proxy:
        proxy.append(p.get('proxy'))
    cfg.proxy.freepool = proxy
    return cfg


def number_parser(file_path: str):
    # //TODO 还没看
    # file_path = os.path.basename(file_path)
    file_path = Path(file_path).resolve()
    # return file_path
    try:
        if '-' in file_path or '_' in file_path:
            file_path = file_path.replace("_", '-')
            filename = str(
                re.sub(r"\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", file_path))  # 去除文件名中时间
            file_number = re.search(r'\w+-\w+', filename, re.A).group()
            return file_number
        else:  # 提取不含减号-的番号，FANZA CID
            try:
                return str(
                    re.findall(r'(.+?)\.',
                               str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', file_path).group()))).strip(
                    "['']").replace('_', '-')
            except re.error:
                return re.search(r'(.+?)\.', file_path)[0]
    except Exception as e:
        print('[-]' + str(e))
        return


def create_failed_folder(cfg) -> object:
    """
    create failed folder
    Args:
        cfg:
    """
    faild_folder = Path(cfg.common.failed_output_folder)
    try:
        faild_folder.mkdir(exist_ok=True)
    except OSError as exc:
        logger.error("fail to create folder: {}".format(str(exc)))
        sys.exit()


def get_video_path_list(folder_path, cfg):
    """
    search video according to path, exclude excluded folder
    Args:
        folder_path:
        cfg:

    Returns:

    """
    path_list = []
    file_type = tuple(['.mp4', '.avi', '.rmvb', '.wmv', '.mov',
                       '.mkv', '.flv', '.ts', '.webm', '.iso'])

    for root, dirs, files in os.walk(folder_path, topdown=True):
        # exclude folder
        dirs[:] = [d for d in dirs if d not in cfg.exclude.folder]
        # filter
        files[:] = [f for f in files if f.lower().endswith(file_type)]

        for file in files:
            path_list.append(os.path.join(root, file))

    return path_list


def check_data_state(data) -> object:
    """
    check main metadata
    """
    if not data.title or data.title == "null":
        return False
    if not data.number or data.number == "null":
        return False
    else:
        return True


def replace_date(data, location_rule) -> str:
    """
    replace path or name with the metadata
    Returns:
        str:
    """
    # TODO 更换了数据暂存方式，需要更改
    # replace_data_list = [i for i in list(
    #     asdict(data).keys()) if i in location_rule]
    # for s in replace_data_list:
    #     location_rule = location_rule.replace(s, asdict(data)[s])
    # # Remove illegal characters
    # res = '[\/\\\:\*\?\"\<\>\|]'
    # location_rule = re.sub(res, "_", location_rule)
    # return location_rule


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
        logger.info("folder name is too long:%s\ntry manual entry：\n".format(name))
        choice = input("automatic clip name(y), or try manual entry: \n")
        if choice.lower() == "y":
            return name[:max_title_len]
        else:
            check_name_length(choice, max_title_len)
    else:
        return name


def move_to_failed_folder(file_path, cfg):
    """
    move video file searching failed to failed folder
    Args:
        file_path: org file path
        cfg: config
    """
    try:
        shutil.move(file_path, cfg.common.failed_output_folder)
        logger.info("move %s to failed folder".format(os.path.split(file_path)[1]))
    except Exception as error_info:
        logger.error("fail to move file" + str(error_info))


def write_nfo(file_path, data, cfg):
    """
    //TODO fields写完
    Args:
        cfg:
        file_path:
        data:
    """
    nfo_root = Element("movie")
    folder = Path(file_path).parent
    filename = folder.joinpath(Path(file_path).with_suffix('.nfo'))
    nfo_fields = dict
    if cfg.common.mode == "":
        nfo_fields = {
            'title': data.title,
            'studio': data.studio,
            'year': data.year,
            'tag': data.tag,
        }
    for field_name, values in nfo_fields.items():
        if not values:
            continue
        if not isinstance(values, list):
            values = [values]
        for value in values:
            SubElement(nfo_root, field_name).text = f"{value}"

    ElementTree(nfo_root).write(
        filename, encoding="utf-8", xml_declaration=True, pretty_print=True
    )
