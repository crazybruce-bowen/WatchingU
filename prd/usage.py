# ==============================
# 链家部分

"""
TODO list:
1. 输入城市, 查询可选区域参数  |  Done
2. 输入城市和可选区域, 查询二级可选区域参数  |  Done
3. 输入城市, 区域, 二级区域, 其他备选信息, 计算链家原始信息  |  Done
4. 解析原始信息
5. 存储信息至数据库
6. 自动执行, 多线程执行

"""

from prd.ops import LianJiaHtmlOps, ZiRoomHtmlOps
from prd.utils import get_city_code, get_city_info, get_lj_rent_url, lj_generate_filter_url
from prd.service import get_one_page_html, get_doc_from_url
from prd.constants import ZiRoomFilter
from typing import List


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
        内容包括：链家id, 标题, 小区, 描述, 价格, 房源url, 图片地址url

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
    for pq in pq_total:
        n += 1
        print(f'= 解析第{n}页 =')
        tmp_room_info = lj_ops.get_room_info_page(pq)
        room_info_total += tmp_room_info
    print(f'== html解析完成，共解析房源{len(room_info_total)}个 == ')

    return room_info_total


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


# ==========================================================
# 二次解析


if __name__ == '__main__':
    t = get_ziroom_info('hz', '西湖', '文三西路', price_min=3000, price_max=6000, rent_type='整租')
    print(len(t))
    print(t[:5])


