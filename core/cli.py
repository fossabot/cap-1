import argparse
import re
import textwrap
from pathlib import Path

from config.config import get_cfg_defaults
from core.comm import get_video_path_list
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


def load_config():
    """
    load default config and merge user config
    Returns:

    """
    parser = set_argparse()
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


def check_input(cfg):
    """
    sort command line input
    Args:
        cfg: config
    Returns:
    """
    parser = set_argparse()
    assert isinstance(parser.p, str), 'input must single file-id or single folder'
    # split means pointing number
    obj = re.split(r'->', parser.p)
    if len(obj) == 2:
        file = Path(obj[0])
        if file.is_file():
            logger.info(f'The following video: {obj[0]}  {obj[1]} will be searched soon')
            return {'file': [file], 'number': [obj[1]]}
        logger.info(f'file path error: {obj[0]}')
    else:
        path = Path(obj[0]).resolve()
        if path.is_dir():
            files = get_video_path_list(path, cfg)
            if len(files) > 0:
                logger.debug(f'the videos in folder: {obj[0]} will be searched soon:',
                             extra={'list': files})
            return {path: files}
        logger.info(f'folder path error: {str(path)}')


if __name__ == "__main__":
    load_config()
    # input_ = check_input(cfg)
