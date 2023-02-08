import re
from typing import List
from prd.utils import *


class LianJiaHtmlOps:
    """ 链家html相关操作, 由于链家返回url均为城市主站+后缀, 故继承citycode信息 """

    def __init__(self, citycode=None):
        self.citycode = citycode if citycode else '001'
        self.city_url = get_lj_url(citycode)
        self.city_cn = get_city_info(citycode, 'city_cn')

    def city2area_dict(self, city_html) -> List[dict]:
        """
        链家html解析。解析city_doc, 提取可用的区级信息, 输出dict

        参数:
            city_html: 城市主页的html字符或pq(PyQuery)类型均可
            citycode: 项目城市编码
        """
        doc = make_standard_html(city_html)

        # 解析区域信息
        res = []
        for i in doc('ul[data-target=area]')('a').items():
            tmp = i.text()
            if tmp != '不限':
                res.append({'area': i.text(),  # 区域中文名
                            'url': self.city_url + i.attr('href')})  # 区域url

        return res

    def get_area_url(self, city_html, area: str):
        """
        获取城市某个区域的url

        :param city_html:
        :param area: 城市区域 中文
        :return:
        """
        d_area = self.city2area_dict(city_html)
        url_area = None
        for i in d_area:
            if i['area'] == area:
                url_area = i['url']
                break
        assert url_area, f'{self.city_cn} 中未找到区域 {area}'
        return url_area

    def city2area_list(self, city_html) -> list:
        """
        链家html解析。解析city_doc, 提取可用的区级信息, 输出dict

        参数:
            city_html: 城市主页的html字符或pq(PyQuery)类型均可
            citycode: 项目城市编码
        """
        doc = make_standard_html(city_html)
        d = self.city2area_dict(doc)
        res = []
        for i in d:
            area = i.get('area')
            if area:
                res.append(area)
        if not res:
            print(f'== Warning 该城市 {self.city_cn} 无可用区域 ==')
        return res

    def area_level2_dict(self, area_html) -> List[dict]:
        """
        链家二级区域信息获取, 提取二级区域名和对应的url, 输出dict

        参数:
            area_html: html字符或pq(PyQuery)类型均可

        """
        doc = make_standard_html(area_html)
        # 解析区域信息
        res = []
        doc('ul[data-target=area]').remove('[class=""]')
        for i in doc('ul[data-target=area]')('a').items():
            tmp = i.text()
            if tmp != '不限':
                res.append({'area': i.text(),  # 区域中文名
                            'url': self.city_url + i.attr('href')})  # 区域url
        return res

    def get_area_lv2(self, area_html, area_lv2) -> str:
        """
        获取某个区域的二级区域的url

        :param area_html:
        :param area_lv2:
        :return:
        """
        d_area = self.area_level2_dict(area_html)
        url_area = None
        for i in d_area:
            if i['area'] == area_lv2:
                url_area = i['url']
                break
        assert url_area, f'{self.city_cn} 中未找到区域 {area_lv2}'
        return url_area

    def area_level2_list(self, area_html) -> List[dict]:
        """
        链家二级区域信息获取, 提取二级区域名和对应的url, 输出list

        参数:
            area_html: html字符或pq(PyQuery)类型均可

        """
        doc = make_standard_html(area_html)
        d = self.area_level2_dict(doc)
        res = []
        for i in d:
            area = i.get('area')
            if area:
                res.append(area)
        if not res:
            print(f'== Warning 该城市 {self.city_cn} 无可用区域 ==')
        return res

    def pagination(self, html) -> list:
        """ 获取分页完整url, 从第二页开始, 返回list """

        doc = make_standard_html(html)
        res = []
        for i in doc('div.content__article > ul[style=display\:hidden] > li > a').items():
            res.append(self.city_url + i.attr('href'))  # 第二页开始的分页

        return res

    def get_room_info_page(self, html_pg) -> List[dict]:
        """
        根据分页的页面获取房源信息, 只做信息爬取, 不做计算

        :param html_pg:
        :return: 链家id, 标题, 小区, 描述, 价格, 房源url, 图片url
        """
        doc = make_standard_html(html_pg)
        # 判断当页是否有符合条件的内容
        tag = doc('div.content__article')('span.content__title--hl').text()
        if tag == '0':
            print('= 该页没有房源 =')
            return list()
        room_info_list = doc('div.content__list--item')
        room_info_items = room_info_list.items()
        print(f'= 该页共{len(room_info_list)}个房源 =')
        res = list()
        for i in room_info_items:
            # 链家内部code
            lj_code = i.attr('data-house_code')
            # url
            url = self.city_url + i('a.content__list--item--aside').attr('href')
            # 图片url
            url_pic = i('img').attr('data-src')
            # 标题
            title = i('a.content__list--item--aside').attr('title')
            # 全部描述
            desc = i('p.content__list--item--des')
            # 小区
            xiaoqu = desc('a[title]').text()
            # 价格
            price = i('span.content__list--item-price').text()

            dict_info = {'链家id': lj_code, '标题': title, '小区': xiaoqu, '描述': desc.text(),
                         '价格': price, '房源url': url, '图片url': url_pic}
            res.append(dict_info)

        return res

    def get_room_info_single(self, html_room):
        """
        解析单房源html

        :param html_room:
        :return:
        """
        print(self.city_url)
        return True


