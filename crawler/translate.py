import json
import random
from urllib.parse import quote

from crawler.requestHandler import RequestHandler
from utils.logger import setup_logger

logger = setup_logger()


class GoogleTranslate(RequestHandler):
    # https://github.com/lushan88a/google_trans_new
    # 直接简化自此项目
    def __init__(self, cfg):
        super().__init__(cfg)
        self.url = (
            "https://translate.google.com/_/TranslateWebserverUi/data/batchexecute"
        )

    @staticmethod
    def package_rpc(text, target):
        parameter = [[text.strip(), "auto", target, True], [1]]
        escaped_parameter = json.dumps(parameter, separators=(",", ":"))
        rpc = [
            [[random.choice(["MkEWBc"]), escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(",", ":"))
        return f"f.req={quote(espaced_rpc)}&"

    @staticmethod
    def extract(decoded):
        try:
            response = json.loads((decoded + "]"))
            response = json.loads(list(response)[0][2])
            response = list(response)[1][0]
            if len(response) == 1:
                if len(response[0]) > 5:
                    sentences = response[0][5]
                else:
                    sentences = response[0][0]
                return "".join("".join(d[0].strip()) for d in sentences)
            return "".join(s[0] for s in response)

        except Exception as exc:
            logger.warning(f"warn: {exc}")

    def translate(self, text, target="zh-cn"):
        if len(text) == 0:
            return
        freq = self.package_rpc(text, target)
        headers = {
            "Referer": "http://translate.google.com/",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = self.post(self.url, freq, headers=headers)
        for line in response.iter_lines(chunk_size=1024):
            decoded = line.decode("utf-8")
            if "MkEWBc" in decoded:
                return self.extract(decoded)
