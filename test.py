"""
TODO list:
1. 输入城市, 查询可选区域参数  |  Done
2. 输入城市和可选区域, 查询二级可选区域参数  |  Done
3. 输入城市, 区域, 二级区域, 其他备选信息, 计算链家原始信息  |  Done
4. 解析原始信息  |  Done
4.1 自如价格解析
5. 存储信息至数据库
6. 自动执行, 多线程执行

"""

from prd.ops import LianJiaHtmlOps, ZiRoomHtmlOps, AnalysisOps, XiaoquHtmlOps
from prd.utils import get_city_code, get_city_info, get_lj_rent_url, lj_generate_filter_url, get_lj_xiaoqu_url
from prd.service import get_one_page_html, get_doc_from_url
from prd.constants import ZiRoomFilter
from typing import List
import pandas as pd
from pyquery import PyQuery as pq
from prd.utils import print_time
from PIL import Image
import requests
from io import BytesIO



# ==============================
# 链家部分

def get_lianjia_area_list(city: str) -> list:
    """
    输入城市，返回可选区域

    :param city: 城市 可输入中文、拼音、缩写或城市编号。如 上海|上海市|sh|shanghai|'001'
    :return: 可选区域list
    """
    city_code = get_city_code(city)
    url = get_lj_rent_url(city_code)
    html_url = get_one_page_html(url)
    lj_ops = LianJiaHtmlOps(city_code)
    res = lj_ops.city2area_list(html_url)
    return res


def get_lianjia_area_level2_list(city: str, area: str) -> list:
    """
    输入城市和一级区域，返回二级区域

    :param city: 城市 可输入中文、拼音、缩写或城市编号。如 上海|上海市|sh|shanghai|'001'
    :param area: 一级区域，可通过get_lianjia_area_list查询
    :return:
    """
    # 标准编码
    city_code = get_city_code(city)

    # 城市url和html
    url = get_lj_rent_url(city_code)
    html_url = get_one_page_html(url)

    # lj ops初始化
    lj_ops = LianJiaHtmlOps(city_code)

    # 特定区域的url和html
    url_area = lj_ops.get_area_url(html_url, area)
    area_html = get_one_page_html(url_area)

    # 返回二级区域列表
    res = lj_ops.area_level2_list(area_html)
    return res


def get_lianjia_info(city, area=None, area_lv2=None, **kwargs) -> List[dict]:
    """
    获取链家房源信息

    :param city:
    :param area:
    :param area_lv2:
    :param kwargs:
        可选列表如下：
        rent_type: 房源类型，可选【整租|合租】
        price_min: 租金最低值
        price_max: 租金最高值
        room_num: list or int 多选。如1居2居可传入[1, 2]。房间数可选1-3, 4以上自动合成
        toward: list or int 多选 房间朝向, 可选【东|南|西|北|南北】
    :return: list of dict
        内容包括：链家id, 标题, 小区, 描述, 价格, 房源url, 图片url

    """
    # 城市编码
    city_code = get_city_code(city)
    city_str = get_city_info(city_code, 'city_cn')

    # 城市url和html
    url_city = get_lj_rent_url(city_code)
    html_city = get_one_page_html(url_city)

    lj_ops = LianJiaHtmlOps(city_code)
    # 有区域
    if area:
        url_area = lj_ops.get_area_url(html_city, area)
        html_area = get_one_page_html(url_area)
        city_str = city_str + '-' + area
        # 2级区域
        if area_lv2:
            url_f = lj_ops.get_area_lv2(html_area, area_lv2)
            city_str = city_str + '-' + area_lv2
        else:
            url_f = url_area
    # 无区域
    else:
        url_f = url_city

    # 制作filter
    url_f += lj_generate_filter_url(kwargs)

    # 分页信息
    html_f = get_one_page_html(url_f)
    url_pages = lj_ops.pagination(html_f)

    # 全量url
    url_total = [url_f] + url_pages

    print(f'== 本次共提取链家{city_str} {len(url_total)}页房源 == ')

    # 全量html捕获
    pq_total = []
    n = 0
    for url in url_total:
        n += 1
        print(f'= 下载第{n}页 =')
        try:
            tmp_pq = get_doc_from_url(url)
            pq_total.append(tmp_pq)
        except Exception as e:
            print(f'= 第{n}页url获取失败，异常情况如下 =')
            print(e)
            pass

    print(f'== 本次提取链家{city_str} 房源完成 == ')

    print(f'== 开始解析html == ')
    # 解析html
    room_info_total = []
    n = 0
    for i in pq_total:
        n += 1
        print(f'= 解析第{n}页 =')
        tmp_room_info = lj_ops.get_room_info_page(i)
        room_info_total += tmp_room_info
    print(f'== html解析完成，共解析房源{len(room_info_total)}个 == ')

    return room_info_total


