import re
import shutil
import sys
from pathlib import Path

# import requests
from lxml.etree import Element, SubElement, ElementTree

from utils.logger import Logger

logger = Logger()


# def free_proxy_pool(cfg):
#     """
#     https://github.com/jhao104/proxy_pool
#     get free proxy
#     store proxy to config
#     Args:
#         cfg:
#     Returns:
#
#     """
#     all_proxy = requests.get("http://118.24.52.95/get_all/").json()
#     proxy = []
#     for p in all_proxy:
#         proxy.append(p.get('proxy'))
#     cfg.proxy.freepool = proxy
#     return cfg


def number_parser(file: Path):
    def del_extra(st) -> str:
        """
        删除汉字，cd1.. ，cC ,时间戳
        """
        regex_list = [
            r'[\u4e00-\u9fa5]',
            r'cd\d+',
            r'-\d{4}-\d{1,2}-\d{1,2}',
            r'\d{4}-\d{1,2}-\d{1,2}-'
        ]
        for regex in regex_list:
            st = re.sub(regex, '', st, flags=re.I)
        st = st.strip('-cC ')
        return st

    filename: str = del_extra(file.stem)

    # 提取欧美番号 sexart.11.11.11, 尽可能匹配人名
    searchobj1 = re.search(r'^\D+\d{2}\.\d{2}\.\d{2}', filename)
    if searchobj1:
        r_searchobj1 = re.search(r'^\D+\d{2}\.\d{2}\.\d{2}\.\D+', filename)
        if r_searchobj1:
            return r_searchobj1.group()
        else:
            return searchobj1.group()

    # 提取xxx-av-11111
    searchobj2 = re.search(r'XXX-AV-\d{4,}', filename.upper())
    if searchobj2:
        return searchobj2.group()

    def regular_id(st) -> str:
        search_regex = [
            'FC2-\d{5,}',  # 提取类似fc2-111111番号
            '[a-zA-Z]+-\d+',  # 提取类似mkbd-120番号
            '\d+[a-zA-Z]+-\d+',  # 提取类似259luxu-1111番号
            '[a-zA-Z]+-[a-zA-Z]\d+',  # 提取类似mkbd-s120番号
            '\d+-[a-zA-Z]+',  # 提取类似 111111-MMMM 番号
            '\d+-\d+',  # 提取类似 111111-000 番号
            '\d+_\d+'  # 提取类似 111111_000 番号
        ]
        for regex in search_regex:
            searchobj = re.search(regex, st)
            if searchobj:
                return searchobj.group().replace('_', '-')
            else:
                continue

    if '-' in filename or '_' in filename:
        filename = regular_id(filename)
        if filename:
            return filename
    else:
        # filename = re.sub(u"\\(.*?\\)|{.*?}|\\[.*?]", "", filename)
        # filename = filename.translate({ord(c): '' for c in set(string.punctuation)})
        try:
            find_num = re.findall(r'\d+', filename)[0]
            find_char = re.findall(r'\D+', filename)[0]
            return find_char + '-' + find_num
        except re.error:
            logger.warning(f'fail to match id: \n{file.name}\n try input manualy')
            return input()


def create_failed_folder(search_path, needed_create):
    """
    create failed folder
    Args:
        needed_create:
        search_path:
    """
    faild_folder = Path(needed_create).resolve()

    # 如果配置文件中路径不是绝对路径
    if not faild_folder.is_absolute():
        created = search_path.parents.joinpath(needed_create)
        mkdir(created)
        return created
    else:
        mkdir(faild_folder)
        return faild_folder


def get_video_path_list(path, cfg):
    """
    search video according to path, exclude excluded folder
    Args:
        path: 需要搜寻的文件夹
        cfg: config

    Returns:

    """
    file_type = cfg.common.file_type
    excluded = [path.joinpath(e) for e in cfg.exclude.folder]
    return [f for f in path.rglob('*') if f.suffix in file_type and not [a for a in excluded if a in f.parents]]


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


def replace_date(data, location_rule: str) -> str:
    """
    replace path or name with the metadata
    Returns:
        str:
    """
    replace_data_list = [i for i in data.keys() if i in location_rule]
    for s in replace_data_list:
        location_rule = location_rule.replace(s, data[s])
    # # Remove illegal characters
    res = '[\/\\\:\*\?\"\<\>\|]'
    return re.sub(res, "_", location_rule)


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


def mv(target, dest, flag: str = None):
    """
    move video file searching failed to failed folder
    Args:
        target: org file path
        dest:
        flag:
    """
    try:
        shutil.move(target, dest)
        logger.info(fr'move {target.name} to {flag} folder')
    except Exception as error_info:
        logger.error("fail to move file" + str(error_info))


def mkdir(target):
    try:
        target.mkdir()
    except OSError as exc:
        logger.error("fail to create folder: {}".format(str(exc)))
        sys.exit()


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
