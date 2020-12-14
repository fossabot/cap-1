from pathlib import Path

from core.number import number_parser

file_list = {
    "BF-622": "xxx_原版首发_BF-622.mp4",
    "SHKD-769": "[ThePorn][SHKD-769]高飛車女社長下克上輪姦希島あいり--更多视频访问[theporn.xyz].mp4",
    "DV-928": " (アリス JAPAN) DV-928 麻美ゆまと 100 人のオナニスト.mp4",
    "SPRD-839": "【SPRD-839】少妻的春光诱惑 - [上原亚衣].mp4",
    "100818_753": "[ThZu.Cc]100818_753-1pon-1080p.mp4",
    "mast-003": "mast-003-A.mp4",
    "fc2-1154295": "2048 社区 - fun2048.com@fc1154295.mp4",
    "MGT-081": "MGT-081A~nyap2p.com.mp4",
    "EYAN-052": "(E-BODY)(EYAN-052) ノーブラ Fcup 母乳妻の甘～い誘惑 小椋かをり.mp4",
    "PPPD-365": "PPPD-365.1080p.mp4",
    "259luxu-1111": "259luxu-1111",
    "FC2-1142063": "【FC2 PPV 1142063】カラオケで！見つからないかドキドキしながらもハメハメ !!!.mp4",
    "n0890": "tokyo_hot-n0890.mp4",
    "n0891": "Tokyo-Hot n0891 Shameless CA-Mary Jane Lee {18iso.com} [720p uncensored].mp4",
    "kmhrs-026": "kmhrs-026-C.mp4",
    "STARS-272": "STARS272AC.mp4",
    "ipx-568": "ipx-568-C.mp4",
    "STARS-267": "STARS267.mp4",
    "GVG-509": "GVG-509.mp4",
    "MIDE-856": "MIDE-856.1080p.mp4",
    "STARS-250": "STARS250.mp4",
    "SDMF-013": "SDMF-013_CH_SD.mp4",
    "STARS-126": "STARS-126_HD_CH.mp4",
    "JFB-164": "[44x.me]JFB-164-2.mp4",
    "ipz-844": "[Thz.la]ipz-844.mp4",
    "GOJU-158": "GOJU-158_CH_SD.mp4",
    "bab-013": "HD_bab-013.mp4",
    "gvg-904": "HD-gvg-904.mp4",
    "SSNI-745": "ซับฝัง/SSNI-745.mp4",
    "EMAZ-209": "[鱼香肉丝]EMAZ-209.mp4",
    "PRED-276": "big2048.com@PRED-276.mp4",
    "ipz-947": "ipz-947-C.mp4",
    "STARS-058": "STARS-058_CH_SD.mp4",
    "SSNI-780": "SSNI-780@AD.mp4",
    "katu-059": "katu-059.1080p.mp4",
    "OFJE-267": "[69av][OFJE-267]圧倒的美少女が故に標的にされた橋本ありな快楽に堕ちるレ○プベスト8時間--更多视频访问[69av.one.mp4",
    "CJOD-269": "@蜂鳥@FENGNIAO131.VIP-CJOD-269_2K.mp4",
    "BANK-021": "HD_BANK-021.mp4",
    "OKP-057": "1080fhd.com_OKP-057.mp4",
    "111920-001": "[psk.la]111920-001-carib-1080p.mp4",
}


def test_number_parser():
    for k, v in file_list.items():
        v = Path(v)
        assert number_parser(v) == k
