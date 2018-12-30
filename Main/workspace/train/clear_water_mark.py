# -*- coding: utf-8 -*-
import cv2
import numpy as np


def clear_water_mark_alpha(src, value, show):

    #图片不存在
    if not src.data:
        print("Picture is not exist!\n")
        return -1

    #图片通道数不为4，无法采用此方式进行水印处理
    if src.shape[2] != 4:
        print("This picture's alpha channel is not exist, please try another way to clear watermark.\n")
        return -2

    #变量定义
    rgb_channels = []
    alpha_channel = []
    rgb_image = np.zeros((src.shape[0], src.shape[1], 3), dtype=src.dtype)
    alpha_image = np.zeros((src.shape[0], src.shape[1], 3), dtype=src.dtype)
    blank_image = np.zeros((src.shape[0], src.shape[1], 1), dtype=src.dtype)
    weight = 0.8

    #分离通道,合成rgb通道
    blue = cv2.split(src)[0]   # Blue通道
    green = cv2.split(src)[1]  # Green通道
    red = cv2.split(src)[2]    # Red通道
    alpha = cv2.split(src)[3]  # Alpha通道

    #合并红、绿、蓝三通道,形成rgb图片
    rgb_channels.append(blue)
    rgb_channels.append(green)
    rgb_channels.append(red)
    cv2.merge(rgb_channels, rgb_image)

    #合成alpha通道,形成alpha图片
    alpha_channel.append(blank_image)
    alpha_channel.append(blank_image)
    alpha_channel.append(alpha)
    cv2.merge(alpha_channel, alpha_image)

    #处理水印
    color_image = alpha_image * weight - rgb_image
    #图片二值化处理
    color_image = np.float32(color_image)
    dst = cv2.cvtColor(color_image, cv2.COLOR_RGB2GRAY)
    cv2.threshold(dst, 5, value, 0, dst)

    #显示水印处理效果
    if show:
        window_name = "Cleat the image's water mark by alpha channel Window"
        cv2.namedWindow(window_name)
        cv2.imshow(window_name, dst)
        cv2.waitKey(0)
        cv2.destroyWindow(window_name)

    return dst
