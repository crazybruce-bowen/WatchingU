#%%
import os
import sys
import traceback
from pyquery import PyQuery as pq
import re
import requests
import numpy as np
import time
import pickle

now_dir = os.path.dirname(__file__)
path_code = os.path.dirname(now_dir)
path_root = os.path.dirname(path_code)
if path_root not in sys.path:
    sys.path.append(path_root)

from code.utils.common_utils import print_time
from code.utils.html_service import get_one_page_html
from code.utils.io_service import save_info_to_local, save_info_to_mongodb
from code.utils.orc_service import PricePredict

#%%
class RoomInfoCatching:
    """ 基类 """
    def __init__(self):
        print('== Hi U ==')

    @classmethod
    def update_info(cls, room_info: [dict], source='ZR'):
        res = list()
        tmp = dict()
        for i in room_info:
            if source == 'ZR':
                tmp['小区'] = re.sub('\d居室', '', i['name'].split('·')[-1].split('-')[0])
                tmp['朝向'] = i['name'].split('-')[-1] if len(i['name'].split('-')) > 1 else ''
            else:
                tmp['小区'] = i['name'].split('-')[-1]
                tmp['朝向'] = i['orientation']
            tmp['平米均价'] = i['avg_price']
            tmp['房源链接'] = i['room_url']
            tmp['区域'] = i['区域']
            tmp['户型'] = i['room_types'].replace(' ', '')
            tmp['价格'] = i.get('price')
            tmp['面积'] = i['area']
            tmp['楼层'] = i['floor']
            res.append(tmp)
        return res


