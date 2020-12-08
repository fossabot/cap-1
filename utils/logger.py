import copy
import logging
import sys
import time
from pathlib import Path

import colorama

# specify colors for different logging levels
LOG_COLORS = {
    logging.ERROR: colorama.Fore.RED,
    logging.WARNING: colorama.Fore.YELLOW,
    logging.DEBUG: colorama.Fore.WHITE,
    logging.INFO: colorama.Fore.GREEN,
    logging.CRITICAL: colorama.Fore.MAGENTA,
}


class ColorFormatter(logging.Formatter):
    def format(self, record, *args, **kwargs):
        # if the corresponding logger has children, they may receive modified
        # record, so we want to keep it intact
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
            # we want levelname to be in different color, so let's modify it
            new_record.levelname = "{color_begin}{level:8s}{color_end}".format(
                level=new_record.levelname,
                color_begin=LOG_COLORS[new_record.levelno],
                color_end=colorama.Style.RESET_ALL,
            )
        # now we can let standart formatting take care of the rest
        return super(ColorFormatter, self).format(new_record)


class ListFilter(logging.Filter):
    """
    # https://stackoverflow.com/questions/22934616/multi-line-logging-in-python
    The other optional keyword argument is extra which can be used to pass a dictionary
    which is used to populate the __dict__ of the LogRecord created for the logging event with user-defined attributes.
    """

    def filter(self, record):
        # extra = {'list': List}
        # 闲着没事，顺便画了个方框
        # 增加 map(str, record.list),很大概率传入 Path 对象
        if hasattr(record, 'list'):
            width = max(map(len, list(map(str, record.list))))
            record.msg = record.msg + f'\n{"+ "}{"-" * width}{" +"}\n'
            record.msg += ''.join([f'|{" "}{line:<{width}}{" "}|\n' for line in list(map(str, record.list))])
            record.msg = record.msg + f'{"+ "}{"-" * width}{" +"}'
        # extra = {'dict': Dict}
        # 用 count 记数，增加序号，用于检查番号提取（特定需求）
        if hasattr(record, 'dict'):
            count = 1
            for k, v in record.dict.items():
                record.msg += f'\n No.{count} file: {k} -> id: {v} '
                count += 1
        return super(ListFilter, self).filter(record)


class Logger:
    def __init__(self):
        """
        指定保存日志的文件路径，日志级别，以及调用文件
        日志等级 debug 只写入log文件，其他都会在控制台打印
        只有控制台输出有颜色
        """

        # 创建一个logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # 指定最低的日志级别 critical > error > warning > info > debug

        # 创建一个handler，用于写入日志文件
        log_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        log_name = Path(__file__).parent.parent.joinpath("{}.log".format(log_time))
        #  这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志，解决重复打印的问题
        if not self.logger.handlers:
            # FileHandler
            fh = logging.FileHandler(log_name, 'a', encoding='utf-8')
            fh.setLevel(logging.DEBUG)

            fh_formatter = logging.Formatter(
                '[%(asctime)s] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s] %(message)s')
            fh.setFormatter(fh_formatter)
            # StreamHandler
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.INFO)
            # 定义handler的输出格式, 控制台输出使用 ColorFormatter
            formatter = ColorFormatter('%(levelname)s %(message)s')
            ch.setFormatter(formatter)
            # 按行打印 list

            # 给logger添加handler
            self.logger.addFilter(ListFilter())
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(str(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(str(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(str(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(str(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(str(msg), *args, **kwargs)


if __name__ == '__main__':
    log = Logger()
    # d = {'list': ['str1', 'str2', 'str3']}
    d = {'dict': {'one': 'test_one', 'two': 'test_two'}}
    log.info("This shows extra", extra=d)
    # log.debug("info")
    # log.error("error")
    # log.warning("warning")
    # log.critical("critical")
