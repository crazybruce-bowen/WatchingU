from prd.tmp import *

case = 'background-image: url(//static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png);background-position: -192.6px||background-image: url(//static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png);background-position: -107px||background-image: url(//static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png);background-position: -21.4px||background-image: url(//static8.ziroom.com/phoenix/pc/images/price/new-list/a8a37e8b760bc3538c37b93d60043cfc.png);background-position: -171.2px'

# 数字列表
t = convert_numbers(case)

#%%

# 单个数字
a = t[0]

#%%
from PIL import Image
import requests
from io import BytesIO


url = a['url']
response = requests.get(url)

im = Image.open()