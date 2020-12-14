import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

from core.comm import check_name_length, replace_date, move, mkdir
from core.metadata import sort_website, check_data_state, extra_tag
from crawler.crawlerComm import DownloadImg
from utils.logger import setup_logger

logger = setup_logger()

thePoolsize = 3


def thread_pool(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return asyncio.wrap_future(
            ThreadPoolExecutor(thePoolsize).submit(f, *args, **kwargs)
        )

    return wrap


@thread_pool
def get_metadata(services, file, number, cfg):
    """
    get metadata from website according to number
    根据编号从网站爬取元数据
    依次从各个网站中爬取，根据特定编号排列优先级
    Returns: metadata
    """
    # priority init， get sorted website
    priority = sort_website(number, cfg.priority.website)
    # priority.sort_website(self.number)
    while not priority.empty():
        # noinspection PyBroadException
        try:
            data = services.get(priority.pop(), number, cfg)
            if check_data_state(data):
                return extra_tag(file, data)
            continue
        except Exception as exc:
            logger.error(f"No data obtained: {exc}")


@thread_pool
def file_utils(file, created_folder, data, cfg):
    """
    重命名和移动文件
    Returns: 重命名和移动之后的文件地址

    """
    # 替换数据，检查长度，移动和重命名文件，
    # check length of name
    naming_rule = check_name_length(
        cfg.name_rule.naming_rule, cfg.name_rule.max_title_len
    )
    file_name = replace_date(data, naming_rule)

    for mark in data.extra.values():
        file_name += "-" + mark

    file_name += file.suffix
    new_file_path = created_folder.joinpath(file_name)
    move(file, new_file_path)
    return new_file_path


@thread_pool
def folder_utils(cfg, search_path, data):
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
    if len(data.actor.split(",")) >= 5:
        data.actor = ",".join(data.actor.split(",")[:2]) + "etc."
    location_rule = replace_date(data, cfg.name_rule.location_rule)
    # mkdir folder by level
    new_folder = None
    for name in location_rule.split("/"):
        name = check_name_length(name, cfg.name_rule.max_title_len)
        output_folder = folder_utils(
            search_path, cfg.name_rule.success_output_folder, cfg
        )
        new_folder = mkdir(output_folder.joinpath(name))
    return new_folder


@thread_pool
def img_utils(created_folder: Path, data, cfg):
    """
    download and process pic
    处理和下载图片
    Args:
        cfg:
        data:
        created_folder: 已创建的文件夹地址
    """
    request = DownloadImg(cfg)
    # 伪代码
    img_url = {"poster": data.poster,
               "thumb": data.thumb, "fanart": data.fanart}
    request.download_all(img_url, created_folder)
    # //TODO 裁剪，水印


@thread_pool
def create_nfo(file_path: Path, data, cfg):
    """
    //TODO fields写完
    Args:
        cfg:
        file_path:
        data:
    """
    nfo_root = Element("movie")
    folder = Path(file_path).parent
    filename = folder.joinpath(Path(file_path).with_suffix(".nfo"))
    nfo_fields = dict
    if cfg.common.mode == "":
        nfo_fields = {
            "title": data.title,
            "studio": data.studio,
            "year": data.year,
            "tag": data.tag,
        }
    for field_name, values in nfo_fields.items():
        if not values:
            continue
        if not isinstance(values, list):
            values = [values]
        for value in values:
            SubElement(nfo_root, field_name).text = f"{value}"

    ElementTree(nfo_root).write(
        filename, encoding="utf-8", xml_declaration=True)
