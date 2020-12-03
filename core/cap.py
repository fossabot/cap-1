import shutil
from pathlib import Path
from core.common import (
    number_parser,
    create_failed_folder,
    check_data_state,
    replace_date,
    check_name_length,
    move_to_failed_folder,
    write_nfo
)
from crawler.crawlerCommon import (
    CrawlerCommon,
    WebsitePriority
)
from crawler.registerService import auto_register_service
from utils.logger import Logger

logger = Logger()
try:
    import concurrent.futures
except ImportError as e:
    # print (e)
    import threading

    poolSupport = False
else:
    poolSupport = True


class CapBase:
    """
    capture single file  according file path and number
    根据文件地址和对应编号刮削单个文件
    获取元数据 -> 创建文件夹 -> 重命名和移动文件 -> 下载和处理图片 -> 创建 nfo
    """

    def __init__(self, path, number, cfg):
        self.file_path: str = path
        self.number: str = number
        self.data = None
        self.cfg = cfg
        if not self.cfg.common.debug:
            create_failed_folder(self.cfg)

    @property
    def get_metadata(self):
        """
        get metadata from website according to number
        根据编号从网站爬取元数据
        依次从各个网站中爬取，根据特定编号排列优先级
        Returns: metadata

        """
        # priority init， get sorted website
        priority = WebsitePriority(self.cfg.priority.website)
        # 自动注册 crawler 文件夹中的爬虫类
        services = auto_register_service()
        while not priority.empty():
            try:
                self.data = services.get(priority.pop(), self.number, self.cfg)
                if check_data_state(self.data):
                    return self.data
                else:
                    continue
            finally:
                move_to_failed_folder(self.file_path, self.cfg)
                logger.error("No data obtained")

    def create_folder(self, data):
        """
        use metadate replace location_rule, create folder
        使用爬取的元数据替换路径规则，再创建文件。
        根据 / 划分层级，检查每层文件夹的名称长度
        Args:
            data: metadata
        """
        location_rule = self.cfg.name_rule.location_rule
        # If the number of actors is more than 5, take the first two
        # 如果演员数量大于5 ，则取前两个
        if len(data.actor.split(',')) >= 5:
            data.actor = ','.join(data.actor.split(',')[:2]) + 'etc.'
        # replace data
        location_rule = replace_date(data, location_rule)
        # mkdir folder by level
        for name in location_rule.split('/'):
            # check length of name
            name = check_name_length(name, self.cfg.name_rule.max_title_len)
            output_folder = Path(self.cfg.name_rule.success_output_folder).resolve()
            folder_path = output_folder.joinpath(name)
            try:
                folder_path.mkdir(exist_ok=True)
                # logger.info("mkdir folder %s".format(folder_path))
                return folder_path
            except OSError:
                logger.info("fail to mkdir folder: %s".format(folder_path))

    def move_rename_video(self, folder_path, data):
        """
        替换数据，检查长度，移动和重命名文件，
        Args:
            folder_path:
            data:
        """
        # check length of name
        naming_rule = check_name_length(self.cfg.name_rule.naming_rule, self.cfg.name_rule.max_title_len)
        # replace data ,get new file name
        new_file_name = replace_date(data, naming_rule)
        new_file_path = Path(folder_path).joinpath(new_file_name)
        try:
            shutil.move(self.file_path, new_file_path)
            logger.info("move: {} to folder: {} ".format(self.file_path, folder_path))
        except Exception as exc:
            logger.error("fail to move" + str(exc))

        return new_file_name

    def img_utils(self, created_folder, metadata):
        """
        download and process pic
        处理和下载图片
        Args:
            created_folder:
            metadata:
        """
        # //TODO 图片下载
        request = CrawlerCommon(self.cfg)
        request.download(metadata.poster, Path(created_folder).joinpath('poster.name'))

    def create_nfo(self, new_file_name, metadata):
        """
        创建 nfo 文件
        Returns:
            object:
        """
        return write_nfo(new_file_name, metadata, self.cfg)

    def __call__(self):
        metadata = self.get_metadata
        if not self.cfg.common.debug:
            created_folder = self.create_folder(metadata)
            new_file_name = self.move_rename_video(created_folder, metadata)
            self.img_utils(created_folder, metadata)
            self.create_nfo(new_file_name, metadata)


class Cap:
    def __init__(self, target, cfg):
        if isinstance(target, dict):
            self.files = target['file']
            self.id = target['id']
        if isinstance(target, list):
            self.files = target
            self.id = [number_parser(f) for f in target]
        self.cfg = cfg
        # if self.cfg.proxy.enablefree:
        #     self.cfg = free_proxy_pool(cfg)

    def process(self):
        target = dict(zip(self.files, self.id))
        for f, n in target.items():
            cap = CapBase(f, n, self.cfg)
            cap()
