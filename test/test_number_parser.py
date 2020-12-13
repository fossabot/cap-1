import re
import unittest


def number_parser(filename):
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

    filename = del_extra(filename)

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
    # 提取luxu
    if "luxu" in filename.lower():
        searchobj3 = re.search(r"\d{0,3}luxu[-_]\d{4}", filename, re.I)
        if searchobj3:
            return searchobj3.group()
    # 如果有fc2删除 ppv
    if "fc2" in filename.lower() and "ppv" in filename.lower():
        # 如果有短横线，则删除 ppv
        if re.search(r"ppv\s*[-|_]\s*\d{6,}", filename, flags=re.I):
            filename = re.sub(r"ppv", "", filename, flags=re.I)
        # 如果没有，替换ppv为短横线
        filename = re.sub(r"\s{0,2}ppv\s{0,2}", "-", filename, flags=re.I)
    # 如果符合fc111111的格式，则替换 fc 为 fc2
    if re.search(r"fc[^2]\d{5,}", filename, re.I):
        filename = filename.replace("fc", "fc2-").replace("FC", "FC2-")

    def regular_id(st) -> str:
        """
        提取带 -或者_的
        提取特定番号
        这里采用严格字符数量的匹配方法，感觉很容易误触
        """
        search_regex = [
            r"FC2[-_]\d{6,}",  # fc2-111111
            r"[a-z]{2,5}[-_]\d{2,3}",  # bf-123 abp-454 mkbd-120  kmhrs-026
            r"[a-z]{4}[-_][a-z]\d{3}",  # mkbd-s120
            r"\d{6,}[-_][a-z]{4,}",  # 111111-MMMM
            r"\d{6,}[-_]\d{3,}",  # 111111-111
            r"n[-_]*[1|0]\d{3}",
        ]
        for regex in search_regex:
            searchobj = re.search(regex, st, flags=re.I)
            if searchobj:
                return searchobj.group()
            continue

    def no_line_id(st) -> str:
        """
        提取不带 -或者_的
        应该只有集中不带横线，
        """
        search_regex = [
            r"[a-z]{2,5}\d{2,3}",  # mkbd120 bf123
            r"\d{6,}[a-z]{4,}",  # 111111MMMM
        ]
        for regex in search_regex:
            searchobj5 = re.search(regex, st, flags=re.I)
            if searchobj5:
                num = re.search(r"^\d{3,}", searchobj5.group())
                char = re.findall(r"[a-z]+", searchobj5.group(), flags=re.I)[0]
                if num:
                    return num.group() + "-" + char
                return char + "-" + re.search(r"\d+", searchobj5.group()).group()
            continue

    # 最简单的还是通过 - _ 来分割判断
    if "-" in filename or "_" in filename:
        filename = regular_id(filename)
        if filename:
            return filename
    # n1111
    searchobj4 = re.search(r"n[1|0]\d{3}", filename, flags=re.I)
    if searchobj4:
        return searchobj4.group()

    filename = no_line_id(filename)
    if filename:
        return filename
        # logger.warning(f'fail to match id: \n{file.name}\n try input manualy')
        # return input()


class MyTestCase(unittest.TestCase):
    def test_number_parser(self):
        # AA-111
        # AAAA-111
        # 111111-111
        # FC1111111 FC-1111111 FC.1111111
        # AAA-111

        file_list = {
            "BF-622": "xxx_原版首发_BF-622",
            "SHKD-769": "[ThePorn][SHKD-769]高飛車女社長下克上輪姦希島あいり--更多视频访问[theporn.xyz]",
            "DV-928": " (アリス JAPAN) DV-928 麻美ゆまと 100 人のオナニスト",
            "SPRD-839": "【SPRD-839】少妻的春光诱惑 - [上原亚衣]",
            "100818_753": "[ThZu.Cc]100818_753-1pon-1080p",
            "mast-003": "mast-003-A",
            "fc2-1154295": "2048 社区 - fun2048.com@fc1154295",
            "MGT-081": "MGT-081A~nyap2p.com",
            "EYAN-052": "(E-BODY)(EYAN-052) ノーブラ Fcup 母乳妻の甘～い誘惑 小椋かをり",
            "PPPD-365": "PPPD-365.1080p",
            "259luxu-1111": "259luxu-1111",
            "FC2-1142063": "【FC2 PPV 1142063】カラオケで！見つからないかドキドキしながらもハメハメ !!!",
            "n0890": "tokyo_hot-n0890",
            "n0891": "Tokyo-Hot n0891 Shameless CA-Mary Jane Lee {18iso.com} [720p uncensored]",
            "kmhrs-026": "kmhrs-026-C",
            "STARS-272": "STARS272AC",
            "ipx-568": "ipx-568-C",
            "STARS-267": "STARS267",
            "GVG-509": "GVG-509",
            "MIDE-856": "MIDE-856.1080p",
            "STARS-250": "STARS250",
            "SDMF-013": "SDMF-013_CH_SD",
            "STARS-126": "STARS-126_HD_CH",
            "JFB-164": "[44x.me]JFB-164-2",
            "ipz-844": "[Thz.la]ipz-844",
            "GOJU-158": "GOJU-158_CH_SD",
            "bab-013": "HD_bab-013",
            "gvg-904": "HD-gvg-904",
            "SSNI-745": "ซับฝัง/SSNI-745",
            "EMAZ-209": "[鱼香肉丝]EMAZ-209",
            "PRED-276": "big2048.com@PRED-276",
            "ipz-947": "ipz-947-C",
            "STARS-058": "STARS-058_CH_SD",
            "SSNI-780": "SSNI-780@AD",
            "katu-059": "katu-059.1080p",
            "OFJE-267": "[69av][OFJE-267]圧倒的美少女が故に標的にされた橋本ありな快楽に堕ちるレ○プベスト8時間--更多视频访问[69av.one",
            "CJOD-269": "@蜂鳥@FENGNIAO131.VIP-CJOD-269_2K",
            "BANK-021": "HD_BANK-021",
            "OKP-057": "1080fhd.com_OKP-057",
            "111920-001": "[psk.la]111920-001-carib-1080p",
        }

        for k, v in file_list.items():
            self.assertEqual(k, number_parser(v))

    def _test_single(self):
        filename = "【FC2 PPV 1142063】カラオケで！見つからないかドキドキしながらもハメハメ !!!"
        self.assertEqual("FC2-1142063", number_parser(filename))


if __name__ == "__main__":
    unittest.main()