def get_lianjia_html(city, area=None, area_lv2=None, **kwargs) -> List[str]:
    """
    获取链家房源信息，进行request请求，返回html的list

    :param city:
    :param area:
    :param area_lv2:
    :param kwargs:
        可选列表如下：
        rent_type: 房源类型，可选【整租|合租】
        price_min: 租金最低值
        price_max: 租金最高值
        room_num: list or int 多选。如1居2居可传入[1, 2]。房间数可选1-3, 4以上自动合成
        toward: list or int 多选 房间朝向, 可选【东|南|西|北|南北】
    :return: list of dict
        内容包括：链家id, 标题, 小区, 描述, 价格, 房源url, 图片url

    """
    # 城市编码
    city_code = get_city_code(city)
    city_str = get_city_info(city_code, 'city_cn')

    # 城市url和html
    url_city = get_lj_rent_url(city_code)
    html_city = get_one_page_html(url_city)

    lj_ops = LianJiaHtmlOps(city_code)
    # 有区域
    if area:
        url_area = lj_ops.get_area_url(html_city, area)
        html_area = get_one_page_html(url_area)
        city_str = city_str + '-' + area
        # 2级区域
        if area_lv2:
            url_f = lj_ops.get_area_lv2(html_area, area_lv2)
            city_str = city_str + '-' + area_lv2
        else:
            url_f = url_area
    # 无区域
    else:
        url_f = url_city

    # 制作filter
    url_f += lj_generate_filter_url(kwargs)

    # 分页信息
    url_pages = lj_ops.pagination(url_f)
    # 全量url
    url_total = [url_f] + url_pages

    print(f'== 本次共提取链家{city_str} {len(url_total)}页房源 == ')

    # 全量html捕获
    html_total = []
    n = 0
    for url in url_total:
        n += 1
        print(f'= 下载第{n}页 =')
        try:
            tmp_html = get_one_page_html(url)
            html_total.append(tmp_html)
        except Exception as e:
            print(f'= 第{n}页url获取失败，异常情况如下 =')
            print(e)
            pass

    print(f'== 本次提取链家{city_str} 房源完成 == ')
    return html_total


def analyse_lianjia_html(html_list: List[str], city=None):
    """
    下载到html文件后，可用此方法进行解析

    :param html_list:
    :param city: 城市
    :return:
    """
    # pq化
    pq_total = []
    for i in html_list:
        doc = pq(i)
        pq_total.append(doc)

    print(f'== 开始解析html == ')
    city_code = get_city_code(city)
    lj_ops = LianJiaHtmlOps(city_code)
    # 解析html
    room_info_total = []
    n = 0
    for i in pq_total:
        n += 1
        print(f'= 解析第{n}页 =')
        tmp_room_info = lj_ops.get_room_info_page(i)
        room_info_total += tmp_room_info
    print(f'== html解析完成，共解析房源{len(room_info_total)}个 == ')


@print_time
def get_lj_info_standard(city, area=None, area_lv2=None, **kwargs) -> List[dict]:
    room_info = get_lianjia_info(city, area, area_lv2, **kwargs)
    print('== 开始整理信息 ==')
    res = []
    for i in room_info:
        res.append(AnalysisOps.analyse_lianjia_info_item(i))
    return res


