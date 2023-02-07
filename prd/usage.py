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

from prd.ops import LianJiaHtmlOps
from prd.utils import get_city_code, get_city_info, get_lj_rent_url, lj_generate_filter_url
from prd.service import get_one_page_html, get_doc_from_url


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


def get_lianjia_info(city, area=None, area_lv2=None, **kwargs):
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
    :return:
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
        print(f'= 操作第{n}页 =')
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
    for pq in pq_total:
        tmp_room_info = lj_ops.get_room_info_page(pq)
        room_info_total += tmp_room_info
    print(f'== html解析完成，共解析房源{len(room_info_total)}个 == ')

    return room_info_total


def analyse_lianjia_info_item(room_info: dict) -> dict:
    """
    解析链家信息的单条记录

    :param room_info: 链家信息的单条记录
    :return:
    """
    pass


# ===========================================
# 自如部分
"""
TODO list:
1. 输入城市, 查询可选区域参数  
2. 输入城市和可选区域, 查询二级可选区域参数  
3. 输入城市, 区域, 二级区域, 其他备选信息, 计算链家原始信息  

"""


if __name__ == '__main__':
    t = get_lianjia_info('hz', '西湖', '文三西路', price_min=3000, price_max=6000, rent_type='整租')
    print(len(t))
    print(t[:5])


