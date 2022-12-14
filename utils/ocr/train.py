#! /usr/bin/python3
# Attention path
from PIL import Image
import numpy as np
from sklearn.linear_model import LogisticRegression as LR
import pickle
import os
import copy
import pandas as pd


path = r'D:\学习总文件夹\整体项目\爬虫\住房问题\整体\code\utils\orc\training_data'
os.chdir(path)

model_path = 'LR_0906.pickle'


def my_threshold(image):
    """
    将灰度图像转换为二元图像，即1-0

    :param image: PIL Image对象
    :return: PIL Image对象
    """
    im0 = copy.deepcopy(image)
    im0_num = pd.DataFrame(np.array(im0))
    im0_num[im0_num > 130] = 255
    im0_num[im0_num <= 130] = 0
    res = Image.fromarray(np.array(im0_num))
    return res


def train():
    model = LR()
    images = []
    for i in range(10):
        image_path = os.path.join(path, '%d.jpg' % i)
        image = Image.open(image_path)
        image = my_threshold(image)
        images.append(np.array(image))
    images = np.array(images)
    images = images.reshape((10, -1))
    print(images.shape)
    X = images
    # Y = np.reshape(np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]), (10, 1))
    Y = np.array(range(10))
    model.fit(X, Y)
    print(model.score(X, Y))
    # save model
    with open(model_path, 'wb') as fw:
        pickle.dump(model, fw)


if __name__ == '__main__':
    train()


#%% test
# a = Image.open(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\自如\data\training_data\9.jpg')
# b = Image.open(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\自如\data\training_data\20220818\9.jpg')

# a1 = np.array(a)
# b1 = np.array(b)

# p_a = KMeans(n_clusters=2, random_state=9).fit_predict(
#     a1.reshape((a1.shape[0]*a1.shape[1], 1)))

# p_b = KMeans(n_clusters=2, random_state=9).fit_predict(
#     b1.reshape((b1.shape[0]*b1.shape[1], 1)))

# p_t = KMeans(n_clusters=2, random_state=9).fit_predict(
#     t1.reshape((t1.shape[0]*t1.shape[1], 1)))

# #%%
# a2 = np.array(a.convert('L'))
# b2 = np.array(b.convert('L'))

# a1 = thin(a).reshape((1, -1))
# b1 = thin(b).reshape((1, -1))

# print(model.predict(b1))