class ZiRoomHtmlOps:
    """ 自如html相关操作 """

    def __init__(self, citycode=None):
        self.citycode = citycode if citycode else '001'
        self.city_url = get_lj_url(citycode)
        self.city_cn = get_city_info(citycode, 'city_cn')

    def city2area_dict(self, city_html) -> List[dict]:
        """
        自如html解析。解析city_doc, 提取可用的区级信息, 输出dict

        参数:
            city_html: 城市主页的html字符或pq(PyQuery)类型均可
            citycode: 项目城市编码
        """
        doc = make_standard_html(city_html)

        # 解析区域信息
        res = []
        for i in doc('div.opt-type')('span.opt-name:contains(区域)').parent()('div.wrapper a.item').items():
            res.append({'area': i.text(),  # 区域中文名
                        'url': 'https:' + i.attr('href')})  # 区域url
        return res

    def get_area_url(self, city_html, area: str):
        """
        获取城市某个区域的url

        :param city_html:
        :param area: 城市区域 中文
        :return:
        """
        d_area = self.city2area_dict(city_html)
        url_area = None
        for i in d_area:
            if i['area'] == area:
                url_area = i['url']
                break
        assert url_area, f'{self.city_cn} 中未找到区域 {area}'
        return url_area

    def city2area_list(self, city_html) -> list:
        """
        自如html解析。解析city_doc, 提取可用的区级信息, 输出dict

        参数:
            city_html: 城市主页的html字符或pq(PyQuery)类型均可
            citycode: 项目城市编码
        """
        doc = make_standard_html(city_html)
        d = self.city2area_dict(doc)
        res = []
        for i in d:
            area = i.get('area')
            if area:
                res.append(area)
        if not res:
            print(f'== Warning 该城市 {self.city_cn} 无可用区域 ==')
        return res

    def area_level2_dict(self, area_html) -> List[dict]:
        """
        自如二级区域信息获取, 提取二级区域名和对应的url, 输出dict

        参数:
            area_html: html字符或pq(PyQuery)类型均可

        """
        doc = make_standard_html(area_html)
        # 解析区域信息
        res = []
        for i in doc('span.checkbox-group')('a').items():
            res.append({'area': i.text(),  # 区域中文名
                        'url': 'https:' + i.attr('href')})  # 区域url
        return res

    def get_area_lv2(self, area_html, area_lv2) -> str:
        """
        获取某个区域的二级区域的url

        :param area_html:
        :param area_lv2:
        :return:
        """
        d_area = self.area_level2_dict(area_html)
        url_area = None
        for i in d_area:
            if i['area'] == area_lv2:
                url_area = i['url']
                break
        assert url_area, f'{self.city_cn} 中未找到区域 {area_lv2}'
        return url_area

    def area_level2_list(self, area_html) -> List[dict]:
        """
        自如二级区域信息获取, 提取二级区域名和对应的url, 输出list

        参数:
            area_html: html字符或pq(PyQuery)类型均可

        """
        doc = make_standard_html(area_html)
        d = self.area_level2_dict(doc)
        res = []
        for i in d:
            area = i.get('area')
            if area:
                res.append(area)
        if not res:
            print(f'== Warning 该城市 {self.city_cn} 无可用区域 ==')
        return res

    def pagination(self, html) -> list:
        """ 获取分页完整url, 从第二页开始, 返回list """

        doc = make_standard_html(html)
        page_num_text = doc('div.Z_pages span:contains(共)').text()
        if not page_num_text:
            return list()
        page_num = int(re.findall('共(\d+)页', page_num_text)[0])
        url_page1 = 'https:' + doc('div.Z_pages a.active').attr('href')
        tmp = re.match('(.*p)\d(.*)', url_page1)
        res = list()
        for i in range(1, page_num):
            res.append(tmp.group(1) + str(i) + tmp.group(2))
        return res

    def get_room_info_page(self, html_pg) -> List[dict]:
        """
        根据分页的页面获取房源信息, 只做信息爬取, 不做计算

        :param html_pg:
        :return: 标题, 小区, 描述, 价格, 房源url, 图片url, 位置信息, 价格信息
        """
        doc = make_standard_html(html_pg)
        room_info = doc('div.item').items()
        res = list()
        for i in room_info:
            title = i('div.info-box a').text()  # 名称
            url = 'https:' + i('div.info-box a').attr('href')  # url
            url_pic = i('div.pic-box')('img').attr('data-original')
            desc = i('div.desc div:nth-of-type(1)').text()  # 描述
            locations = i('div.desc>div.location').text()  # 位置描述
            # 价格信息
            price_info = '||'.join([num.attr('style') for num in i('div.price span.num').items()])  # ||分割改list为str
            # 其他标签
            tags = '||'.join([tag.text() for tag in i('div.tag span').items()])  # ||分割改list为str

            dict_info = {'标题': title, '描述': desc, '房源url': url, '图片url': url_pic,
                         '位置信息': locations, '价格信息': price_info, '其他标签': tags}
            res.append(dict_info)

        return res

    def get_room_info_single(self, html_room):
        """
        解析单房源html

        :param html_room:
        :return:
        """
        print(self.city_url)
        return True


