import sys
import os
import logging
import time
import datetime
import traceback
import pandas as pd
import argparse
import copy

path_code = os.path.dirname(__file__)
path_root = os.path.dirname(path_code)
if path_code not in sys.path:
    sys.path.append(path_code)

from core.core_catching import RoomInfoCatching, RoomInfoCatchingLJ, RoomInfoCatchingZR, HouseDistrictCatching
from utils.log_service import Logging
from utils.io_service import save_info_to_local, save_info_to_mongodb, test_db_connect

logger = Logging().log(level='INFO')


def main(city=None, local_path: str=None, db_config: dict=None, tag_local=True, tag_db=False,
         model_path=None, house_district=False, multi_process=False, *args, **kwargs):
    """

    :param local_path:  存入本地的路径 注 会在该路径下生成LJ和ZR两个文件夹, 代表链家和自如。默认在项目result中
    :param db_config:  MongoDB config, 如手动输入, 需要有如下字段
        host
        port
        db_name
        tb_name_lj  链家的库名
        tb_name_zr  自如的库名
        tb_name_hd  链家小区的库名，如果计算小区的话
    :param tag_local:  是否存入本地
    :param tag_db:  是否存入数据库
    :param model_path:  预测自如房价的预训练模型路径 图片文字识别模型路径, 如自行添加, 需要该类存在predict方法即可
    :param house_district:  是否计算小区数据 计算耗时较久
    :param multi_process:  是否使用multi_process
    :return:
    """
    if tag_db:  # 测试数据库链接
        if not db_config:  # 默认存local
            r = test_db_connect({'host': 'localhost', 'port': 27017})
        else:
            r = test_db_connect(db_config)
        if not r:
            return False, 'mongo数据库链接失败, 请检查配置 {}'.format(db_config)

    time_tag = datetime.datetime.today().strftime('%Y%m%d')

    if not multi_process:
        time0 = time.time()  # 开始时间
        if not city:
            logger.info('== 开始获取链家的房源信息 {} =='.format(time.asctime()))
            info_lj = RoomInfoCatchingLJ().get_room_info_total()
            logger.info('== 链家房源信息获取完毕，开始获取自如房源信息 {} =='.format(time.asctime()))
            info_zr = RoomInfoCatchingZR().get_room_info_total()
        else:
            logger.info('== 开始获取链家的房源信息 {} =='.format(time.asctime()))
            info_lj = RoomInfoCatchingLJ.init_city(city).get_room_info_total()
            logger.info('== 链家房源信息获取完毕，开始获取自如房源信息 {} =='.format(time.asctime()))
            info_zr = RoomInfoCatchingZR.init_city(city).get_room_info_total()
        
        logger.info('== 自如房源信息获取完毕 {} =='.format(time.asctime()))
        if not model_path:
            model_path = os.path.join(path_root, r'code\utils\orc\pre_trained_model\LR_0906.pickle')
        # 添加价格
        t = RoomInfoCatchingZR()
        for i in info_zr:
            i['price'] = t.get_price(i['price_info'], model_path)
        logger.info('== 自如房源价格计算完毕 {} =='.format(time.asctime()))
        # 添加均价
        for i in info_zr:
            try:
                avg_price = round(float(i['price']) / float(i['area']), 2)
            except:
                avg_price = ''
            i['avg_price'] = avg_price
        # 整理数据
        info_zr = RoomInfoCatching.update_info(info_zr, 'ZR')
        info_lj = RoomInfoCatching.update_info(info_lj, 'LJ')
        if house_district:  # 计算小区信息
            hd = HouseDistrictCatching()
            info_hd = hd.get_total_hd_info()
            # 数据中添加小区信息
            tmp_df_zr = pd.DataFrame(info_zr)
            tmp_df_lj = pd.DataFrame(info_lj)
            tmp_df_hd = pd.DataFrame(info_hd)
            info_zr = tmp_df_zr.merge(tmp_df_hd[['小区', '小区均价']], on='小区', how='left').to_dict('records')
            info_lj = tmp_df_lj.merge(tmp_df_hd[['小区', '小区均价']], on='小区', how='left').to_dict('records')
        # 写入local
        if tag_local:
            if not local_path:
                local_path = os.path.join(path_root, 'result')
            path_lj = os.path.join(local_path, 'LJ')
            path_zr = os.path.join(local_path, 'ZR')
            if not os.path.isdir(path_lj):
                os.makedirs(path_lj)
            if not os.path.isdir(path_zr):
                os.makedirs(path_zr)
            save_info_to_local(info_lj, path_lj, 'LJ_room_info_{}.xlsx'.format(time_tag))
            save_info_to_local(info_zr, path_zr, 'ZR_room_info_{}.xlsx'.format(time_tag))
            if house_district:  # 计算小区信息
                save_info_to_local(info_hd, local_path, 'house_district_info_{}.xlsx'.format(time_tag))
            logger.info('== 写入本地 {} 完成 {} =='.format(local_path, time.asctime()))
        # 写入数据库
        if tag_db:
            if not db_config:  # 默认存local
                db_config_lj = {'db_name': 'crawler',
                                'tb_name': 'room_info_lj_{}'.format(time_tag)}
                db_config_zr = {'db_name': 'crawler',
                                'tb_name': 'room_info_zr_{}'.format(time_tag)}
                save_info_to_mongodb(info_lj, db_config_lj)
                save_info_to_mongodb(info_zr, db_config_zr)
                if house_district:
                    db_config_hd = {'db_name': 'crawler',
                                    'tb_name': 'house_district_info_{}'.format(time_tag)}
                    save_info_to_mongodb(info_hd, db_config_hd)
            else:
                db_config_lj = {'db_name': db_config['db_name'], 'tb_name': db_config['tb_name_lj']}
                db_config_zr = {'db_name': db_config['db_name'], 'tb_name': db_config['tb_name_zr']}
                server_config = {'host': db_config['host'], 'port': db_config['port']}
                save_info_to_mongodb(info_lj, db_config_lj, server_config)
                save_info_to_mongodb(info_zr, db_config_zr, server_config)
                if house_district:
                    db_config_hd = {'db_name': db_config['db_name'], 'tb_name': db_config['tb_name_hd']}
                    save_info_to_mongodb(info_hd, db_config_hd, server_config)
            logger.info('== 写入数据库 {} {}和{} 完成 {} =='.format(db_config_lj['db_name'],
                                                            db_config_lj['tb_name'],
                                                            db_config_zr['tb_name'],
                                                            time.asctime()))

    else:
        raise Exception('暂未开放')
    logger.info('== 全部任务完成，共耗时 {} 秒 =='.format(int(time.time() - time0)))
    return True


