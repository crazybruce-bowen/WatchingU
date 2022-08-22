from sklearn.cluster import KMeans
from skimage import morphology
import pickle
from PIL import Image
import numpy as np


class PricePredict:
    def __init__(self, image, model):
        """

        :param image: IO class or file path 直接抓取的图像
        :param model: 训练好的预测模型类
        """
        self.image = image
        self.model = model

    def predict(self, n):
        """

        :param model:
        :param n: 第n个数字
        :return:
        """
        image = self.get_img_idx(n)
        image = image.getchannel(3)
        image = thin(image)
        v_image = image.reshape((1, -1))
        res = self.model.predict(v_image)[0]
        return res

    def get_img_idx(self, n):
        """ 获取类图片的第n个数字，从0开始 """
        image_width = int(self.image.size[0] / 10)
        im = self.image.crop((image_width * n, 0, image_width * (n+1), self.image.size[1]))
        return im


def thresholding(image):
    predicted = KMeans(n_clusters=2, random_state=9).fit_predict(
        image.reshape((image.shape[0]*image.shape[1], 1)))
    image = predicted.reshape((image.shape[0], image.shape[1]))
    return image


def thin(image):
    image = thresholding(np.array(image))
    thin_image = morphology.skeletonize(image)
    return thin_image


#%%
if __name__ == '__main__':
    # model_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\自如\data\LR_0817.pickle'
    # with open(model_path, 'rb') as fr:
    #     model = pickle.load(fr)
    #
    # img = Image.open(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\自如\data\测试价格图片.png')
    # b = img.crop((60, 0, 90, 28))
    #
    # n = predict(model, b)
    # print(n)

    pass