class AnalysisOps:
    """
    统一两平台信息内容，生成标准输出字典

    规则如下：
        房源url | 来源 | 小区 | 租金 | 类型 | 面积 | 房型 | 居室数 | 朝向 | 楼层描述 | 楼层数 | 原始标题 | 图片url | 图片*
        xxx | 链家 | xx小区 | 3500 | 整租 | 54 | 2室1厅 | 2 | 南 | 高楼层 （9层） | 6 | xxx | xxx | *
        图片格式待定
    """

    @staticmethod
    def analyse_lianjia_info_item(room_info: dict, get_picture=False) -> dict:
        """
        解析链家信息的单条记录

        :param room_info: 链家信息的单条记录
        :param get_picture: 是否获取图片数据
        :return:
        """
        res = dict()
        title_str = room_info.get('标题')
        res['原始标题'] = title_str
        # 租房类型 整租 合租
        rent_type_str = re.compile('(.租)·').findall(title_str)
        if rent_type_str:
            res['类型'] = rent_type_str[0]
        res['房源url'] = room_info.get('房源url')
        res['来源'] = '链家'
        res['小区'] = room_info.get('小区')
        price = re.compile('\d+(?= +元/月)').findall(room_info.get('价格'))
        if price:  # 取出的是list
            res['租金'] = int(price[0])
        desc = room_info['描述']
        res['原始描述'] = desc
        # 正则捕获面积，房型
        area = re.compile('(\d+\.*\d+)㎡').findall(desc)
        if area:
            res['面积'] = float(area[0])
        room = re.compile('(\d室\d厅)').findall(desc)
        if room:
            res['房型'] = room[0]
        # 居室数
        room_num_str = re.compile('(\d)室').findall(desc)
        res['居室数'] = int(room_num_str[0])
        # 楼层
        desc_split = desc.split('/')
        if desc_split and len(desc_split) > 4:
            res['楼层描述'] = desc_split[-1]
            res['楼层'] = int(re.findall('(\d)层', desc_split[-1])[0])
        # 朝向
        desc_split = desc.split('/')
        if desc_split and len(desc_split) > 4:
            res['朝向'] = desc_split[-3]

        # 图片
        res['图片url'] = room_info.get('图片url')
        if get_picture:
            pass

        return res

    @staticmethod
    def analyse_ziroom_info_item(room_info: dict, get_price=False, get_picture=False) -> dict:
        """
        解析自如信息的单条记录

        :param room_info: 自如信息的单条记录
        :param get_price: 是否计算价格
        :param get_picture: 是否获取图片数据
        :return:
        """
        res = dict()
        res['房源url'] = room_info.get('房源url')
        res['来源'] = '自如'
        # 小区，类型
        title_str = room_info.get('标题')
        res['原始标题'] = title_str
        rent_type_str = re.compile('(.租)·').findall(title_str)
        if rent_type_str:
            res['类型'] = rent_type_str[0]
        xiaoqu = re.compile('·(.*)\d居室').findall(title_str)
        if xiaoqu:
            res['小区'] = xiaoqu[0]
        # 面积，楼层
        desc_str = room_info.get('描述')
        res['原始描述'] = desc_str
        area = re.compile('(\d+\.*\d+)㎡').findall(desc_str)
        if area:
            res['面积'] = float(area[0])
        floor_desc = re.compile('\d/\d层').findall(desc_str)
        if floor_desc:
            res['楼层描述'] = floor_desc[0]
        floor = re.compile('(\d)/\d层').findall(desc_str)
        if floor:
            res['楼层'] = int(floor[0])
        # 房型，居室数
        room_num_desc = re.compile('\d居室').findall(title_str)
        if room_num_desc:
            res['房型'] = room_num_desc[0]
        room_num = re.compile('(\d)居室').findall(title_str)
        if room_num:
            res['居室数'] = room_num[0]
        # 朝向
        res['朝向'] = title_str.split('-')[-1]

        # 图片
        res['图片url'] = room_info.get('图片url')
        if get_picture:
            pass
        # 价格
        res['价格信息'] = room_info.get('价格信息')
        res['位置信息'] = room_info.get('位置信息')
        res['其他标签'] = room_info.get('其他标签')
        if get_price:
            pass
        return res






# class InformationOps:
#     """
#     提取的information操作和转换
#     """
#
#     @staticmethod
#     def analyse_lj_page(lj_page_info: dict):
#         """
#         将链家page页爬取的单条房源信息进行处理
#
#         :param lj_page_info:
#         :return:
#         """
