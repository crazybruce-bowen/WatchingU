# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:25:27 2023

@author: 47176
"""

#%% Key
import requests
import ast


url = 'https://restapi.amap.com/v5/direction/driving'

key = '5bbb6851e17bded31b146e95f8cd17c9'
#%% 取位置
# url = 'https://restapi.amap.com/v3/geocode/geo?parameters'

# 锦绣华都position
origin = '121.580804,31.154171'

# 高铁站position

destination = '121.320205,31.193935'

# 结果控制
show_fields = 'cost'
#%% 测试路线返回

# 参数
d = {'key': key,
     'origin': origin,
     'destination': destination,
     'show_fields': show_fields
     }

# res = requests.get(url+f'?key={key}&origin=121.580804,31.154171&destination=121.320205,31.193935')
res = requests.get(url, params=d)

print(res.text)


#%% 完整功能测试
import ast
import requests

address = '浙港国际'
city = '杭州市'
url = 'https://restapi.amap.com/v3/geocode/geo'
key = '5bbb6851e17bded31b146e95f8cd17c9'

params = {
    'address': address,
    'city': city,
    'key': key}

aa = requests.get(url, params=params)

aa_dict = ast.literal_eval(aa.text)

geocodes_info = aa_dict.get('geocodes')

if geocodes_info:
    location = geocodes_info[0].get('location')
else:
    location = None

if location:
    destination = '121.320205,31.193935'
    show_fields = 'cost'
    url = 'https://restapi.amap.com/v5/direction/driving'
    d = {'key': key,
         'origin': location,
         'destination': destination,
         'show_fields': show_fields
         }

    # res = requests.get(url+f'?key={key}&origin=121.580804,31.154171&destination=121.320205,31.193935')
    res = requests.get(url, params=d)

    print(res.text)


#%%
"""
TODO list
1. 根据地址获取原始坐标信息
2. 根据原始坐标信息整理成标准坐标信息
3. 根据标准坐标信息获取到某固定坐标的路径规划原始信息
4. 根据4的原始信息整理成行车耗时等信息

"""

key = '5bbb6851e17bded31b146e95f8cd17c9'


# 1
def get_location_dict(address, city) -> dict:
    """
    地理编码
    """
    url = 'https://restapi.amap.com/v3/geocode/geo'
    params = {
        'address': address,
        'city': city,
        'key': key}
    res = requests.get(url, params)
    if not res.text:
        return None
    dic_res = ast.literal_eval(res.text)
    return dic_res


# 2
def analyse_location_info(address_info) -> str:
    geocodes = address_info.get('geocodes')
    if not geocodes:
        return None
    res = geocodes[0].get('location')
    return res

# 2*
def get_locaion_str(address, city) -> str:
    url = 'https://restapi.amap.com/v3/geocode/geo'
    res = analyse_location_info(get_location_dict(address, city))
    return res

# 3
def get_drive_info(location: str, destination='121.320205,31.193935') -> dict:
    """
    获取初始地到目标地的开车信息
    
    Parameters
    ----------
    location : str
        起始地坐标.
    destination : str, optional
        目标地坐标, 默认虹桥机场 '121.320205,31.193935'.

    Returns
    -------
    None.

    """
    url = 'https://restapi.amap.com/v5/direction/driving'
    show_fields = 'cost'
    params = {'key': key,
              'origin': location,
              'destination': destination,
              'show_fields': show_fields
              }
    res = requests.get(url, params=params)
    if not res.text:
        return None
    info_dict = ast.literal_eval(res.text)
    return info_dict

# 4.1
def analyse_drive_info(drive_info: dict, attr='time'):
    """
    
    """
    route_info = drive_info.get('route')
    path_info = route_info.get('paths')
    cost = 0
    for i in path_info:
        cost += int(i.get('cost').get('duration', 0))
    cost /= 3 
    cost = round(cost / 60, 2)
    return cost


# 5
dict_destination = {
    '上海虹桥站': '121.319321,31.194743',
    '上海虹桥机场': '121.348630,31.190784',
    '杭州东站': '120.212427,30.291538',
    '杭州火车站': '120.181851,30.243535',
    '蚂蚁': '120.108086,30.267078',
    
    }

def get_drive_time(address, city, destination):
    """
    输入地址, 返回到杭州东站的

    Parameters
    ----------
    address : TYPE
        DESCRIPTION.
    city : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    destination_position = dict_destination.get(destination)
    if not destination_position:
        destination_position = get_locaion_str(destination, city=city)
    location_info = get_location_dict(address, city)
    location = analyse_location_info(location_info)
    drive_info = get_drive_info(location)
    cost_time = analyse_drive_info(drive_info)
    return cost_time

#%%
if __name__ == '__main__':
    address = '锦绣华都'
    city = '上海市'
    location_info = get_location_dict(address, city)
    location = analyse_location_info(location_info)
    drive_info = get_drive_info(location)
    cost_time = analyse_drive_info(drive_info)
