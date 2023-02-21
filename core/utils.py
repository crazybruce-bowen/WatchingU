import time
from pyquery import PyQuery as pq
from core.constants import CityCode, DefaultInfo
from core.constants import LjFilter, ZiRoomFilter
from xpinyin import Pinyin


# =========================================
# 通用类

def print_time(f):
    """ 函数修饰器, 打印执行时间 """

    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> <%s> 任务的执行时间为 : %s 秒' % (f.__name__, round(float(time.time() - s), 2)))
        return res

    return fi


def mapper(list1: list, list2: list) -> dict:
    """ 制作list1到list2的map字典 """
    return dict(zip(list1, list2))


def get_url_base(url):
    """ 取主站url, 即https://xxx/ 为止 """
    return '/'.join(url.split('/')[:3])


def make_standard_html(html: str or pq):
    """ 生成标准doc """
    # 参数处理
    if isinstance(html, str):
        doc = pq(html)
    else:
        doc = html
    assert isinstance(doc, pq), 'city_html参数格式错误, 仅支持str类型的html文件或PyQuery类型'
    return doc


def chinese_to_pinyin(s: str):
    p = Pinyin()
    return p.get_pinyin(s)


# =========================================
# 业务类

def get_city_code(city: str) -> str or False:
    """ 将用户输入的城市信息字符串转化为项目城市code """
    assert isinstance(city, str), 'get_city_code方法输入的city信息必须是字符串'
    assert len(city) <= 20, 'get_city_code方法输入字符串最大长度为20'
    # 判断是否为中文
    tag_cn = False
    for s in city:
        if '\u4e00' <= s <= '\u9fa5':
            tag_cn = True
            break
    # 匹配
    if tag_cn is True:  # 中文匹配
        if city in CityCode.city_cn:
            citycode = mapper(CityCode.city_cn, CityCode.city_code).get(city)
        else:
            citycode = mapper(CityCode.city_cn2, CityCode.city_code).get(city, False)
    else:  # 英文匹配
        city = city.lower()
        if city in CityCode.city_en_abbr:
            citycode = mapper(CityCode.city_en_abbr, CityCode.city_code).get(city)
        else:
            citycode = mapper(CityCode.city_en, CityCode.city_code).get(city, False)

    return citycode


def get_city_info(citycode: str, attr: str) -> str:
    """
    根据citycode获取对应的信息

    参数:
        citycode: str 项目城市code, 已内置完成, 详见CityCode中的文档
        attr: 获取属性信息, 可用列表如下
          - city_cn  中文名  如 上海
          - city_cn2  中文名+市  如 上海市
          - city_en  拼音全名  如 shanghai
          - city_en_abbr  拼音缩写  如 sh
          - city_url_lianjia  该城市链家首页地址  如 sh.lianjia.com
          - city_url_ziroom  该城市自如首页地址  如 sh.ziroom.com

    """
    assert attr in dir(CityCode), f'{attr} 属性不在CityCode属性中, 请核实'
    attr_info = getattr(CityCode, attr)
    res = mapper(CityCode.city_code, attr_info).get(citycode, False)
    return res


def get_lj_rent_url(citycode=None) -> str:
    """
    根据city信息获取链家租房首页地址

    参数:
        citycode: 项目城市编码
    """
    if not citycode:
        citycode = DefaultInfo.city_code
    url_city = get_city_info(citycode, 'city_url_lianjia')

    return url_city


def get_lj_xiaoqu_url(citycode=None) -> str:
    """ 获取链家小区城市主站 """
    if not citycode:
        citycode = DefaultInfo.city_code
    url_city = get_url_base(get_lj_url(citycode)) + '/xiaoqu'

    return url_city


def get_lj_url(citycode=None) -> str:
    """ 获取链家城市主站 """
    return get_url_base(get_lj_rent_url(citycode))


# =========================================
# 待分类

def make_lianjia_filter(rent_type='整租', price_min=3000, price_max=6000,
                        room_num: list = [] or int, towards: list = [] or int) -> dict:
    """
    生成下探筛选条件, 生成字典

    参数：
        rent_type: 房源类型，可选【整租|合租】
        price_min: 租金最低值
        price_max: 租金最高值
        room_num: list 多选。如1居2居可传入[1, 2]。房间数可选1-3, 4以上自动合成
        toward: list 多选 房间朝向, 可选【东|南|西|北|南北】
    """
    # 参数校验
    if isinstance(room_num, int):
        room_num = [room_num]
    if isinstance(towards, str):
        towards = [towards]
    assert price_max > price_min, f'最高价格需高于最低价格, 当前设置最高价格{price_max}, 最低价格{price_min}'
    assert len(room_num) <= 4, f'room_num参数设置过多, 最多支持4个, 当前为{len(room_num)}个'
    assert len(towards) <= 5, f'toward参数设置过多, 最多支持5个, 当前为{len(towards)}个'
    res = {
        'rent_type': rent_type,
        'price_min': price_min,
        'price_max': price_max,
        'room_num': room_num,
        'toward': towards
    }

    return res


def lj_generate_filter_url(f: dict) -> str:
    """ 链家用, 根据filter条件生成url后缀。此方法为人工学习结果, 可能更改 """

    rent_type = f.get('rent_type')
    price_min = f.get('price_min')
    price_max = f.get('price_max')
    room_num = f.get('room_num')
    towards = f.get('towards')

    if room_num and isinstance(room_num, int):
        room_num = [room_num]
    if towards and isinstance(towards, str):
        towards = [towards]
    # 输出的字符变量
    res = ''
    # 最左端为租房类型
    if rent_type:
        res += LjFilter.rent_type_mapper.get(rent_type)
    # 之后为朝向
    if towards:
        for i in towards:
            res += LjFilter.toward_mapper.get(i)
    # 之后为房间数量
    if room_num:
        for i in room_num:
            res += LjFilter.room_num_mapper(i)
    # 右端为价格
    if price_min:
        res += LjFilter.price_mapper(price_min, 'left')
    if price_max:
        res += LjFilter.price_mapper(price_max, 'right')

    return res


# def zr_generate_filter_url(f: dict) -> str:
#     """ 自如用, 根据filter条件生成url后缀。此方法为人工学习结果, 可能更改 """
#     area_sub_url = f.get('area_sub_url')
#     area_lv2_sub_url = f.get('area_lv2_sub_url')
#     rent_type = f.get('rent_type')
#     price_min = f.get('price_min')
#     price_max = f.get('price_max')
#     room_num = f.get('room_num')
#     towards = f.get('towards')
#
#     if room_num and isinstance(room_num, int):
#         room_num = [room_num]
#     if towards and isinstance(towards, str):
#         towards = [towards]
#     # 输出的字符变量
#     res = ''
#     # 最左端为租房类型
#     if rent_type:
#         res += ZiRoomFilter.rent_type_mapper.get(rent_type)
#     # 之后为区域
#     if area_sub_url:
#         res = res + '-' + area_sub_url
#     # lv2区域
#     if area_lv2_sub_url:
#         res = res + '-' + area_lv2_sub_url
#
#     # 之后为房间数量
#     if room_num:
#         for i in room_num:
#             res += LjFilter.room_num_mapper(i)
#     # 右端为价格
#     if price_min:
#         res += LjFilter.price_mapper(price_min, 'left')
#     if price_max:
#         res += LjFilter.price_mapper(price_max, 'right')
#
#     return res

