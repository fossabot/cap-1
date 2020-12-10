import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from pathlib import Path

from core.cli import (
    load_config,
    check_input
)
from core.comm import (
    number_parser,
    check_data_state,
    extra_tag,
    create_successfull_folder,
    write_nfo,
    rename_move_file
)
from crawler.crawlerCommon import (
    CrawlerCommon,
    WebsitePriority
)
from crawler.registerService import auto_register_service
from utils.logger import setup_logger
from utils.path import PathHandler

thePoolsize = 3

logger = setup_logger()


def thread_pool(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return asyncio.wrap_future(ThreadPoolExecutor(thePoolsize).submit(f, *args, **kwargs))

    return wrap


class CapBase:
    """
    capture single file  according file path and number
    根据文件地址和对应编号刮削单个文件
    获取元数据 -> 创建文件夹 -> 重命名和移动文件 -> 下载和处理图片 -> 创建 nfo
    """

    def __init__(
            self, file: Path, number: str, search_folder: Path, failed_folder: Path, cfg
    ):
        """
        Args:
            file: 原文件地址
            number: 番号
            search_folder: 搜索地址，单文件搜索即为文件地址，否则为文件夹地址
            failed_folder: 创建的失败文件夹地址
            cfg: 配置
        """
        self.file = file
        self.number = number
        self.search_folder = search_folder
        self.failed_folder = failed_folder
        self.cfg = cfg

    @classmethod
    def parameter(cls, file, number, search_folder, failed_folder, cfg):
        return cls(file, number, search_folder, failed_folder, cfg)

    @thread_pool
    def get_metadata(self):
        """
        get metadata from website according to number
        根据编号从网站爬取元数据
        依次从各个网站中爬取，根据特定编号排列优先级
        Returns: metadata

        """
        # priority init， get sorted website
        priority = WebsitePriority(self.cfg.priority.website)
        # priority.sort_website(self.number)
        # 自动注册 crawler 文件夹中的爬虫类
        services = auto_register_service()
        while not priority.empty():
            # noinspection PyBroadException
            try:
                data = services.get(priority.pop(), self.number, self.cfg)
                if check_data_state(data):
                    data = extra_tag(self.file, data)
                    return data
                continue
            # 这里太宽泛了，很容易跳到这里，添加 finally 来移动文件夹。
            except Exception as exc:
                logger.error(f'No data obtained: {exc}')
                continue

    @thread_pool
    def folder_utils(self, data):
        """
        use metadate replace location_rule, create folder
        使用爬取的元数据替换路径规则，再创建文件。
        根据 / 划分层级，检查每层文件夹的名称长度
        """
        return create_successfull_folder(self.search_folder, data, self.cfg)

    @thread_pool
    def file_utils(self, created_folder, data):
        """
        重命名和移动文件
        Args:
            created_folder:
            data:

        Returns:

        """
        return rename_move_file(self.file, created_folder, data, self.cfg)

    @thread_pool
    def img_utils(self, created_folder: Path, data):
        """
        download and process pic
        处理和下载图片
        Args:
            data:
            created_folder: 已创建的文件夹地址
        """
        request = CrawlerCommon(self.cfg)
        # 伪代码
        img_url = {'poster': data.poster, 'thumb': data.thumb, 'fanart': data.fanart}
        for name, url in img_url.items():
            request.download(url, created_folder.joinpath(name + 'jpg'))
        # //TODO 裁剪，水印

    @thread_pool
    def create_nfo(self, new_file_path: Path, data):
        """
        创建 nfo 文件
        Args:
            data:
            new_file_path: 用于 nfo 名称和 nfo文件位置
        """

        write_nfo(new_file_path, data, self.cfg)


class Cap(CapBase):

    async def chain(self) -> None:
        start_time = time.perf_counter()
        logger.info(f'searching: {self.number}')
        data = await self.get_metadata()
        print(data)
        # created_folder = await self.folder_utils(data)
        # new_file_path = await self.file_utils(created_folder, data)
        # await self.img_utils(created_folder, data)
        # await self.create_nfo(new_file_path, data)
        end_time = time.perf_counter() - start_time
        logger.debug(f"searching: {self.number} (took {end_time:0.2f} seconds).")


class Capture:

    def __init__(self):
        """
        判断传入类型
        """
        self.cfg = load_config()
        target = check_input(self.cfg)

        if 'file' in target:
            self.file = target['file']
            self.number = target['number']
            self.folder = self.file
        else:
            self.folder, = target
            self.file, = target.values()
            self.number = [number_parser(f) for f in self.file]

        if not self.cfg.common.debug:
            filed_folder = self.cfg.common.failed_output_folder
            self.failed = PathHandler.create_folder(self.folder, filed_folder)
        else:
            self.failed = ''

    async def start(self):
        tasks = []
        print(self.file)
        print(self.number)
        target = dict(zip(self.file, self.number))
        for file, number in target.items():
            tasks.append(Cap.parameter(file, number, self.folder, self.failed, self.cfg).chain())
        await asyncio.gather(*tasks)