def make_argsparse():
    """
    参数生成。此方法默认直接使用python解释器执行, 故tag_local强制为True
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('--city', type=str)  # 需要访问的城市名, 如未输入，默认上海
    parse.add_argument('--local_path', type=str)  # 本地存储路径
    parse.add_argument('--db_host', type=str) # 存入的数据库host地址
    parse.add_argument('--db_port', type=str) # 存入的数据库port地址
    parse.add_argument('--db_name', type=str) # 存入的数据库db名
    parse.add_argument('--db_tb_name_lj', type=str) # 存入的数据库链家tb名
    parse.add_argument('--db_tb_name_zr', type=str) # 存入的数据库自如tb名
    parse.add_argument('--tb_name_hd', type=str) # 存入的数据库链家小区名   
    parse.add_argument('--tag_db', default='False', action='store_true') # 是否存入数据库 
    parse.add_argument('--house_district', default='False', action='store_true') # 是否计算小区数据   
    parse.add_argument('--multi_process', default='False', action='store_true') # 是否使用multiprocess
    parse.add_argument('--model_path', type=str) # 用于自如价格图像分割识别数字的模型路径，建议不要修改，使用本项目自带的部分       
    
    args = copy.deepcopy(parse.parse_args().__dict__)
    
    if args.get('tag_db') == True:
        args['db_config'] = {
            'db_host': args.get('db_host'), 'db_port': args.get('db_port'), 'db_name': args.get('db_name'), 
            'db_tb_name_lj': args.get('db_tb_name_lj'), 'db_tb_name_zr': args.get('db_tb_name_zr'), 'tb_name_hd': args.get('tb_name_hd'),
            }
    
    return args


def run_script(args: dict):
    """ 用argparse的方法执行的入口 """
    return main(**args)


if __name__ == '__main__':
    try:
        main(tag_db=True, house_district=True)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
