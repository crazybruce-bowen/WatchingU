import time
from dataclasses import dataclass


@dataclass
class G_LJ:
    city_list = ['北京', '长春', '成都', '重庆', '长沙', '大连', '青岛', '上海', '石家庄', '苏州', '沈阳', '深圳', '天津', '太原', '武汉', '无锡', '西安', '厦门', '烟台', '郑州']
    url_list = ['https://bj.lianjia.com/', 'https://cc.lianjia.com/', 'https://cd.lianjia.com/', 'https://cq.lianjia.com/', 'https://cs.lianjia.com/', 'https://dl.lianjia.com/', 'https://qd.lianjia.com/', 'https://sh.lianjia.com/', 'https://sjz.lianjia.com/', 'https://su.lianjia.com/', 'https://sy.lianjia.com/', 'https://sz.lianjia.com/', 'https://tj.lianjia.com/', 'https://ty.lianjia.com/', 'https://wh.lianjia.com/', 'https://wx.lianjia.com/', 'https://xa.lianjia.com/', 'https://xm.lianjia.com/', 'https://yt.lianjia.com/', 'https://zz.lianjia.com/']
    citycode_list = ['bj', 'cc', 'cd', 'cq', 'cs', 'dl', 'qd', 'sh', 'sjz', 'su', 'sy', 'sz', 'tj', 'ty', 'wh', 'wx', 'xa', 'xm', 'yt', 'zz']
    ciry2url_mapper = dict(zip(city_list, url_list))
    citycode2url_mapper = dict(zip(citycode_list, url_list))


@dataclass
class G_ZR:
    city_list = ['北京', '上海', '深圳', '杭州', '南京', '成都', '武汉', '广州', '天津', '苏州']
    url_list = ['https://www.ziroom.com/', 'https://sh.ziroom.com/', 'https://sz.ziroom.com/', 'https://hz.ziroom.com/', 'https://nj.ziroom.com/', 'https://cd.ziroom.com/', 'https://wh.ziroom.com/', 'https://gz.ziroom.com/', 'https://tj.ziroom.com/', 'https://su.ziroom.com/']
    citycode_list = ['bj', 'sh', 'sz', 'hz', 'nj', 'cd', 'wh', 'gz', 'tj', 'su']
    city2url_mapper = dict(zip(city_list, url_list))
    citycode2url_mapper = dict(zip(citycode_list, url_list))


def print_time(f):
    """Decorator of viewing function runtime.
    eg:
        ```py
        from print_time import print_time as pt
        @pt
        def work(...):
            print('work is running')
        word()
        # work is running
        # --> RUN TIME: <work> : 2.8371810913085938e-05
        ```
    """
    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %s' % (f.__name__, round(float(time.time() - s), 2)))
        return res
    return fi