class RoomInfoCatchingLJ(RoomInfoCatching):
    """ 小区信息提取 """
    def __init__(self, url_base=None):
        """ base_url: 链家首页 """
        self.url_base = url_base if url_base else 'https://sh.lianjia.com'
        # 均价5k-8k以上房源 TODO 修改为动态生成
        self.url_selection = 'https://sh.lianjia.com/zufang/rt200600000001l0l1rp6/?showMore=1'
        self.urls_area = None
        super().__init__()

    def generate_area_urls(self):
        """
        解析主页，生成分区域分页

        :return:
            [{'area': 小区区域, 'url': 分页地址}]
        """
        doc = pq(get_one_page_html(self.url_selection))
        res = []
        for i in doc('ul[data-target=area]')('a').items():
            if i.text() != '不限':
                res.append({'area': i.text(),
                            'url': self.url_base + i.attr('href')})
        self.urls_area = res

        return res

    def get_url_by_area(self, area):
        """ 获取某区域的url """
        area_info_list = self.generate_area_urls() if not self.urls_area else self.urls_area
        area_url = dict(zip([i['area'] for i in area_info_list], [i['url'] for i in area_info_list])).get(area)
        return area_url

    def find_page_url(self, url_area) -> [str]:
        """ 根据区域url获取分页url list """
        doc = pq(get_one_page_html(url_area))
        res = [url_area]
        for i in doc('div.content__article > ul[style=display\:hidden] > li > a').items():
            res.append(self.url_base + i.attr('href'))  # 第二页开始的分页
        return res

    def find_room_url(self, url_pg) -> [dict]:
        """ 根据分页地址去解析房间url链接 """
        doc = pq(get_one_page_html(url_pg))
        urls_info = doc('.content__list')('div > a').items()
        res = []
        for i in urls_info:
            room_name = i.attr('title')
            url_ = i.attr('href')
            room_url = self.url_base + url_
            res.append({'room_name': room_name,
                        'url': room_url})
        return res

    def get_room_info_page(self, url_pg) -> [dict]:  # 获取一整个页面的房间信息
        """
        根据分页的页面获取房源信息

            name: 房间名
            area: 面积
            price: 房间价格
            orientation: 朝向
            types: 房间类型
            floor: 房间楼层
            updated_info: 房间维护信息
        """

        doc = pq(get_one_page_html(url_pg))  # doc
        room_info = doc('.content__list--item--main').items()  # generator
        res = []
        for i in room_info:
            room_url = self.url_base + i('.twoline').attr('href')
            desc = i('.content__list--item--des').text()
            price_str = i('.content__list--item-price').text()
            updated_info = i('.content__list--item--time.oneline').text()
            desc_vec = desc.replace(' ', '').split('/')
            name = desc_vec[0]
            area_str = desc_vec[1]
            orientation = desc_vec[2]
            types = desc_vec[3]
            floor = desc_vec[4]
            price = float(re.findall('(\d+).* +元/月', price_str)[0])
            area = float(re.findall('(.*)㎡', area_str)[0])
            avg_price = round(price / area, 2)
            sub_area = name.split('-')[1]
            dict_info = {'name': name, 'area_str': area_str, 'price_str': price_str,
                         'area': area, 'price': price, 'avg_price': avg_price,
                         'orientation': orientation, 'room_types': types, 'floor': floor,
                         'updated_info': updated_info, '子区域': sub_area,
                         'room_url': room_url}
            res.append(dict_info)
        return res

    @staticmethod
    def get_room_info(url_room) -> dict:
        """ 获取单个房源url的信息, 暂时不需要房源额外信息，防止过多调用 """
        print(url_room)
        return dict()

    def get_room_info_by_area(self, area):
        area_url = self.get_url_by_area(area)
        if not area_url:
            return False, '未获取到该区 {} 的链接，支持的区域为 {}'.format(area, [i['area'] for i in self.generate_area_urls()])

        urls_area_pg = self.find_page_url(area_url)
        room_info_total = list()
        print('== 该区域 {} 共有页面 {} 个'.format(area, len(urls_area_pg)))
        n = 0
        for i in urls_area_pg:
            n += 1
            print('== 开始计算第 {} 个页面 =='.format(n))
            room_info_list = self.get_room_info_page(i)
            for room_info in room_info_list:
                room_info['区域'] = area
            room_info_total += room_info_list
        return room_info_total

    @print_time
    def get_room_info_total(self):
        urls_area_list = self.generate_area_urls()
        room_info_total = list()
        for i in urls_area_list:
            room_info_total += self.get_room_info_by_area(i['area'])
            print('== 完成 {} 区域'.format(i['area']))
        return room_info_total

    # def main_multiprocess(self, area):
    #     """ 子进程方法执行全量数据 """
    #     print('=== 子进程开始执行 {} 区域 ==='.format(area))
    #     room_info_total = self.get_room_info_by_area(area)
    #     out_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家\result\20220816'
    #     file_name = area + '_20220816.xlsx'
    #     save_info_to_local(room_info_total, out_path, file_name)
    #     print('== {} 区域存储本地完毕，开始写入数据库 =='.format(area))
    #
    #     db_config = {'db_name': 'bw_test', 'tb_name': 'room_info_0816'}
    #     save_info_to_mongodb(room_info_total, db_config)
    #     print('== {} 区域数据库写入完毕 =='.format(area))
    #     print('=== 子进程 {} 区域执行完毕 ==='.format(area))


