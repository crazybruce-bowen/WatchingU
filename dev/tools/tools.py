# 2023.02.02
# 重构代码
# 此处放所有工具类代码，之后再划分

# ==============================================
# 常量

import pandas as pd
from dataclasses import dataclass


@dataclass
class CityCode:
    url_ziru = 'https://www.ziroom.com/'
    url_lianjia = 'https://www.lianjia.com/'
    path = 'data/标准城市信息对照表.xlsx'
    df = pd.read_excel(path, dtype=str)
    city_code = df['city_code'].dropna().tolist()
    city_cn = df['city_cn'].dropna().tolist()
    city_cn2 = df['city_cn2'].dropna().tolist()
    city_en = df['city_en'].dropna().tolist()
    city_en_abbr = df['city_en_abbr'].dropna().tolist()
    city_url_lianjia = df['city_url_lianjia'].dropna().tolist()
    city_url_ziru = df['city_url_ziru'].dropna().tolist()


@dataclass
class DefaultInfo:
    city = 'sh'
    city_code = '001'

# ==============================================
# 非业务功能

import time


def print_time(f):
    """ 函数修饰器, 打印执行时间 """
    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %s' % (f.__name__, round(float(time.time() - s), 2)))
        return res
    return fi


def mapper(list1: list, list2: list) -> dict:
    """ 制作list1到list2的map字典 """
    return dict(zip(list1, list2))


def get_url_base(url):
    """ 取主站url, 即https://xxx/ 为止 """
    return '/'.join(url.split('/')[:3])



# ==============================================
# 业务信息变换

def get_city_code(city: str) -> str or False:
    """ 将用户输入的城市信息字符串转化为项目城市code """
    assert isinstance(city, str), 'get_city_code方法输入的city信息必须是字符串'
    assert len(city)<=20, 'get_city_code方法输入字符串最大长度为20'
    # 判断是否为中文
    tag_cn = False
    for s in city:
        if '\u4e00' <= s <= '\u9fa5':
            tag_cn = True
            break
    # 匹配
    if tag_cn is True:    # 中文匹配
        if city in CityCode.city_cn:
            citycode = mapper(CityCode.city_cn, CityCode.city_code).get(city)
        else:
            citycode = mapper(CityCode.city_cn2, CityCode.city_code).get(city, False)
    else:    # 英文匹配
        city = city.lower()
        if city in CityCode.city_en_abbr:
            citycode = mapper(CityCode.city_en_abbr, CityCode.city_code).get(city)
        else:
            citycode = mapper(CityCode.city_en, CityCode.city_code).get(city, False)

    return citycode


def get_city_info(citycode: str, attr: str) -> str:
    """ 
    功能: 
        根据citycode获取对应的信息
    参数:
        citycode: str 项目城市code, 已内置完成, 详见CityCode中的文档
        attr: 获取属性信息, 可用列表如下
          - city_cn  中文名  如 上海
          - city_cn2  中文名+市  如 上海市
          - city_en  拼音全名  如 shanghai
          - city_en_abbr  拼音缩写  如 sh
          - city_url_lianjia  该城市链家首页地址  如 sh.lianjia.com
          - city_url_ziru  该城市自如首页地址  如 sh.ziroom.com
    
    """
    assert attr in dir(CityCode), f'{attr} 属性不在CityCode属性中, 请核实'
    attr_info = getattr(CityCode, attr)
    res = mapper(CityCode.city_code, attr_info).get(citycode, False)
    return res


def get_lj_url(citycode=None) -> str:
    """
    功能:
        根据city信息获取链家首页地址
    参数:
        citycode: 项目城市编码
    """
    if not citycode:
        citycode = DefaultInfo.city_code
    url_city = get_city_info(citycode, 'city_url_lianjia')

    return url_city

# ==============================================
# url爬取html  *要求网络

from requests.exceptions import RequestException
import requests
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


# 解析url直接到pq格式
def get_doc_from_url(url: str) -> pq:
    """ 解析url直接到pq格式 """
    doc = pq(get_one_page_html(url))
    return doc

# ==============================================
# html解析 *注意，此模块仅可输入html和pq类型参数，禁止使用网络

def lj_city2area_html_dict(city_html: str or pq, citycode: str=None) -> dict:
    """
    功能:
        链家html解析。解析city_doc, 提取可用的区级信息, 输出dict
    参数: 
        city_html: 城市主页的html字符或pq(PyQuery)类型均可
        citycode: 项目城市编码
    """
    # 参数处理
    if isinstance(city_html, str):
        doc = pq(city_html)
    else:
        doc = city_html
    assert isinstance(doc, pq), 'city_html参数格式错误, 仅支持str类型的html文件或PyQuery类型'

    # 城市主站
    url_city = get_lj_url(citycode)

    # 解析区域信息
    res = []
    for i in doc('ul[data-target=area]')('a').items():
        tmp = i.text()
        if tmp != '不限':
            res.append({'area': i.text(),  # 区域中文名
                        'url': get_url_base(url_city) + i.attr('href')})    # 区域url  
    
    return res


def lj_city2area_html_list(city_html: str or pq, citycode: str=None) -> list:
    """
    功能:
        链家html解析。解析city_doc, 提取可用的区级信息, 输出可用的中文名list
    参数: 
        city_html: 城市主页的html字符或pq(PyQuery)类型均可
        citycode: 项目城市编码
    """
    d = lj_city2area_html_dict(city_html, citycode)
    res = []
    for i in d:
        area = i.get('area')
        if area:
            res.qppend(area)
    if not res:
        city_cn = get_city_info(citycode, 'city_cn')
        print(f'== Warning 该城市 {city_cn} 无可用区域 ==')
    return res


def lj_area_level2_html_dict(area_html: str or pq, area: str) -> dict:
    """
    功能：
        链家二级区域信息获取, 提取二级区域名和对应的url, 输出dict
    参数: 
        area_html: html字符或pq(PyQuery)类型均可
        area: 一级区域中文名* 注: 此处中文名无法验证

    """
    


# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================

# ==============================================