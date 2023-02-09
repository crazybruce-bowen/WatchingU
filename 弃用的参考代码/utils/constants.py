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
