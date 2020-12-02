import copy
import logging
import os.path
import sys
import time

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
            new_record.levelname = "{color_begin}{level}{color_end}".format(
                level=new_record.levelname,
                color_begin=LOG_COLORS[new_record.levelno],
                color_end=colorama.Style.RESET_ALL,
            )
        # now we can let standart formatting take care of the rest
        return super(ColorFormatter, self).format(new_record)


class Logger(object):
    def __init__(self):
        """
        指定保存日志的文件路径，日志级别，以及调用文件
        将日志存入到指定的文件中
        """

        # 创建一个logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)  # 指定最低的日志级别 critical > error > warning > info > debug

        # 创建一个handler，用于写入日志文件
        log_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        # log_path = os.getcwd() + "/logs/"
        log_path = os.path.split(os.path.dirname(__file__))[0]
        log_name = os.path.join(log_path, "{}.log".format(log_time))
        #  这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志，解决重复打印的问题
        if not self.logger.handlers:
            # 写入日志文件
            fh = logging.FileHandler(log_name, 'a', encoding='utf-8')  # 追加模式  这个是python2的
            fh.setLevel(logging.DEBUG)

            fh_formatter = logging.Formatter(
                '[%(asctime)s] %(filename)s->%(funcName)s line:%(lineno)d [%(levelname)s]%(message)s')
            fh.setFormatter(fh_formatter)

            # 创建一个handler，用于输出到控制台
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            # 定义handler的输出格式, 控制台输出使用 ColorFormatter
            formatter = ColorFormatter("%(levelname)s %(message)s")
            ch.setFormatter(formatter)

            # 给logger添加handler
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def debug(self, msg):
        self.logger.debug(str(msg))

    def info(self, msg):
        self.logger.info(str(msg))

    def warning(self, msg):
        self.logger.warning(str(msg))

    def error(self, msg):
        self.logger.error(str(msg))

    def critical(self, msg):
        self.logger.critical(str(msg))


if __name__ == '__main__':
    log = Logger()
    log.debug("debug")
    log.info("info")
    log.error("error")
    log.warning("warning")
    log.critical("critical")