# ===========================================
# 自如部分
"""
TODO list:
1. 输入城市, 查询可选区域参数  
2. 输入城市和可选区域, 查询二级可选区域参数  
3. 输入城市, 区域, 二级区域, 其他备选信息, 计算链家原始信息  

"""


def get_ziroom_area_list(city: str) -> list:
    """
    输入城市，返回可选区域

    :param city: 城市 可输入中文、拼音、缩写或城市编号。如 上海|上海市|sh|shanghai|'001'
    :return: 可选区域list
    """
    city_code = get_city_code(city)
    url = get_city_info(city_code, 'city_url_ziroom')
    html_url = get_one_page_html(url)
    zr_ops = ZiRoomHtmlOps(city_code)
    res = zr_ops.city2area_list(html_url)
    return res


def get_ziroom_area_level2_list(city: str, area: str) -> list:
    """
    输入城市和一级区域，返回二级区域

    :param city: 城市 可输入中文、拼音、缩写或城市编号。如 上海|上海市|sh|shanghai|'001'
    :param area: 一级区域，可通过get_ziroom_area_list查询
    :return:
    """
    # 标准编码
    city_code = get_city_code(city)

    # 城市url和html
    url = get_city_info(city_code, 'city_url_ziroom')
    html_url = get_one_page_html(url)

    # lj ops初始化
    zr_ops = ZiRoomHtmlOps(city_code)

    # 特定区域的url和html
    url_area = zr_ops.get_area_url(html_url, area)
    area_html = get_one_page_html(url_area)

    # 返回二级区域列表
    res = zr_ops.area_level2_list(area_html)
    return res


def get_ziroom_info(city, area=None, area_lv2=None, rent_type=None, price_min: float = None, price_max: float = None,
                    room_num: int or list = None, towards=None):
    """
    获取自如房源信息

    :param city: 城市
    :param area: 区域
    :param area_lv2: 二级区域
    :param rent_type: 房源类型，可选【整租|合租】
    :param price_min: 租金最低值
    :param price_max: 租金最高值
    :param room_num: list or int 多选。如1居2居可传入[1, 2]。房间数可选1-3, 4以上自动合成
    :param towards: list or int 多选 房间朝向, 可选【东|南|西|北|南北】
    :return:
    """
    if price_max and price_min:
        assert price_max > price_min, f'最高价格须高于最低价格, 当前最高价格 {price_max}, 最低价格 {price_min}'

    # 城市编码
    city_code = get_city_code(city)
    city_str = get_city_info(city_code, 'city_cn')

    # 城市url和html
    url_city = get_city_info(city_code, 'city_url_ziroom')
    html_city = get_one_page_html(url_city)

    zr_ops = ZiRoomHtmlOps(city_code)

    # 直接拼接
    url_f = url_city
    # 先拼租房类型
    if rent_type:
        url_f += ZiRoomFilter.rent_type_mapper.get(rent_type)
    # 再拼区域
    if area:
        url_area = zr_ops.get_area_url(html_city, area)
        html_area = get_one_page_html(url_area)
        city_str = city_str + '-' + area
        # 2级区域
        if area_lv2:
            url_area = zr_ops.get_area_lv2(html_area, area_lv2)
            city_str = city_str + '-' + area_lv2
        url_f = url_f + '-' + url_area.split('/')[-2]

    # 再拼户型
    if room_num:
        url_f = url_f + '-' + ZiRoomFilter.make_room_num_str(room_num)

    # 下级参数
    url_f = url_f + '/?'

    # 再拼朝向
    if towards:
        url_f = url_f + ZiRoomFilter.make_towards_str(towards)
    # 再拼价格
    if price_min or price_max:
        if price_max:
            if not price_min:
                price_min = 0
        else:
            price_max = 99999
        url_f = url_f + f'&cp={price_min}TO{price_max}'

    # 分页信息
    html_f = get_one_page_html(url_f)
    url_pages = zr_ops.pagination(html_f)
    # 全量url
    url_total = [url_f] + url_pages

    print(f'== 本次共提取自如{city_str} {len(url_total)}页房源, url地址为 {url_f} == ')

    # 全量html捕获
    pq_total = []
    n = 0
    for url in url_total:
        n += 1
        print(f'= 下载第{n}页 =')
        try:
            tmp_pq = get_doc_from_url(url)
            pq_total.append(tmp_pq)
        except Exception as e:
            print(f'= 第{n}页url获取失败，异常情况如下 =')
            print(e)
            pass

    print(f'== 本次提取自如{city_str} 房源完成 == ')

    print('== 开始解析html == ')
    # 解析html
    room_info_total = []
    n = 0
    for pq in pq_total:
        n += 1
        print(f'= 解析第{n}页 =')
        tmp_room_info = zr_ops.get_room_info_page(pq)
        room_info_total += tmp_room_info
    print(f'== html解析完成，共解析房源{len(room_info_total)}个 == ')

    return room_info_total


