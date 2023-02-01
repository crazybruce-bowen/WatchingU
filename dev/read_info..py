# Bowen
# 2023.02.01
# 此处开发从html解析信息的相关内容
from dev.get_info import get_lj_url, get_one_page_html, get_doc_from_url


# 根据城市获得可选区域
def lj_get_city_area_list(city: str) -> list:
    """
    params:
        city: 英文/英文缩写/中文 均可 如shanghai/sh/上海/上海市
    """
    url_city = get_lj_url(city)
    doc = get_doc_from_url(url_city)

    
