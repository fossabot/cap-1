import concurrent.futures
from pathlib import Path

from core.comm import (
    number_parser,
    create_folder,
    check_data_state,
    mv,
    create_folder_move_file,
    write_nfo
)
from crawler.crawlerCommon import (
    CrawlerCommon,
    WebsitePriority
)
from crawler.registerService import auto_register_service
from utils.logger import Logger

thePoolsize = 5

logger = Logger()


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
        priority.sort_website(self.number)
        # 自动注册 crawler 文件夹中的爬虫类
        services = auto_register_service()
        while not priority.empty():
            # noinspection PyBroadException
            try:
                self.data = services.get(priority.pop(), self.number, self.cfg)
                if check_data_state(self.data):
                    break
                else:
                    continue
            # 这里太宽泛了，很容易跳到这里，添加 finally 来移动文件夹。
            except Exception as exc:
                logger.error(f'No data obtained: {exc}')
                continue
            finally:
                if not self.data:
                    mv(self.file, self.failed_folder, flag='fail')
                else:
                    pass

    def folder_file_utils(self) -> Path:
        """
        use metadate replace location_rule, create folder
        使用爬取的元数据替换路径规则，再创建文件。
        根据 / 划分层级，检查每层文件夹的名称长度
        """
        return create_folder_move_file(self.file, self.search_path, self.data, self.cfg)

    def img_utils(self, created_folder: Path):
        """
        download and process pic
        处理和下载图片
        Args:
            created_folder:
        """
        request = CrawlerCommon(self.cfg)
        img_url = {'poster': self.data.poster, 'thumb': self.data.thumb, 'fanart': self.data.fanart}
        for name, url in img_url.items():
            request.download(url, created_folder.joinpath(name + 'jpg'))

    def create_nfo(self, new_file_path: Path):
        """
        创建 nfo 文件
        Returns:
            object:
        """

        return write_nfo(new_file_path, self.data, self.cfg)

    def __call__(self):
        self.get_metadata()
        # if data:
        #     print(f'test only title: {data.title}')
        # else:
        #     pass
        new_file_path: Path = self.folder_file_utils
        self.img_utils(new_file_path.parents)
        self.create_nfo(new_file_path)


class Cap:
    def __init__(self, target, cfg):
        if isinstance(target, list):
            self.file = target[0]
            self.id = target[1]

        if isinstance(target, dict):
            self.folder, = target
            self.files, = target.values()
            self.ids = [number_parser(f) for f in self.files]
        self.cfg = cfg
        self.failed = self.failed_folder()

    def failed_folder(self):
        if not self.cfg.common.debug:
            if hasattr(self, 'folder'):
                return create_folder(self.folder, self.cfg)
            else:
                return create_folder(self.file, self.cfg)

    def check_number_parser(self, target):
        logger.info('file pointing number', extra={'dict': target})
        flag = input('change number(c) or continue(enter) \n')
        if flag.lower() == 'c':
            file_id = input('use [ <Serial_number><space>number ], eg 4 ABP-454\n')
            try:
                target['id'][file_id.split()[0] - 1] = file_id.split()[1]
                self.check_number_parser(target)
            except KeyError:
                raise
        else:
            return target

    def mutil_process(self, target):
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=thePoolsize) as pool:
            for f, n in target.items():
                cap = CapBase(file_path=f,
                              number=n,
                              search_path=self.folder,
                              failed_folder_path=self.failed,
                              cfg=self.cfg)
                futures.append(pool.submit(cap()))

    def start(self):
        if hasattr(self, 'file'):
            cap = CapBase(file_path=self.file,
                          number=self.id,
                          search_path=self.file,
                          failed_folder_path=self.failed,
                          cfg=self.cfg)
            return cap()
        else:
            target = dict(zip(self.files, self.ids))
            if self.cfg.debug.check_number_parser:
                target = self.check_number_parser(target)
                self.mutil_process(target)
