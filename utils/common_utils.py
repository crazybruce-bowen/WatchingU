import time
from utils.constants import CityCode


def print_time(f):
    """ 函数修饰器，打印执行时间 """
    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %s' % (f.__name__, round(float(time.time() - s), 2)))
        return res
    return fi


def mapper(list1, list2):
    return dict(zip(list1, list2))


def get_city_code(city: str) -> str or False:
    """ 将用户输入的城市信息字符串转化为自己的城市code """
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
    """ 根据citycode获取对应的信息，info可选项为CityCode的属性名称，如city_en等 """
    assert attr in dir(CityCode), f'{attr} 属性不在CityCode属性中，请核实'
    attr_info = getattr(CityCode, attr)
    res = mapper(CityCode.city_code, attr_info).get(citycode, False)
    return res


def get_url_base(url):
    """ 取主站url，即https://xxx/ 为止 """
    return '/'.join(url.split('/')[:3])
    