@print_time
def get_ziroom_info_standard(city, area=None, area_lv2=None, **kwargs) -> List[dict]:
    room_info = get_ziroom_info(city, area, area_lv2, **kwargs)
    print('== 开始整理信息 ==')
    res = []
    for i in room_info:
        res.append(AnalysisOps.analyse_ziroom_info_item(i))
    print('== 整理信息完成 ==')
    return res


def get_room_info_standard(city, area=None, area_lv2=None, **kwargs) -> List[dict]:
    """
    获取整理后的信息，链家和自如一起操作

    :param city:
    :param area:
    :param area_lv2:
    :param kwargs:
    :return:
    """
    # 操作链家
    print('=== 开始执行链家任务 ===')
    room_info_lj = get_lj_info_standard(city, area, area_lv2, **kwargs)
    print('=== 链家任务执行完成 ===')
    # 操作自如
    print('=== 开始执行自如任务 ===')
    room_info_zr = get_ziroom_info_standard(city, area, area_lv2, **kwargs)
    print('=== 自如任务执行完成 ===')
    res = room_info_lj + room_info_zr
    return res


# ==========================================================
# 小区情况
@print_time
def get_xiaoqu_info(city, area=None, area_lv2=None):
    """
    获取小区信息。此处需要下探到小区页面, 耗时较长

    :param city:
    :param area:
    :param area_lv2:
    :return:
    """
    city_code = get_city_code(city)
    city_str = get_city_info(city_code, 'city_cn')
    # 城市url和html
    url_city = get_lj_xiaoqu_url(city_code)
    html_city = get_one_page_html(url_city)

    xiaoqu_ops = XiaoquHtmlOps(city_code)
    # 有区域
    if area:
        url_area = xiaoqu_ops.get_area_url(html_city, area)
        html_area = get_one_page_html(url_area)
        city_str = city_str + '-' + area
        # 2级区域
        if area_lv2:
            url_f = xiaoqu_ops.get_area_lv2(html_area, area_lv2)
            city_str = city_str + '-' + area_lv2
        else:
            url_f = url_area
    # 无区域
    else:
        url_f = url_city

    # 分页信息
    html_f = get_one_page_html(url_f)
    url_pages = xiaoqu_ops.pagination(html_f, url_f)
    # 全量url
    url_total = [url_f] + url_pages

    print(f'== 本次共提取链家{city_str} {len(url_total)}页小区情况 == ')

    # 全量html捕获
    pq_total = []
    n = 0
    for url in url_total:
        n += 1
        print(f'= 下载第{n}页 =')
        try:
            tmp_pq = get_doc_from_url(url)
            pq_total.append(tmp_pq)
        except Exception as e:
            print(f'= 第{n}页url获取失败，异常情况如下 =')
            print(e)
            pass

    print(f'== 本次提取链家{city_str} 小区情况完成 == ')

    print('== 开始解析分页html == ')
    # 解析html
    xiaoqu_info_total = []
    n = 0
    for i in pq_total:
        n += 1
        print(f'= 解析第{n}页 =')
        tmp_room_info = xiaoqu_ops.get_xiaoqu_info_page(i)
        xiaoqu_info_total += tmp_room_info
    print(f'== 分页html解析完成，共解析小区{len(xiaoqu_info_total)}个 == ')

    print('== 开始进入小区页面获取详细信息 ==')

    # 频繁下载不一定是好事，下方统一操作
    res = []
    n = 0
    for i in xiaoqu_info_total:
        n += 1
        if n % 10 == 0:
            print(f'= 已完成 {n} 个小区，共 {len(xiaoqu_info_total)} 个')
        url = i.get('小区url')
        try:
            html = get_one_page_html(url)
        except Exception as e:
            print(f'= 第{n}个小区信息获取失败, url为{url}, 报错信息如下 =')
            print(e)
            continue
        xiaoqu_info = xiaoqu_ops.get_xiaoqu_info_single(html)
        res.append(xiaoqu_info)
    return res


