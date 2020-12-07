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
        logger.info(f'move {target.name} to {flag} folder')
    except Exception as error_info:
        logger.error(f'fail to move file: {str(error_info)}')


def mkdir(target):
    try:
        target.mkdir()
        return target
    except OSError as exc:
        logger.error(f'fail to create folder: {str(exc)}')
        sys.exit()


def number_parser(filename):
    """
    提取番号
    又在 btsow 上抓了一些 Hot Tags 页面的番号，测试一下
    正则也不会，感觉这段写的好蠢，开销大不大的
    Args:
        filename:

    Returns:

    """

    def del_extra(st) -> str:
        """
        删除cd1.. ，时间戳,
        """
        regex_list = [
            # r'[\u4e00-\u9fa5]+',
            # r'[^A-Za-z0-9-_.()]',
            r'cd\d$',  # 删除cd1
            r'-\d{4}-\d{1,2}-\d{1,2}',  # 日期
            r'\d{4}-\d{1,2}-\d{1,2}-',
            r'1080p',
            r'1pon',
            r'.com',
            r'nyap2p',
            r'22-sht.me',
            r'xxx'
        ]
        for regex in regex_list:
            st = re.sub(regex, '', st, flags=re.I)
        st = st.rstrip('-cC ')
        return st

    filename = del_extra(filename.stem)

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
    # 提取luxu
    if 'luxu' in filename.lower():
        searchobj3 = re.search(r'\d{0,3}luxu[-_]\d{4}', filename, re.I)
        if searchobj3:
            return searchobj3.group()
    # 如果有fc2删除 ppv
    if 'fc2' in filename.lower() and 'ppv' in filename.lower():
        # 如果有短横线，则删除 ppv
        if re.search(r'ppv\s*[-|_]\s*\d{6,}', filename, flags=re.I):
            filename = re.sub(r'ppv', '', filename, flags=re.I)
        # 如果没有，替换ppv为短横线
        else:
            filename = re.sub(r'\s{0,2}ppv\s{0,2}', '-', filename, flags=re.I)
    # 如果符合fc111111的格式，则替换 fc 为 fc2
    if re.search(r'fc[^2]\d{5,}', filename, re.I):
        filename = filename.replace('fc', 'fc2-').replace('FC', 'FC2-')

    def regular_id(st) -> str:
        """
        提取带 -或者_的
        提取特定番号
        这里采用严格字符数量的匹配方法，感觉很容易误触
        """
        search_regex = [
            r'FC2[-_]\d{6,}',  # fc2-111111
            r'[a-z]{2,5}[-_]\d{3}',  # bf-123 abp-454 mkbd-120  kmhrs-026
            r'[a-z]{4}[-_][a-z]\d{3}',  # mkbd-s120
            r'\d{6,}[-_][a-z]{4,}',  # 111111-MMMM
            r'\d{6,}[-_]\d{3,}',  # 111111-111
            r'n[-_]*[1|0]\d{3}'  # 有短横线，n1111 或者n-1111
        ]
        for regex in search_regex:
            searchobj = re.search(regex, st, flags=re.I)
            if searchobj:
                return searchobj.group()
            else:
                continue

    def no_line_id(st) -> str:
        """
        提取不带 -或者_的
        应该只有几种不带横线，
        """
        search_regex = [
            r'[a-z]{2,5}\d{3}',  # bf123 abp454 mkbd120  kmhrs026
            r'\d{6,}[a-z]{4,}',  # 111111MMMM
        ]
        for regex in search_regex:
            searchobj5 = re.search(regex, st, flags=re.I)
            if searchobj5:
                # 进一步判断数字在前还是字母在前
                num = re.search(r'^\d{3,}', searchobj5.group())
                char = re.findall(r'[a-z]+', searchobj5.group(), flags=re.I)[0]
                if num:
                    return num.group() + '-' + char
                else:
                    return char + '-' + re.search(r'\d+', searchobj5.group()).group()
            else:
                continue

    # 最简单的还是通过 - _ 来分割判断
    if '-' in filename or '_' in filename:
        filename = regular_id(filename)
        if filename:
            return filename
    else:
        # n1111
        searchobj4 = re.search(r'n[1|0]\d{3}', filename, flags=re.I)
        if searchobj4:
            return searchobj4.group()

        filename = no_line_id(filename)
        if filename:
            return filename
        else:
            logger.warning(f'fail to match id: \n{filename}\n try input manualy')
            return input()


def create_folder(search_path, needed_create):
    """
    create failed folder
    Args:
        needed_create:
        search_path:
    """
    folder = Path(needed_create).resolve()

    # 如果配置文件中路径不是绝对路径
    if not folder.is_absolute():
        created = search_path.parents.joinpath(needed_create)
        return mkdir(created)
    else:
        return mkdir(folder)


def get_video_path_list(search_path, cfg):
    """
    search video according to path, exclude excluded folder
    Args:
        search_path: 需要搜寻的文件夹
        cfg: config

    Returns: 文件地址你表

    """
    file_type = cfg.common.file_type
    # 完整排除文件夹的路径
    excluded = [search_path.joinpath(e) for e in cfg.exclude.folders]
    # suffix 获取后缀
    # parents 获取所有父级文件夹
    # 如果在需要搜索的文件中，文件符合格式后缀，且该文件的所有父级文件夹不在排除文件夹中，则为需要的文件
    # （感觉这个写法开销是很大的，需要改进，且有滥用列表生成式的问题）
    return [f for f in search_path.rglob('*') if f.suffix in file_type and not [n for n in excluded if n in f.parents]]


def check_data_state(data) -> object:
    """
    check main metadata
    """
    if not data.title or data.title == "null":
        return False
    if not data.id or data.id == "null":
        return False
    else:
        return True


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
    # # Remove illegal characters
    res = r'[\/\\\:\*\?\"\<\>\|]'
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


def create_folder_move_file(old_file_path, search_path, data, cfg):
    """
    use metadate replace location_rule, create folder
    使用爬取的元数据替换路径规则，再创建文件。
    根据 / 划分层级，检查每层文件夹的名称长度
    Args:
        old_file_path:
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
        output_folder = create_folder(search_path, cfg.name_rule.success_output_folder)
        new_folder = mkdir(output_folder.joinpath(name))
    assert new_folder is not None
    # 替换数据，检查长度，移动和重命名文件，
    # check length of name
    naming_rule = check_name_length(cfg.name_rule.naming_rule, cfg.name_rule.max_title_len)
    new_file_name = replace_date(data, naming_rule)
    new_file_path = new_folder.joinpath(new_file_name)
    mv(old_file_path, new_file_path)
    return new_file_path


def extra_tag(file_path: Path):
    file_name = file_path.name
    if '-cd' in file_name.lower():
        pass
    if '-c.' in file_name.lower() or '中文' in file_name or '字幕' in file_name:
        pass
    if '流出' in file_name:
        pass


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
