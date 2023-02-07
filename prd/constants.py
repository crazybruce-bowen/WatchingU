import pandas as pd
import sys
import os
from dataclasses import dataclass
proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class CityCode:
    url_ziru = 'https://www.ziroom.com/'
    url_lianjia = 'https://www.lianjia.com/'
    path = 'data/标准城市信息对照表.xlsx'
    df = pd.read_excel(os.path.join(proj_path, path), dtype=str)
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


@dataclass
class LjFilter:
    # 链家filter对照关系
    rent_type_mapper = {'整租': 'rt200600000001', '合租': 'rt200600000002'}
    toward_mapper = {'东': 'f100500000001', '西': 'f100500000005', '南': 'f100500000003', '北': 'f100500000007',
                     '南北': 'f100500000009'}

    @staticmethod
    def price_mapper(p: int, method='left'):
        """
        生成price filter字符

        参数:
            p: 价格
            method: 可选 【left|right】
        """
        if method == 'left':
            res = f'brp{p}'
        elif method == 'right':
            res = f'erp{p}'
        else:
            raise Exception('生成价格仅可使用left或者right参数')
        return res

    @staticmethod
    def room_num_mapper(n: int):
        """ 房间数量对应字符, n为房间数 """
        if n >= 4:
            n = 4
        return f'l{n - 1}'