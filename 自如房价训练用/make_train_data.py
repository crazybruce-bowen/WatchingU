# 自如图像识别训练
"""
TODO list:

"""

#%% Env
from PIL import Image
import os


# 样例图片
path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\训练图片\train_data'
# 49835716020
pic1 = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\训练图片\样例1.png'
# 8652039147
pic2 = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\训练图片\样例2.png'
# 9635804271
pic3 = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\训练图片\样例3.png'

pic_list = [pic1, pic2, pic3]
num_list = ['49835716020', '8652039147', '9635804271']
tag_list = ['a', 'b', 'c']
#%% 设置

# 读取, 置灰并拆分图片
def split_pic(pic_path):
    im = Image.open(pic_path).getchannel(3)
    width = im.size[0] / 10
    res = []
    for i in range(10):
        box = (i * width, 0, (i + 1) * width,im.size[1])
        res.append(im.crop(box))
    return res

def save_pic_list(pic_list, name='x'):
    n = 0
    for i in pic_list:
        n += 1
        i.save(os.path.join(path, f'{name}-{n}.png'))
    return True

def main(pic_path, num_str='1234567890', name='x'):
    im = Image.open(pic_path).getchannel(3)
    width = im.size[0] / 10
    res = []
    for i in range(10):
        box = (i * width, 0, (i + 1) * width,im.size[1])
        im_crop = im.crop(box)
        dir_path = os.path.join(path, num_str[i])
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        im_crop.save(os.path.join(dir_path, f'{name}-{num_str[i]}.png'))
        res.append(im_crop)
    return res
        
#%% 执行
for i in range(3):
    main(pic_list[i], num_list[i], tag_list[i])
#%%
