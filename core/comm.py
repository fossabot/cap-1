"""
对应 argument， 这里放每一个视频都会运行的函数
"""
import re
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

from utils.logger import setup_logger
from utils.path import PathHandler

logger = setup_logger()


def check_data_state(data) -> bool:
    """
    check main metadata
    """
    if not data.title or data.title == "null":
        return False
    if not data.id or data.id == "null":
        return False
    return True


def extra_tag(file_path: Path, data):
    file_name = file_path.name
    # data.extra = {}
    if '流出' in file_name or 'leaked' in file_name.lower():
        data.extra.leaked = 'Leaked'

    if '-cd' in file_name.lower():
        searchobj = re.search(r'-cd\d', file_name, flags=re.I)
        if searchobj:
            data.extra.part = searchobj.group()

    if '-c' in file_name.lower() or '中文' in file_name or '字幕' in file_name:
        data.extra.sub = '-C'

    return data


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


def create_successfull_folder(search_path, data, cfg):
    """
    use metadate replace location_rule, create folder
    使用爬取的元数据替换路径规则，再创建文件。
    根据 / 划分层级，检查每层文件夹的名称长度
    Args:
        cfg:
        search_path:
        data: metadata
    """
    # If the number of actors is more than 5, take the first two
    # 如果演员数量大于5 ，则取前两个

    if len(data.actor.split(',')) >= 5:
        data.actor = ','.join(data.actor.split(',')[:2]) + 'etc.'
    location_rule = replace_date(data, cfg.name_rule.location_rule)
    # mkdir folder by level
    new_folder = None
    for name in location_rule.split('/'):
        name = check_name_length(name, cfg.name_rule.max_title_len)
        output_folder = create_successfull_folder(search_path, cfg.name_rule.success_output_folder, cfg)
        new_folder = PathHandler.mkdir(output_folder.joinpath(name))
    return new_folder


def rename_move_file(old_file_path, new_folder_path, data, cfg):
    # 替换数据，检查长度，移动和重命名文件，
    # check length of name
    naming_rule = check_name_length(cfg.name_rule.naming_rule, cfg.name_rule.max_title_len)
    file_name = replace_date(data, naming_rule)

    for mark in data.extra.values():
        file_name += '-' + mark

    file_name += old_file_path.suffix
    new_file_path = new_folder_path.joinpath(file_name)
    PathHandler.move(old_file_path, new_file_path)
    return new_file_path


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

    ElementTree(nfo_root).write(filename, encoding="utf-8", xml_declaration=True)
