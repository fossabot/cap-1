import re

from utils.logger import setup_logger

logger = setup_logger()


def del_extra(st) -> str:
    """
    删除cd1.. ，时间戳,
    """
    regex_list = [
        # r'[\u4e00-\u9fa5]+',
        # r'[^A-Za-z0-9-_.()]',
        r"cd\d$",  # 删除cd1
        r"-\d{4}-\d{1,2}-\d{1,2}",  # 日期
        r"\d{4}-\d{1,2}-\d{1,2}-",
        r"1080p",
        r"1pon",
        r".com",
        r"nyap2p",
        r"22-sht.me",
        r"xxx",
        r"carib ",
    ]
    for regex in regex_list:
        st = re.sub(regex, "", st, flags=re.I)
    st = st.rstrip("-cC ")
    return st


def regular_id(st) -> str:
    """
    提取带 -或者_的
    提取特定番号
    这里采用严格字符数量的匹配方法，感觉很容易误触
    """
    search_regex = [
        r"FC2[-_]\d{6,}",  # fc2-111111
        r"[a-z]{2,5}[-_]\d{2,4}",  # bf-123 abp-454 mkbd-120  kmhrs-026
        r"[a-z]{4}[-_][a-z]\d{3}",  # mkbd-s120
        r"\d{6,}[-_][a-z]{4,}",  # 111111-MMMM
        r"\d{6,}[-_]\d{3,}",  # 111111-111
        r"n[-_]*[1|0]\d{3}",  # 有短横线，n1111 或者n-1111
    ]
    for regex in search_regex:
        searchobj = re.search(regex, st, flags=re.I)
        if searchobj:
            return searchobj.group()
        continue


def no_line_id(st) -> str:
    """
    提取不带 -或者_的
    应该只有几种不带横线，
    """
    search_regex = [
        r"[a-z]{2,5}\d{2,3}",  # bf123 abp454 mkbd120  kmhrs026
        r"\d{6,}[a-z]{4,}",  # 111111MMMM
    ]
    for regex in search_regex:
        searchobj = re.search(regex, st, flags=re.I)
        if searchobj:
            # 进一步判断数字在前还是字母在前
            num = re.search(r"^\d{3,}", searchobj.group())
            char = re.findall(r"[a-z]+", searchobj.group(), flags=re.I)[0]
            if num:
                return num.group() + "-" + char
            return char + "-" + re.search(r"\d+", searchobj.group()).group()


def luxu(filename):
    searchobj = re.search(r"\d{0,3}luxu[-_]\d{4}", filename, re.I)
    if searchobj:
        return searchobj.group()


def fc2(filename):
    if "fc2" in filename.lower() and "ppv" in filename.lower():
        # 如果有短横线，则删除 ppv
        if re.search(r"ppv\s*[-|_]\s*\d{6,}", filename, flags=re.I):
            filename = re.sub(r"ppv", "", filename, flags=re.I)
        # 如果没有，替换ppv为短横线
        filename = re.sub(r"\s{0,2}ppv\s{0,2}", "-", filename, flags=re.I)
    # 如果符合fc111111的格式，则替换 fc 为 fc2

    if re.search(r"fc[^2]\d{5,}", filename, re.I):
        filename = filename.replace("fc", "fc2-").replace("FC", "FC2-")

    return filename


def number_parser(filename):
    """
    提取番号
    又在 btsow 上抓了一些 Hot Tags 页面的番号，测试一下
    正则也不会，感觉这段写的好蠢，开销大不大的
    Args:
        filename:

    Returns:

    """
    # 删除多余内容
    filename = del_extra(filename.stem)

    # 提取欧美番号 sexart.11.11.11, 尽可能匹配人名
    searchobj1 = re.search(r"^\D+\d{2}\.\d{2}\.\d{2}", filename)
    if searchobj1:
        r_searchobj1 = re.search(r"^\D+\d{2}\.\d{2}\.\d{2}\.\D+", filename)
        if r_searchobj1:
            return r_searchobj1.group()
        return searchobj1.group()

    # 提取xxx-av-11111
    searchobj2 = re.search(r"XXX-AV-\d{4,}", filename.upper())
    if searchobj2:
        return searchobj2.group()

    # n1111
    searchobj3 = re.search(r"n[1|0]\d{3}", filename, flags=re.I)
    if searchobj3:
        return searchobj3.group()

    # 提取luxu
    if "luxu" in filename.lower():
        return luxu(filename)
    # fc2
    filename = fc2(filename)

    # 最简单的还是通过 - _ 来分割判断
    if "-" in filename or "_" in filename:
        filename = regular_id(filename)
        if filename:
            return filename

    filename = no_line_id(filename)

    if filename:
        return filename
    logger.warning(f"fail to match id: \n{filename}\n try input manualy")
    return input()
