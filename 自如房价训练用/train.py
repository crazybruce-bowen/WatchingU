# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:49:54 2023

@author: 47176
"""

#%% Env

import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
from os.path import dirname
from tensorflow.keras import models
import numpy as np
from matplotlib import pyplot as plt

#%% Data
train_path = r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\训练图片\train_data'


from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale=1/255)

train_generator = train_datagen.flow_from_directory(
    train_path, 
    color_mode='grayscale',
    target_size = (30, 30),  # resize all image
    batch_size = 1,
    class_mode='categorical'
    )

#%% 模型定义
model = keras.models.Sequential([
    keras.layers.Conv2D(4, (2, 2), activation='relu', input_shape=(30, 30, 1), padding='same'),
    keras.layers.MaxPooling2D(2, 2),
    keras.layers.Flatten(),
    keras.layers.Dense(10, activation='softmax'),
    ])

model.summary()
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#%% 训练
model.fit(train_generator, epochs=10)


#%% 输出
model.save(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\pre_trained.h5')

#%% 模型导入

model2 = keras.models.load_model(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\pre_trained.h5')

#%% 预测
from tensorflow.keras.utils import load_img, img_to_array

im_pre = load_img(r'D:\Learn\学习入口\大项目\爬他妈的\住房问题\整合\自如房价训练用\训练图片\train_data\8\b-8.png',
                  target_size=(30, 30), color_mode='grayscale')

x = img_to_array(im_pre)
x = np.expand_dims(x, axis=0)

images = np.vstack([x])

t = model.predict(images)


