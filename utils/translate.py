import asyncio
import time

from google_trans_new import google_translator


async def request(text):
    lang = "zh"
    t = google_translator(url_suffix="hk", timeout=8)
    translate_text = t.translate(text.strip(), lang)
    print(translate_text)


async def main():
    with open("test.txt", 'r') as f_p:
        texts = f_p.readlines()
        tasks = [asyncio.create_task(request(text)) for text in texts]
        for task in tasks:
            await task


if __name__ == "__main__":
    time1 = time.time()
    asyncio.run(main())
    time2 = time.time()
    print("Translating sentences, a total of %s s" % (time2 - time1))
