import re
from time import sleep

from lxml import etree

from core.cli import get_cfg_defaults
from crawler.requestHandler import RequestHandler

config = get_cfg_defaults()
request = RequestHandler(config)

# f.close()
number_list = []
file_list = []
#
for line in open("btsow.txt"):
    link1 = line.split('|', 1)[-1].strip()
    print(link1)
    try:
        response1 = request.get(link1).text
        html = etree.fromstring(response1, etree.HTMLParser())
        print('获取第一层link')
        link2 = html.xpath('//div[@class="data-list"]//div[2]/a/@href')[0]
        searchsub = re.search(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', link2)
        assert searchsub, '不是网页'
        sleep(5)
        try:
            response2 = request.get(link2).text
            html2 = etree.fromstring(response2, etree.HTMLParser())
            print("获取第二层文件名称")
            filenames = html2.xpath('/html/body/div[2]/div[8]//div/div[1]/text()')
            size = html2.xpath('/html/body/div[2]/div[8]//div/div[2]/text()')
            file_zise = dict(zip(filenames, size))
            for file, size in file_zise.items():
                if re.search('.mp4', file, flags=re.I) and re.search('GB', size):
                    print(f'file: {file.strip()}')
                    file_list.append(file.strip())
                    number_list.append(line.split('.', 1)[0].strip())
            sleep(5)
        except Exception as exc:
            print(f'error :{exc}')
            continue
    except Exception as exc:
        print(f'error :{exc}')
        continue

assert len(number_list) == len(file_list)
num_file = dict(zip(number_list, file_list))
with open('next.txt', "w", encoding='utf-8') as fi:
    for num, file in num_file.items():
        fi.write('\'' + num + '\': ' + '\'' + file + '\',\n')