class RoomInfoCatchingZR(RoomInfoCatching):
    def __init__(self):
        self.url_base = 'https://sh.ziroom.com/'
        self.url_selectoin = 'https://sh.ziroom.com/z/z2-r0/?cp=4000TO8000'  # 4k-8k TODO 改成动态生成
        self.urls_area = None
        self.url_pic = dict()
        super().__init__()

    def generate_area_urls(self):
        doc = pq(get_one_page_html(self.url_selectoin))
        urls_items = doc('div.opt-type')(' span.opt-name:contains(区域)').parent()('div.wrapper a.item').items()
        res = list()
        for i in urls_items:
            res.append({'area': i.text(),
                        'url': 'https:' + i.attr('href')})
        self.urls_area = res
        return res

    def get_url_by_area(self, area):
        """ 获取某区域的url """
        area_info_list = self.generate_area_urls() if not self.urls_area else self.urls_area
        area_url = dict(zip([i['area'] for i in area_info_list], [i['url'] for i in area_info_list])).get(area)
        return area_url

    @staticmethod
    def find_page_url(url_area) -> [str]:
        """ 根据区域url获取分页url list """
        doc = pq(get_one_page_html(url_area))
        page_num_text = doc('div.Z_pages span:contains(共)').text()
        if not page_num_text:
            return list()
        page_num = int(re.findall('共(\d+)页', page_num_text)[0])
        url_page1 = 'https:' + doc('div.Z_pages a.active').attr('href')
        tmp = re.match('(.*p)\d(.*)', url_page1)
        res = list()
        for i in range(page_num):
            res.append(tmp.group(1) + str(i) + tmp.group(2))
        return res

    @staticmethod
    def find_room_url(url_pg) -> [dict]:
        """ 根据分页地址去解析房间url链接 """
        doc = pq(get_one_page_html(url_pg))
        info_items = doc('div.Z_list-box h5.title a').items()
        res = list()
        for i in info_items:
            res.append({'room_name': i.text(),
                        'url': i.attr('href')})
        return res

    @staticmethod
    def get_room_info_page(url_pg) -> [dict]:  # 获取一整个页面的房间信息
        """
        根据分页的页面获取房源信息

            name: 房间名
            area: 面积
            price: 房间价格
            orientation: 朝向
            types: 房间类型
            floor: 房间楼层
            updated_info: 房间维护信息
        """

        doc = pq(get_one_page_html(url_pg))  # doc
        room_info = doc('div.item').items()
        res = list()
        for i in room_info:
            name = i('div.info-box a').text()  # 名称
            url = 'https:' + i('div.info-box a').attr('href')
            area_desc_str = i('div.desc div:nth-of-type(1)').text()
            area_str = area_desc_str.split('|')[0]
            area = float(re.findall('(.*)㎡', area_str)[0])  # 面积
            tmp_types = area_desc_str.split('|')[1]
            if len(tmp_types.split('/')) > 1:
                types = re.findall('.*(\d+居室).*', name)[0]
                floor = int(tmp_types.split('/')[0])
            else:
                types = tmp_types
                floor = ''
            locations = i('div.desc>div.location').text()
            price_info = '||'.join([num.attr('style') for num in i('div.price span.num').items()])  # ||分割改list为str
            tags = '||'.join([tag.text() for tag in i('div.tag span').items()])  # ||分割改list为str
            dict_info = {'name': name, 'room_url': url, 'area_str': area_str, 'price_info': price_info,
                         'area': area, 'room_types': types, 'locations': locations, 'tags': tags, 'floor': floor,
                         }
            res.append(dict_info)

        return res

    def get_room_info_by_area(self, area):
        area_url = self.get_url_by_area(area)
        if not area_url:
            return False, '未获取到该区 {} 的链接，支持的区域为 {}'.format(area, [i['area'] for i in self.generate_area_urls()])

        urls_area_pg = self.find_page_url(area_url)
        room_info_total = list()
        print('== 该区域 {} 共有页面 {} 个'.format(area, len(urls_area_pg)))
        n = 0
        for i in urls_area_pg:
            n += 1
            print('== 开始计算第 {} 个页面 =='.format(n))
            room_info_list = self.get_room_info_page(i)
            for room_info in room_info_list:
                room_info['区域'] = area
            room_info_total += room_info_list
        return room_info_total

    @print_time
    def get_room_info_total(self):
        urls_area_list = self.generate_area_urls()
        room_info_total = list()
        for i in urls_area_list:
            room_info_total += self.get_room_info_by_area(i['area'])
            print('== 完成 {} 区域'.format(i['area']))
        return room_info_total

    @print_time
    def get_price(self, s, model_path) -> int:
        """
        根据图片的字符信息（price_info 字段）生成数值型价格

        :param s: price_info 内容
        :param model_path: 模型文件路径

        :return:
        """
        from io import BytesIO
        from PIL import Image

        # 拆分price_info内容为list
        p_list = s.split('||')

        # 计算第N位数字
        num_str = str()
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        for i in p_list:
            ## 识别该位数字图片的url
            i_url = 'https:' + re.findall('url\((.*)\)', i)[0]
            if i_url not in self.url_pic:
                ## 根据url获取图片
                img = Image.open(BytesIO(requests.get(i_url).content))
                self.url_pic[i_url] = img
            else:
                img = self.url_pic[i_url]
            ## 图片分割并识别各个顺序位置的值
            pre_obj = PricePredict(img, model)
            p_str = ''
            for j in range(10):
                num_pre = pre_obj.predict(j)
                p_str += str(num_pre)
            # p_str = '1234567890'  # TODO 此处更换为正常数据
            ## 识别该位数字在图片中px位置，并转换为顺序位置
            px = re.findall('background-position: (.*)', i)[0]
            ### px转换position字典 人工学习结果
            px2pos = {'-0px': 0, '-21.4px': 1, '-42.8px': 2, '-64.2px': 3, '-85.6px': 4, '-107px': 5,
                      '-128.4px': 6, '-149.8px': 7, '-171.2px': 8, '-192.6px': 9}
            pos = px2pos.get(px)
            ## 生成该位数字的值
            num = p_str[pos]
            num_str += num
        # 拼接各位数字生成最终价格
        price = int(num_str)
        return price


