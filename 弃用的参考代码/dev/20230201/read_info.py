# Bowen
# 2023.02.01
# 此处开发从html解析信息的相关内容
from dev.get_info import get_doc_from_url, get_lj_url
from utils.common_utils import get_url_base


# 根据城市获得可选区域
def lj_get_city_area_list(city: str=None) -> list:
    """
    usage:
        根据城市获取可选区域
    params:
        city: 英文/英文缩写/中文 均可 如shanghai/sh/上海/上海市
    """
    url_city = get_lj_url(city)
    doc = get_doc_from_url(url_city)
    res = []
    for i in doc('ul[data-target=area]')('a').items():
        tmp = i.text()
        if tmp != '不限':
            res.append(tmp)
    return res


def lj_get_city_area_dict(city: str=None) -> dict:
    """ 根据城市获取可选区域及其url """
    url_city = get_lj_url(city)
    doc = get_doc_from_url(url_city)
    res = []
    for i in doc('ul[data-target=area]')('a').items():
        tmp = i.text()
        if tmp != '不限':
            res.append({'area': i.text(),
                        'url': get_url_base(url_city) + i.attr('href')})

    return res


def lj_get_area_list_level2(area) -> dict:


