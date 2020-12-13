from yacs.config import CfgNode as CN

_C = CN()
# 用户修改设置
_C.common = CN()
_C.common.debug = True
_C.common.main_mode = 1
_C.common.failed_output_folder = "failed"
_C.common.success_output_folder = "output"
_C.common.failed_move = 1
_C.common.auto_exit = 1
_C.common.transalte_to_sc = 1

_C.debug = CN()
_C.debug.enable = True
_C.debug.check_number_parser = True

_C.proxy = CN()
_C.proxy.enable = False
_C.proxy.type = "socks5"
_C.proxy.host = ""

_C.request = CN()
_C.request.status_forcelist = ["413", "429", "500", "502", "503", "504"]
_C.request.timeout = 5
_C.request.total = 3
_C.request.backoff_factor = 1
_C.request.delay = 1
_C.request.javbd_cookie = """"""
_C.request.enable_free_proxy_pool = False
_C.request.free_proxy_pool = []

_C.name_rule = CN()
_C.name_rule.location_rule = "actor/number"
_C.name_rule.naming_rule = "number-title"
_C.name_rule.max_title_len = 50

_C.priority = CN()
_C.priority.website = ["javbus", "javdb", "javstore"]
# , "fanza", "xcity", "mgstage", "fc2", "avsox", "jav321", "javlib", "dlsite"
_C.exclude = CN()
# _C.exclude.literals = "\()/"
_C.exclude.folders = ["failed", "output", "escape"]

# 其他默认设置选项
_C.proxy.support = ["http", "socks5", "socks5h"]
_C.common.file_type = [
    ".mp4",
    ".avi",
    ".rmvb",
    ".wmv",
    ".mov",
    ".mkv",
    ".flv",
    ".ts",
    ".webm",
    ".iso",
]


def get_cfg_defaults():
    """Get a yacs CfgNode object with default values for my_project."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    return _C.clone()


# Alternatively, provide a way to import the defaults as
# a global singleton:
# cfg = _C  # users can `from config import cfg`
