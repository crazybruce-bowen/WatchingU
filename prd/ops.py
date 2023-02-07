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
        :return: 链家id, 标题, 小区, 描述, 价格, 房源url, 图片地址url
        """
        doc = make_standard_html(html_pg)
        room_info_items = doc('div.content__list--item').items()
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
                         '价格': price, '房源url': url, '图片地址': url_pic}
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




