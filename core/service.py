from requests.exceptions import RequestException
import requests
from pyquery import PyQuery as pq
from core.utils import get_city_info, get_city_code
import ast
import mariadb
import time


# ==============================================
# url爬取html  *要求网络


# 根据url获取html文件
class HttpService:
    @staticmethod
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
    @classmethod
    def get_doc_from_url(cls, url: str) -> pq:
        """ 解析url直接到pq格式 """
        doc = pq(cls().get_one_page_html(url))
        return doc


# 高德接口服务
class AmapApiService:
    """
    高德接口服务, 详见https://lbs.amap.com/api/webservice/summary/
    """
    def __init__(self, city):
        """
        初始化继承city信息, city信息非常重要, 输入中文, 英文均可

        :param city:
        """
        self.city = get_city_info(get_city_code(city), 'city_cn2')
        self.key = '5bbb6851e17bded31b146e95f8cd17c9'
        self.destination_dict = {
            '上海虹桥站': '121.319321,31.194743',
            '上海虹桥机场': '121.348630,31.190784',
            '杭州东站': '120.212427,30.291538',
            '杭州火车站': '120.181851,30.243535',
            '蚂蚁': '120.108086,30.267078',
            }
        self.help_url = 'https://lbs.amap.com/api/webservice/summary/'

    def get_location_dict(self, address) -> dict or None:
        """
        地理编码, 转换地理位置到坐标, 返回字典

        """
        url = 'https://restapi.amap.com/v3/geocode/geo' # 地理编码的url, 详见self.help_url
        params = {
            'address': address,
            'city': self.city,
            'key': self.key}
        res = requests.get(url, params)
        if not res.text:
            return None
        dic_res = ast.literal_eval(res.text)
        return dic_res

    @staticmethod
    def analyse_location_info(address_info) -> str or None:
        """
        解析地理编码内容, 提取坐标字符串

        :return:
        """
        geocodes = address_info.get('geocodes')
        if not geocodes:
            return None
        res = geocodes[0].get('location')
        return res

    def get_location_str(self, address) -> str:
        """
        地理编码, 转换地理位置到坐标, 返回字符串

        :param address:
        :return:
        """
        res = self.analyse_location_info(self.get_location_dict(address))
        return res

    def get_drive_info(self, location: str, destination='121.320205,31.193935') -> dict or None:
        """
        获取初始地到目标地的开车信息

        Parameters
        ----------
        location : str
            起始地坐标.
        destination : str, optional
            目标地坐标, 默认虹桥机场 '121.320205,31.193935'.
        """
        url = 'https://restapi.amap.com/v5/direction/driving'  # 路径规划url
        show_fields = 'cost'
        params = {'key': self.key,
                  'origin': location,
                  'destination': destination,
                  'show_fields': show_fields
                  }
        res = requests.get(url, params=params)
        if not res.text:
            return None
        info_dict = ast.literal_eval(res.text)
        return info_dict

    @staticmethod
    def analyse_drive_info(drive_info: dict, attr='time'):
        """
        解析导航信息, 目前仅提供计算时间功能

        """
        route_info = drive_info.get('route')
        if not route_info:
            return None
        path_info = route_info.get('paths')
        res = None
        if attr == 'time':
            cost = 0
            for i in path_info:
                cost += int(i.get('cost').get('duration', 0))
            cost /= 3
            cost = round(cost / 60, 2)
            res = cost
        return res

    def get_drive_time(self, address, destination):
        """
        直接获取到目的地的驾车耗时

        :param address:
        :param destination:
        :return:
        """
        destination_position = self.destination_dict.get(destination)
        if not destination_position:
            print(f'= 未获取目标destination {destination} 的地址 =')
            destination_position = self.get_location_str(destination)
        location_info = self.get_location_dict(address)
        location = self.analyse_location_info(location_info)
        drive_info = self.get_drive_info(location, destination_position)
        if not drive_info:
            return None
        cost_time = self.analyse_drive_info(drive_info)
        return cost_time


# 数据库连接服务
class DatabaseService:

    def __init__(self, user='root', password='root', host='localhost', port='3306'):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self):
        self.conn = mariadb.connect(user=self.user, password=self.password, host=self.host, port=self.port)
        self.cursor = self.conn.cursor()

    def __exit__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_sql(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()

    # def create_table(self, db, tb, info):
    #     """
    #     建表指令
    #
    #     :param db:
    #     :param tb:
    #     :param cols:
    #     :return:
    #     """
    #     sql = f'CREATE {db}\.{tb} \(\)'

    def insert_info(self, db, tb, info: dict):
        """
        插入一条数据

        :param db: 数据库名
        :param tb: 数据表名
        :param info: 字典格式, 将会将每个k作为字段名, v作为值输入
        :return:
        """
        list_keys = ' '.join(list(str(i) for i in info.keys()))
        list_values = ' '.join(list(str(i) for i in info.values()))
        sql = f'INSERT INTO {db}\.{tb} \({list_keys}\) VALUES \({list_values}\)'
        self.execute_sql(sql)
        return True

    # def check_table_exist(self):