def get_xiaoqu_info_standard(city, area=None, area_lv2=None):
    xiaoqu_info = get_xiaoqu_info(city, area, area_lv2)
    print('== 开始整理信息 ==')
    res = []
    for i in xiaoqu_info:
        res.append(AnalysisOps.analyse_xiaoqu_info_item(i))
    print('== 整理信息完成 ==')
    return res


# 开发自如价格生成功能
import re

"""
TODO list
从小到大
Tools:
1. 输入图像url, 返回图像类  *禁止每张图都调用接口，太慢
2. 输入图像(图像类), 像素位置, 返回解析数字

Usage:
1. 输入单个数字的字符, 解析字符, 得到图像url和像素位置  |  Done
2. 房源内多个数字拆解成单个数字  |  Done
3. 解析单个数字信息

"""


def convert_one_number(s: str) -> tuple or False:
    """
    输入单个数字待解析字符, 返回url和像素位置
    
    case:
        'background-image: url(//static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png);background-position: -21.4px'
    :return:
        url 图片url https://static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png
        pos 像素位置
    """
    url_re = re.findall('url\((.*)\)', s)
    if not url_re:
        return False
    url = 'https:' + url_re[0]
    pos_re = re.findall('background-position: *(.*px)', s)
    if not pos_re:
        return False
    pos = pos_re[0]
    return url, pos


def convert_numbers(s: str):
    """
    将多个数字的拼接字符转换为多个数字的url和像素位置

    :param s:
    :return:
    """
    s_list = s.split('||')
    if not s_list:
        return False
    res = []
    for i in s_list:
        url, pos = convert_one_number(i)
        res.append({'url': url, 'pos': pos})

    return res


def get_pic_size(d:dict):
    url = d['url']    
    print(url)
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    return im.size
    

def get_pic_size_all(l: list):
    res = []
    for i in l:
        res.append(get_pic_size(i))
    return res

def get_pix(d: dict):
    pix = d['pos']
    return pix

def get_pix_all(l: list):
    res = []
    for i in l:
        res.append(get_pix(i))
    return res

def get_pic_url(l: list):
    res = l[0]['url']
    return res
#%%
t = get_ziroom_info_standard('hz', '西湖', rent_type='整租')
df = pd.DataFrame(t)

#%%
df['bw1'] = df['价格信息'].apply(convert_numbers)

#%% 加原始图片size
df['bw_size'] = df['bw1'].apply(get_pic_size_all)
#%% 加pix
df['bw_pix'] = df['bw1'].apply(get_pix_all)

df0 = df[['房源url', 'bw_size', 'bw_pix']]

df0.to_excel(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\查验.xlsx', index=None)
#%%

df['bw1'].apply(get_pic_url).to_excel(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\查验2.xlsx', index=None)
