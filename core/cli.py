import argparse
import os
import textwrap
from config.config import get_cfg_defaults
from core.common import get_video_path_list
from utils.logger import Logger

logger = Logger()


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
    > ./cap file_path->number

    ¶ specifying configuration files is no problem either.
    > ./cap -c configuration_file

    ¶ actually, you can still do this.
    > ./cap file_path->number another_file_path->number

    ¶ if you want, that's fine too.
    > ./cap folder_path another_folder_path

    """, '+', lambda line: True))
    parser.add_argument('p', default=[], nargs='*', help="file_path->number")
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
    if not os.path.isfile("config/config.yaml"):
        logger.info("use default config")
    else:
        try:
            cfg.merge_from_file(parser.c)
            logger.info("load config，start searching")
        except Exception as e:
            print(e)
            logger.error('config file error')
    return cfg


def check_input(cfg):
    """
    sort command line input
    Args:
        cfg: config

    Returns:

    """
    parser = set_argparse()
    file, numbers, folder = [], [], []
    for i in parser.p:
        # split means pointing number
        try:
            file, number = i.split('->')
            if os.path.isfile(file):
                file.append(file)
                numbers.append(number)
                logger.info("The following videos will be searched soon：")
                print(*("\n[" + os.path.split(i)[1] + "]\n" for i in file), sep='\n')
                return {"file": file, "number": numbers}
            else:
                logger.info("file path error: {}".format(i))
        except ValueError:
            if os.path.isdir(i):
                folder.append(i) if os.path.isdir(
                    i) else logger.info("folder path error")
                logger.info("the videos in the following folders will be searched soon：")
                print(*("\n[" + i + "]\n" for i in folder), sep='\n')
                return get_video_path_list(folder, cfg)
            else:
                logger.info("folder path error: {}".format(i))


if __name__ == "__main__":
    load_config()
    # input_ = check_input(cfg)
