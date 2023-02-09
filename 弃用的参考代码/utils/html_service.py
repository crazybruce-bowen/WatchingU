# 本方法为html相关内容

import requests
import pandas as pd
from requests.exceptions import RequestException
from pyquery import PyQuery as pq


def get_one_page_html(url):
    """ 获取网站每一页的html return html文件 """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None


# def find_page_url(html) -> [str]:
#     """ 根据html获取分页url """
#     doc = pq(html)
#     pages_info = doc('div.content__article > ul > li > a').items()
#     res = []
#     for i in pages_info:
#         res.append(i.attr('href'))
#     return res

