# 本方法为数据导出等功能
import copy

import pandas as pd
import numpy as np
import os
import pymongo


def save_info_to_local(info: [dict], path: str, file_name='info.xlsx', data_type='DataFrame'):
    """
    将信息存入本地的方法

    :param info: 信息。dict组成的list
    :param path: 输出路径，不包含文件名
    :param file_name: 输出文件名
    :param data_type: 输出文件的格式。目前支持 'json' 和 'DataFrame'
    :return: True/False, info
    """
    # 生成输出路径
    if not os.path.isdir(path):
        os.mkdir(path)
    # 生成输出的信息
    if data_type == 'DataFrame':
        df = pd.DataFrame.from_dict(info)
        df.to_excel(os.path.join(path, file_name), index=False)
        data = df
    elif data_type == 'json':
        with open(os.path.join(path, file_name), 'w') as f:
            f.write(info)
        data = info
    else:
        raise Exception('不支持的信息存入方法，请修改data_type参数')

    return True, data


def save_info_to_mongodb(info: [dict], db_config: dict, server_config=None):
    """
    将信息存入mongodb

    :param info: 要存入的信息
    :param db_config: 数据库信息，要求包含库名，表（集合）名。如{}
    :param server_config:
    :return:
    """
    _info = copy.deepcopy(info)
    # 参数解析
    if server_config:
        host = server_config.get('host')
        port = server_config.get('post')
    else:
        host = 'localhost'
        port = 27017
    db_name = db_config.get('db_name')
    tb_name = db_config.get('tb_name')
    if not db_name or not tb_name:
        raise Exception('数据库信息错误，需要包含db_name和tb_name参数')
    # 开始操作
    client = pymongo.MongoClient(host, port)
    db = client.get_database(db_name)
    tb = db.get_collection(tb_name)
    tb.insert_many(_info)
    return True




