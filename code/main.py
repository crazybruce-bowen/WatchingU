import sys
import os
import logging
import time
import datetime
path_code = os.path.dirname(__file__)
path_root = os.path.dirname(path_code)
if path_root not in sys.path:
    sys.path.append(path_root)

from code.core.core_catching import RoomInfoCatchingLJ, RoomInfoCatchingZR, HouseDistrictCatching
from code.utils.log_service import Logging
from code.utils.io_service import save_info_to_local, save_info_to_mongodb, test_db_connect

logger = Logging().log(level='INFO')


def main(local_path=None, db_config=None, tag_local=True, tag_db=False, multi_process=False):
    """

    :param local_path:  存入本地的路径 注 会在该路径下生成LJ和ZR两个文件夹，代表链家和自如。默认在项目result中
    :param db_config:  MongoDB config，如手动输入，需要有如下字段
        host
        port
        db_name
        tb_name_lj  链家的库名
        tb_name_zr  自如的库名
    :param tag_local:  是否存入本地
    :param tag_db:  是否存入数据库
    :param multi_process:  是否使用multi_process
    :return:
    """
    if tag_db:  # 测试数据库链接
        if not test_db_connect(db_config):
            return False, 'mongo数据库链接失败，请检查配置 {}'.format(db_config)
    if not multi_process:
        time0 = time.time()  # 开始时间
        logger.info('== 开始获取链家的房源信息 {} =='.format(time.asctime()))
        info_lj = RoomInfoCatchingLJ().get_room_info_total()
        logging.info('== 链家房源信息获取完毕，开始获取自如房源信息 {} =='.format(time.asctime()))
        info_zr = RoomInfoCatchingZR().get_room_info_total()
        logging.info('== 自如房源信息获取完毕 {} =='.format(time.asctime()))
        model_path = os.path.join(path_root, r'code\utils\orc\pre_trained_model\LR_0818.pickle')
        # 添加价格
        t = RoomInfoCatchingZR()
        for i in info_zr:
            i['price'] = t.get_price(i['price_info'], model_path)
        logging.info('== 自如房源价格计算完毕 {} =='.format(time.asctime()))
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
            save_info_to_local(info_lj, path_lj,
                               'LJ_room_info_{}.xlsx'.format(datetime.datetime.today().strftime('%Y%m%d')))
            save_info_to_local(info_zr, path_zr,
                               'ZR_room_info_{}.xlsx'.format(datetime.datetime.today().strftime('%Y%m%d')))
            logging.info('== 写入本地 {} 完成 {} =='.format(local_path, time.asctime()))
        # 写入数据库
        if tag_db:
            if not db_config:  # 默认存local
                db_config_lj = {'db_name': 'crawler',
                                'tb_name': 'room_info_lj_{}'.format(datetime.datetime.today().strftime('%Y%m%d'))}
                db_config_zr = {'db_name': 'crawler',
                                'tb_name': 'room_info_zr_{}'.format(datetime.datetime.today().strftime('%Y%m%d'))}
                save_info_to_mongodb(info_lj, db_config_lj)
                save_info_to_mongodb(info_zr, db_config_zr)
            else:
                db_config_lj = {'db_name': db_config['db_name'], 'tb_name': db_config['tb_name_lj']}
                db_config_zr = {'db_name': db_config['db_name'], 'tb_name': db_config['tb_name_zr']}
                server_config = {'host': db_config['host'], 'port': db_config['port']}
                save_info_to_mongodb(info_lj, db_config_lj, server_config)
                save_info_to_mongodb(info_zr, db_config_zr, server_config)
            logging.info('== 写入数据库 {} {}和{} 完成 {} =='.format(db_config_lj['db_name'],
                                                             db_config_lj['tb_name'],
                                                             db_config_zr['tb_name'],
                                                             time.asctime()))

    else:
        raise Exception('暂未开放')

    return True


if __name__ == '__main__':
    main(tag_db=True)
