import shutil

from pathlib3x import Path

from utils.logger import setup_logger

logger = setup_logger()


class PathHandler:
    def __int__(self):
        self.log = setup_logger()

    @staticmethod
    def move(src: Path, dest: Path, flag: str = None):
        """
        移动文件
        Args:
            src:
            dest:
            flag: faild or successfull
        """
        assert src.exists()
        try:
            shutil.move(src, dest)
            logger.info(f'move {src.name} to {flag} folder')
        except Exception as exc:
            logger.error(f'fail to move file: {str(exc)}')

    @staticmethod
    def mkdir(src: Path):
        """
        创建文件夹，并返回已创建的文件夹
        Args:
            src:

        Returns:

        """
        assert src.exists()
        try:
            src.mkdir()
            logger.info(f'succeed create folder: {src.as_posix()}')
            return src
        except Exception as exc:
            logger.error(f'fail to create folder: {str(exc)}')

    def symlink(self):

        raise NotImplementedError()

    @staticmethod
    def create_folder(search_path: Path, needed_create: str):
        """
        根据相对路径和绝对路径创建文件夹
        Args:
            search_path:
            needed_create:

        Returns:

        """
        folder = Path(needed_create).resolve()
        if not folder.is_absolute():
            created = search_path.parent.joinpath(needed_create)
            return PathHandler.mkdir(created)
        return PathHandler.mkdir(folder)
