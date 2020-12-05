from pathlib import Path

from core.comm import (
    number_parser,
    create_failed_folder,
    check_data_state,
    replace_date,
    check_name_length,
    mv,
    mkdir,
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
except ImportError:
    # print (e)
    import threading

    poolSupport = False
else:
    poolSupport = True

thePoolsize = 5


class CapBase:
    """
    capture single file  according file path and number
    根据文件地址和对应编号刮削单个文件
    获取元数据 -> 创建文件夹 -> 重命名和移动文件 -> 下载和处理图片 -> 创建 nfo
    """

    def __init__(self, path, number, folder, cfg):
        self.file = path
        self.number: str = number
        self.data = None
        self.folder = folder
        self.cfg = cfg

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
            # noinspection PyBroadException
            try:
                self.data = services.get(priority.pop(), self.number, self.cfg)
                if check_data_state(self.data):
                    return self.data
                else:
                    continue
            # 这里太宽泛了，很容易跳到这里，添加 finally 来移动文件夹。
            except Exception as exc:
                logger.error(f'No data obtained{exc}')
                continue
            finally:
                if not self.data:
                    mv(self.file, self.folder, flag='fail')
                else:
                    pass

    def create_folder_move_video(self, folder_path, data):
        """
        use metadate replace location_rule, create folder
        使用爬取的元数据替换路径规则，再创建文件。
        根据 / 划分层级，检查每层文件夹的名称长度
        Args:
            folder_path:
            data: metadata
        """
        location_rule = self.cfg.name_rule.location_rule
        naming_rule = self.cfg.name_rule.naming_rule
        max_title_len = self.cfg.name_rule.max_title_len
        # If the number of actors is more than 5, take the first two
        # 如果演员数量大于5 ，则取前两个
        if len(data.actor.split(',')) >= 5:
            data.actor = ','.join(data.actor.split(',')[:2]) + 'etc.'
        # replace data
        location_rule = replace_date(data, location_rule)
        # mkdir folder by level
        for name in location_rule.split('/'):
            # check length of name
            name = check_name_length(name, max_title_len)
            output_folder = Path(self.cfg.name_rule.success_output_folder).resolve()
            folder_path = output_folder.joinpath(name)
            mkdir(folder_path)

        # 替换数据，检查长度，移动和重命名文件，
        # check length of name
        naming_rule = check_name_length(naming_rule, max_title_len)
        new_file_name = replace_date(data, naming_rule)
        mv(self.file, folder_path.joinpath(new_file_name))
        return new_file_name

    def img_utils(self, created_folder: Path, metadata):
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

    def create_nfo(self, new_file_name: Path, metadata):
        """
        创建 nfo 文件
        Returns:
            object:
        """
        return write_nfo(new_file_name, metadata, self.cfg)

    def __call__(self):
        # metadata = self.get_metadata
        # if not self.cfg.common.debug:
        #     created_folder = self.create_folder(metadata)
        #     new_file_name = self.move_rename_video(created_folder, metadata)
        #     self.img_utils(created_folder, metadata)
        #     self.create_nfo(new_file_name, metadata)
        return self.get_metadata


class Cap:
    def __init__(self, target, cfg):
        if isinstance(target, list):
            self.file = target[0]
            self.id = target[1]

        if isinstance(target, dict):
            self.folder, = target
            self.files, = target.values()
            self.ids = [number_parser(f) for f in self.files]

        self.failed = self.failed_folder()
        self.cfg = cfg

    def failed_folder(self):
        if not self.cfg.common.debug:
            if self.folder:
                return create_failed_folder(self.folder, self.cfg)
            else:
                return create_failed_folder(self.file, self.cfg)

    def check_number_parser(self, target):
        logger.info('file pointing number', extra={'dict': target})
        flag = input('change number(c) or continue(enter)?')
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
        # // TODO 多线程要怎么搞呢
        index = 0
        if not poolSupport:
            threads = []
            for f, n in target.items():
                cap = CapBase(f, n, self.failed, self.cfg)
                threads.append(threading.Thread(target=cap()))
                index += 1
            for t in threads:
                t.setDaemon(True)
                t.start()
                t.join()
        else:
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=thePoolsize) as pool:
                for f, n in target.items():
                    cap = CapBase(f, n, self.failed, self.cfg)
                    futures.append(pool.submit(cap()))
                    index += 1
                result = concurrent.futures.wait(
                    futures, timeout=None, return_when='ALL_COMPLETED')
                suc = 0
                for f in result.done:
                    if f.result():
                        suc += 1
                        logger.info('Total number of search: ')

    def start(self):
        if self.file:
            cap = CapBase(self.file, self.id, self.failed, self.cfg)
            return cap()
        else:
            target = dict(zip(self.files, self.ids))
            if self.cfg.debug.check_number_parser:
                target = self.check_number_parser(target)
                self.mutil_process(target)
