import pandas as pd
import sys
import os
from dataclasses import dataclass
from tensorflow import keras


proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class CityCode:
    url_ziroom = 'https://www.ziroom.com/'
    url_lianjia = 'https://www.lianjia.com/'
    path = 'data/标准城市信息对照表.xlsx'
    df = pd.read_excel(os.path.join(proj_path, path), dtype=str)
    city_code = df['city_code'].dropna().tolist()
    city_cn = df['city_cn'].dropna().tolist()
    city_cn2 = df['city_cn2'].dropna().tolist()
    city_en = df['city_en'].dropna().tolist()
    city_en_abbr = df['city_en_abbr'].dropna().tolist()
    city_url_lianjia = df['city_url_lianjia'].dropna().tolist()
    city_url_ziroom = df['city_url_ziroom'].dropna().tolist()


@dataclass
class DefaultInfo:
    city = 'sh'
    city_code = '001'
    amap_api_process_data = 'result/process_data'


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


@dataclass
class ZiRoomFilter:
    # 链家filter对照关系
    rent_type_mapper = {'整租': 'z2', '合租': 'z1'}
    toward_mapper = {'东': '1', '西': '3', '南': '2', '北': '4'}
    room_num_mapper = {1: '13', 2: '14', 3: '15'}

    @classmethod
    def make_towards_str(cls, towards: list or str):
        """
        制作朝向使用的字符

        :param towards:
        :return:
        """
        ops = cls()
        if isinstance(towards, str):
            towards = [towards]
        res = f'&p=g{ops.toward_mapper.get(towards[0])}'
        if len(towards) > 1:
            for i in towards[1:]:
                res += f'|{ops.toward_mapper.get(i)}'
        return res

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

    @classmethod
    def make_room_num_str(cls, room_num: list or int) -> str:
        """ 制作房间数量的字符 """
        ops = cls()
        if isinstance(room_num, int):
            room_num = [room_num]
        res = f'u{ops.room_num_mapper.get(room_num[0])}'
        # 参数校准
        for i in range(len(room_num)):
            if room_num[i] >= 3:
                room_num[i] = 3
        room_num = list(set(room_num))
        # 计算
        if len(room_num) > 1:
            for i in room_num[1:]:
                i = min(i, 3)
                res = res + '%7C' + ops.room_num_mapper.get(i)
        return res


@dataclass
class ZiRoomPriceModel:
    model_path = os.path.join(proj_path, r'自如房价训练用\pre_trained.h5')
    model = keras.models.load_model(model_path)


@dataclass
class Others:
    cols_excel = ['原始标题', '类型', '房源url', '来源', '小区', '租金', '原始描述', '面积', '房型', '居室数', '楼层描述',
                  '楼层', '朝向', '图片url', '价格信息', '位置信息', '其他标签']
    cols_mariadb = ['title', 'type', 'url', 'source', 'xiaoqu', 'cost', 'desc', 'area', 'layout', 'room_num',
                    'desc_floor', 'floor', 'toward', 'orientation', 'desc_price', 'desc_location', 'desc_others']
