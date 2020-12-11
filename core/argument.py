"""
这里放程序运行，只会运行一次的函数
"""

import argparse
import re
import textwrap

from pathlib3x import Path

from utils.config import get_cfg_defaults
from utils.logger import setup_logger

logger = setup_logger()


def set_argparse():
    parser = argparse.ArgumentParser(
        prog="\n\n|> ./cap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.indent("""\

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

    """, '+', lambda line: True))
    parser.add_argument('p', default='G:/a/ARA-460.mp4->ARA-460', nargs='?', help="file->number")
    parser.add_argument('-c', default="config.yaml", help="configuration_file_path")

    return parser.parse_args()


def load_config(parser):
    """
    load default config and merge user config
    Returns:

    """
    # parser = set_argparse()
    # load config file
    cfg = get_cfg_defaults()
    config_file = Path(__file__).parent.parent.joinpath('config.yaml')

    def merge_config(path):
        try:
            cfg.merge_from_file(path)
            logger.info("load config, start searching")
        except Exception as e:
            logger.error(f'config file error:{e}')

    assert isinstance(parser.c, str), 'input must single file->id or single folder'
    if parser.c:
        merge_config(parser.c)
    elif config_file.exists():
        merge_config(str(config_file))
    else:
        logger.info('use defalt config')
    return cfg


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
            r'xxx',
            r'carib '
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
            r'[a-z]{2,5}[-_]\d{2,4}',  # bf-123 abp-454 mkbd-120  kmhrs-026
            r'[a-z]{4}[-_][a-z]\d{3}',  # mkbd-s120
            r'\d{6,}[-_][a-z]{4,}',  # 111111-MMMM
            r'\d{6,}[-_]\d{3,}',  # 111111-111
            r'n[-_]*[1|0]\d{3}'  # 有短横线，n1111 或者n-1111
        ]
        for regex in search_regex:
            searchobj = re.search(regex, st, flags=re.I)
            if searchobj:
                return searchobj.group()
            continue

    def no_line_id(st) -> str:
        """
        提取不带 -或者_的
        应该只有几种不带横线，
        """
        search_regex = [
            r'[a-z]{2,5}\d{2,3}',  # bf123 abp454 mkbd120  kmhrs026
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
                return char + '-' + re.search(r'\d+', searchobj5.group()).group()
            continue

    # 最简单的还是通过 - _ 来分割判断
    if '-' in filename or '_' in filename:
        filename = regular_id(filename)
        if filename:
            return filename
    # n1111
    searchobj4 = re.search(r'n[1|0]\d{3}', filename, flags=re.I)
    if searchobj4:
        return searchobj4.group()

    filename = no_line_id(filename)
    if filename:
        return filename
    logger.warning(f'fail to match id: \n{filename}\n try input manualy')
    return input()


def check_number_parser(target):
    logger.info('file pointing number', extra={'dict': target})
    flag = input('change number(c) or continue(enter) \n')
    if flag.lower() == 'c':
        file_id = input('use [ <Serial_number><space>number ], eg 4 ABP-454\n')
        try:
            target['id'][file_id.split()[0] - 1] = file_id.split()[1]
            check_number_parser(target)
        except KeyError:
            logger.error(f'Syntax error: {file_id}  Check once')
        check_number_parser(target)
    return target


def load_argument():
    parser = set_argparse()
    assert isinstance(parser.p, str), 'input must single file-id or single folder'
    cfg = load_config(parser)

    # split means pointing number
    obj = re.split(r'->', parser.p)
    if len(obj) == 2:
        file = Path(obj[0])
        if file.is_file():
            logger.info(f'The following video: {obj[0]}  {obj[1]} will be searched soon')
            return file, [file], [obj[1]], cfg
        logger.error(f'file path error: {obj[0]}')
    else:
        path = Path(obj[0]).resolve()
        if path.is_dir():
            files = get_video_path_list(path, cfg)
            if len(files) > 0:
                logger.debug(f'the videos in folder: {obj[0]} will be searched soon:',
                             extra={'list': files})
            number = [number_parser(f) for f in files]
            return path, files, number, cfg
        logger.error(f'folder path error: {str(path)}')
