"""
capture single file  according file path and number
根据文件地址和对应编号刮削单个文件
获取元数据 -> 创建文件夹 -> 重命名和移动文件 -> 下载和处理图片 -> 创建 nfo
"""

import asyncio
import time

from core.argument import load_argument, check_number_parser
from core.capbase import get_metadata, folder_utils, file_utils, img_utils, create_nfo
from core.comm import (
    move,
    create_folder,
)
from crawler.registerService import auto_register_service
from utils.logger import setup_logger

logger = setup_logger()


async def start(services, file, number, failed_folder, cfg):
    start_time = time.perf_counter()
    logger.info(f"searching: {number}")
    data = await get_metadata(cfg, services, file, number)
    if not data and not cfg.debug.enable:
        move(file, failed_folder, flag="failed")
    print(data)
    # 伪代码
    created_folder = await folder_utils(data)
    new_file_path = await file_utils(created_folder, data)
    await img_utils(created_folder, data, cfg)
    await create_nfo(new_file_path, data)
    end_time = time.perf_counter() - start_time
    logger.debug(
        f"searching: {number} (took {end_time:0.2f} seconds).")


async def capture():
    # 获取外部输入参数
    folder, file, number, cfg = load_argument()

    # deubg 不创建文件夹
    if not cfg.debug.enable:
        filed_folder = cfg.common.failed_output_folder
        failed = create_folder(folder, filed_folder)
    else:
        failed = None

    # 文件，番号对应
    target = dict(zip(file, number))
    if cfg.debug.check_number_parser:
        target = check_number_parser(target)

    # 自动注册 crawler 文件夹中的爬虫类
    services = auto_register_service()

    # 传入参数，创建任务循环
    tasks = []
    for file, number in target.items():
        tasks.append(start(services, file, number, failed, cfg))
    await asyncio.gather(*tasks)
