from requests.exceptions import RequestException
import requests
from pyquery import PyQuery as pq

# ==============================================
# url爬取html  *要求网络


# 根据url获取html文件
def get_one_page_html(url) -> str or None:
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


# 解析url直接到pq格式
def get_doc_from_url(url: str) -> pq:
    """ 解析url直接到pq格式 """
    doc = pq(get_one_page_html(url))
    return doc