class HouseDistrictCatching(RoomInfoCatching):
    """ 小区信息提取 """
    def __init__(self, base_url=None):
        """ base_url: 链家首页 """
        self.url_base = base_url if base_url else 'https://sh.lianjia.com'
        self.url_selection = 'https://sh.lianjia.com/xiaoqu/bp6ep10000/'  # 均价6w以上小区 TODO 修改为动态生成
        # self.html_base = get_one_page_html(self.url_selection)  # 筛选页首页html
        # self.doc_base = pq(self.html_base)  # 生成pg包的doc文件
        self.urls_area = None
        super().__init__()

    def generate_area_urls(self):
        """
        解析主页，生成分区域分页

        :return:
            [{'area': 小区区域, 'url': 分页地址}]
        """
        doc = pq(get_one_page_html(self.url_selection))
        res = []
        for i in doc('div[data-role=ershoufang]')('a').items():
            res.append({'area': i.text(),
                        'url': self.url_base + i.attr('href')})
        self.urls_area = res

        return res

    @staticmethod
    def generate_hd_urls(url) -> [dict]:
        """
        解析当前页面下的小区url

        :param url: 支持首页，区域页面，区域pg页等
        :return:
            [{'house': abc, 'url': 小区页面地址}]
        """
        doc = pq(get_one_page_html(url))
        res = []
        for i in doc('div.title > a').items():
            res.append({'house_district': i.text(),
                        'url': i.attr('href')})
        return res

    def calculate_pg_num(self, area=None, num_one_pg=30):
        """
        计算需要的pg数量

        :param area: 某区域
        :param num_one_pg: 网页中一页的房源
        :return:
        """
        if not area:
            doc = pq(get_one_page_html(self.url_selection))
            house_num = int(doc('div.resultDes')('h2.total.fl')('span').text())
        else:
            url_area = self.get_url_by_area(area)
            doc = pq(get_one_page_html(url_area))
            house_num = int(doc('div.resultDes')('h2.total.fl')('span').text())

        return int(house_num/num_one_pg)+1

    @staticmethod
    def get_hd_info(url_house):
        """ 获取小区基础信息 url_house: 房源的链接 """
        html_house = get_one_page_html(url_house)
        doc = pq(html_house)
        # base info
        items_key = doc('div.xiaoquInfoItem > span.xiaoquInfoLabel').items()
        info_key = [i.text() for i in items_key]
        items_value = doc('div.xiaoquInfoItem > span.xiaoquInfoContent').items()
        info_value = [i.text() for i in items_value]
        base_info_dict = dict(zip(info_key, info_value))
        # price
        items_price = doc('li.fl')('span').items()
        list_price = [int(re.findall('\\d+', i.text())[0]) for i in items_price]
        items_house_desc = doc('li.fl')('div.goodSellItemDesc').items()
        list_desc = [float(re.findall(r"\d+\.?\d*", i.text().split('/')[0])[0]) for i in items_house_desc]
        list_avgprice = [i/j for i, j in zip(list_price, list_desc)]
        base_info_dict['小区均价'] = round(np.mean(list_avgprice), 2) if list_avgprice else None
        return base_info_dict

    @staticmethod
    def generate_pg_url(url, n):
        """
        根据pg号生成页面，针对https://sh.lianjia.com/xiaoqu/**开头

        :param url: 区域页面或者总页面
        :param n: pg号
        :return: url_pg: 带pg号的url
        """
        tmp = url.split('/')
        tmp[-2] = 'pg{}'.format(n) + tmp[-2]
        url_pg = '/'.join(tmp)
        return url_pg

    def get_url_by_area(self, area):
        """ 获取某区域的url """
        area_info_list = self.generate_area_urls() if not self.urls_area else self.urls_area
        area_url = dict(zip([i['area'] for i in area_info_list], [i['url'] for i in area_info_list])).get(area)
        return area_url

    def get_area_hd_info(self, area):
        """ 获取某个区的全部小区信息 """
        area_url = self.get_url_by_area(area)
        if not area_url:
            return False, '未获取到该区 {} 的链接，支持的区域为 {}'.format(area, [i['area'] for i in self.generate_area_urls()])

        # 获取该区域全部小区的urls
        print('== 开始获取小区urls ==')
        pg_num = self.calculate_pg_num(area)
        urls_pg_list = [self.generate_pg_url(area_url, i) for i in range(pg_num)]
        urls_hd_list = list()
        for i in urls_pg_list:  # 区域循环
            urls_hd_list += self.generate_hd_urls(i)
        print('== {} 区域总计 {} 个小区'.format(area, len(urls_hd_list)))  # TODO 改成logging方法
        # 分url获取
        print('== 开始获取各小区信息 ==')
        hd_info_list = list()
        n = 0
        for i in urls_hd_list:
            try:
                house_info = self.get_hd_info(i.get('url'))
                house_info['小区'] = i.get('house_district')
                house_info['区域'] = area
                house_info['url'] = i.get('url')
                hd_info_list.append(house_info)
            except Exception as e:
                print('==== {} 小区信息获取失败 ===='.format(i.get('house_district')))
                print('==== 异常原因如下 =====', traceback.format_exc())
            n += 1
            if n % 100 == 0:
                print('=== 完成 {} 个小区，共有 {} 个'.format(n, len(urls_hd_list)))
        return hd_info_list

    @print_time
    def get_total_hd_info(self):
        """ 获取全区 """
        area_info_list = self.generate_area_urls() if not self.urls_area else self.urls_area
        print('= 分区域获取小区信息开始！共有 {} 个区域 = '.format(len(area_info_list)))
        hd_info_list = list()
        for i in area_info_list:
            area = i.get('area')
            print('== 开始操作 {} 区域'.format(area))
            time1 = time.time()
            hd_info_list += self.get_area_hd_info(area)
            timedelta = int(time.time() - time1)
            print('== 区域 {} 已经完成，耗时 {} 秒'.format(area, timedelta))
        return hd_info_list

    # def main_multiprocess(self, area):
    #     """ 子进程方法执行全量数据 """
    #     print('=== 子进程开始执行 {} 区域 ==='.format(area))
    #     room_info_total = self.get_area_hd_info(area)
    #     out_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\链家\result\20220816'
    #     file_name = area + '_小区_20220816.xlsx'
    #     save_info_to_local(room_info_total, out_path, file_name)
    #     print('== {} 区域存储本地完毕，开始写入数据库 =='.format(area))
    #
    #     db_config = {'db_name': 'bw_test', 'tb_name': 'house_district_info_20220816'}
    #     save_info_to_mongodb(room_info_total, db_config)
    #     print('== {} 区域数据库写入完毕 =='.format(area))
    #     print('=== 子进程 {} 区域执行完毕 ==='.format(area))
