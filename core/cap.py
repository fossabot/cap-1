import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from pathlib import Path

from core.comm import (
    mv,
    number_parser,
    check_number_parser,
    create_folder,
    check_data_state,
    extra_tag,
    create_successfull_folder,
    write_nfo,
    move_file
)
from crawler.crawlerCommon import (
    CrawlerCommon,
    WebsitePriority
)
from crawler.registerService import auto_register_service
from utils.logger import setup_logger

thePoolsize = 3

logger = setup_logger()


def thread_pool(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return asyncio.wrap_future(ThreadPoolExecutor(max_workers=5).submit(f, *args, **kwargs))

    return wrap


class CapBase:
    """
    capture single file  according file path and number
    根据文件地址和对应编号刮削单个文件
    获取元数据 -> 创建文件夹 -> 重命名和移动文件 -> 下载和处理图片 -> 创建 nfo
    """

    def __init__(self,
                 file_path: Path,
                 number: str,
                 search_path: Path,
                 failed_folder_path: Path,
                 cfg):
        """
        Args:
            file_path: 原文件地址
            number: 番号
            search_path: 搜索地址，单文件搜索即为文件地址，否则为文件夹地址
            failed_folder_path: 创建的失败文件夹地址
            cfg: 配置
        """
        self.file = file_path
        self.number = number
        self.search_path = search_path
        self.failed_folder = failed_folder_path
        self.data = None
        self.cfg = cfg

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
                logger.info(f'searching: {self.number}')
                self.data = services.get(priority.pop(), self.number, self.cfg)
                if check_data_state(self.data):
                    self.data = extra_tag(self.file, self.data)
                    break
                continue
            # 这里太宽泛了，很容易跳到这里，添加 finally 来移动文件夹。
            except Exception as exc:
                logger.error(f'No data obtained: {exc}')
                continue

    def folder_utils(self) -> Path:
        """
        use metadate replace location_rule, create folder
        使用爬取的元数据替换路径规则，再创建文件。
        根据 / 划分层级，检查每层文件夹的名称长度
        """
        return create_successfull_folder(self.search_path, self.data, self.cfg)

    def file_utils(self, created_folder) -> Path:

        return move_file(self.file, created_folder, self.data, self.cfg)

    # @thread_pool
    def img_dowload(self, request, created_folder: Path, url, name):
        # request = CrawlerCommon(self.cfg)
        request.download(url, created_folder.joinpath(name + 'jpg'))

    def img_utils(self, created_folder: Path):
        """
        download and process pic
        处理和下载图片
        Args:
            created_folder: 已创建的文件夹地址
        """
        request = CrawlerCommon(self.cfg)
        # 伪代码
        img_url = {'poster': self.data.poster, 'thumb': self.data.thumb, 'fanart': self.data.fanart}
        # tasks = [self.img_dowload(request, created_folder, img_url[key], key) for key in img_url]
        # await asyncio.gather(*tasks)

        # for name, url in img_url.items():
        #     task = asyncio.create_task(self.img_dowload(request, created_folder, url, name))
        #     await task
        #     request.download(url, created_folder.joinpath(name + 'jpg'))
        # //TODO 裁剪，水印

    def create_nfo(self, new_file_path: Path):
        """
        创建 nfo 文件
        Args:
            new_file_path: 用于 nfo 名称和 nfo文件位置
        """

        write_nfo(new_file_path, self.data, self.cfg)

    def run(self):
        self.get_metadata()
        if not self.data:
            mv(self.file, self.failed_folder, flag='fail')

        print(self.data.values())
        # created_folder = self.failed_folder
        # asyncio.run(self.folder_utils())
        # new_file_path = self.file_utils(created_folder)
        # self.create_nfo(new_file_path)


class Cap:
    def __init__(self, target, cfg):
        """
        判断传入类型
        为 list 即单文件搜索
        为 dict 即文件夹搜索，进行番号提取
        Args:
            target: 命令行传入
            cfg:
        """
        if isinstance(target, list):
            self.file = target[0]
            self.id = target[1]

        if isinstance(target, dict):
            self.folder, = target
            self.files, = target.values()
            self.ids = [number_parser(f) for f in self.files]
        self.cfg = cfg
        self.failed = self._failed_folder

    @property
    def _failed_folder(self):
        """
        创建失败文件夹，根据文件和文件夹判断传入路径
        Returns:

        """
        if not self.cfg.common.debug:
            if hasattr(self, 'folder'):
                return create_folder(self.folder, self.cfg)
            return create_folder(self.file, self.cfg)

    def mutile_process(self, target):
        for f, n in target.items():
            cap = CapBase(f, n, self.folder, self.failed, self.cfg)
            cap.run()

    def start(self):
        if hasattr(self, 'file'):
            cap = CapBase(self.file, self.id, self.file, self.failed, self.cfg)
            cap.run()
        target = dict(zip(self.files, self.ids))
        if self.cfg.debug.check_number_parser:
            target = check_number_parser(target)
            self.mutile_process(target)
