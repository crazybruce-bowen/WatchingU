# Bowen
# 2023.02.01
# 此处开发从网页获取html的相关内容

import requests
from requests.exceptions import RequestException
from utils.common_utils import get_city_code, get_city_info
from utils.constants import DefaultInfo
from pyquery import PyQuery as pq


# 根据url获取html文件
def get_one_page_html(url) -> str:
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


# 解析url到pq格式
def get_doc_from_url(url) -> pq:
    doc = pq(get_one_page_html(url))
    return doc


# 获取链家特定城市-区域等的主搜索页url
def get_lj_url(city=None):
    """
    params:
        city: 英文/英文缩写/中文 均可 如shanghai/sh/上海/上海市
    """
    if not city:
        city = DefaultInfo.city
    citycode = get_city_code(city)
    url_city = get_city_info(citycode, 'city_url_lianjia')

    res = url_city
    return res


    



