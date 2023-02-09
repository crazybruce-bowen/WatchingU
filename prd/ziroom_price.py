# 开发自如价格生成功能
import re
from typing import List
import requests
from io import BytesIO
from PIL import Image
import copy

"""
TODO list
从小到大
Tools:
1. 输入图像url, 返回图像类  *禁止每张图都调用接口，太慢
2. 输入图像(图像类), 像素位置, 返回解析数字

Usage:
1. 输入单个数字的字符, 解析字符, 得到图像url和像素位置  |  Done
2. 房源内多个数字拆解成单个数字  |  Done
3. 解析单个数字信息

"""


def convert_one_number(s: str) -> tuple or False:
    """
    输入单个数字待解析字符, 返回url和像素位置
    
    case:
        'background-image: url(//static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png);background-position: -21.4px'
    :return:
        url 图片url https://static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png
        pos 像素位置
    """
    url_re = re.findall('url\((.*)\)', s)
    if not url_re:
        return False
    url = 'https:' + url_re[0]
    pos_re = re.findall('background-position: *(.*px)', s)
    if not pos_re:
        return False
    pos = pos_re[0]
    return url, pos


def convert_numbers(s: str) -> list or False:
    """
    将多个数字的拼接字符转换为多个数字的url和像素位置

    :param s:
    :return:
    """
    s_list = s.split('||')
    if not s_list:
        return False
    res = []
    for i in s_list:
        url, pos = convert_one_number(i)
        res.append({'url': url, 'pos': pos})
    return res


class ZiRoomPicOps:

    def __init__(self):
        self.pic_info = []
        self.info_list = ['url', 'im_size', 'im']

    @property
    def url_list(self):
        """
        设置url为主键, 该方法为判断主键是否存在用

        :return:
        """
        res = []
        if not self.pic_info:
            return res
        for i in self.pic_info:
            res.append(i.get('url'))

    def get_info(self, url: str, info: str):
        """
        根据url返回对应的属性

        :param url:
        :param info:
        :return:
        """
        if info not in self.info_list:
            print(f'-- 该info属性 {info} 不在可选范围中 --')
            print(f'-- 可选属性为 {self.info_list} --')
            return False
        for i in self.pic_info:
            if i.get('url') == url:
                return i.get(info)

        print('-- 该url并未爬取 --')
        return False

    def get_background_pic_size(self, p_info: List[dict]) -> List[tuple] or False:
        """
        传入某房源的多个数字url和像素位置列表字典信息, 返回背景图片size

        :param p_info: 拼接后的price_info
        :return:
            [(300, 30), (300, 30), (300, 30), (300, 30)]
        """
        im_size_list = []

        for i in p_info:
            url = i.get('url')
            if url not in self.url_list:  # 未提取的开始提取
                response = requests.get(url)
                im = Image.open(BytesIO(response.content))
                im_size_list.append(im.size)
                self.pic_info.append({'url': url, 'im_size': im.size, 'im': im})
            else:
                im_size = self.get_info(url, 'im_size')
                im_size_list.append(im_size)

        return im_size_list

    def get_pix_num(self, p_info: List[dict]):
        """
        传入某房源的多个数字url和像素位置列表字典信息, 返回pix数值

        :param p_info:
        :return:
        """
        pix_list = []
        for i in p_info:
            pos_str = i.get('pos')
            pix = float(re.findall('(\d+\.*\d*)px', pos_str)[0])
            pix_list.append(pix)
        return pix_list

    def get_num_position(self, p_info: List[dict], size_show=(13, 20)) -> List[int]:
        """
        传入某房源的多个数字url和像素位置列表字典信息, 返回数字位置

        :param p_info:
        :param size_show: 自如搜索页显示的数字size, 可在浏览器中用"检查"方法查看
        :return:
            pos_list: [2, 5, 1, 9]
        """
        im_size_list = self.get_background_pic_size(p_info)
        pix_list = self.get_pix_num(p_info)
        pos_list = []
        assert len(im_size_list) == len(pix_list), 'im_size_list和pix_list长度不符, 检查代码'
        for i in range(len(im_size_list)):
            rate = size_show[1] / im_size_list[i][1]
            width = im_size_list[i][0] * rate / 10
            pos = pix_list[i] / width
            pos_list.append(pos)
        return pos_list








