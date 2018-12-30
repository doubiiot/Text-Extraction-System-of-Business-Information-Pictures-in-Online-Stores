# -*- coding: UTF-8 -*-
import cv2
import numpy as np

from tools import *



#函数功能：将文本进行垂直分割
#src:原始图片
#limit:二值化的阈值
#number:分割的数目
#store:是否存储
#show:是否展示
#vertical_id:生成图片编号
def vertical_split(src, store, show, vertical_id):
    #按行统计图片的像素信息
    limit = 250
    number = -1
    color_number = get_pixel_matrix(src, 1) / limit
    '''
    color_number = [0 for k in range(0, src.shape[0])]
    for i in range(0, src.shape[0]):
        for j in range(0, src.shape[1]):
            value = src[i][j]
            if value == limit:
                color_number[i] = color_number[i] + 1
    '''


    row_list = []     #用于储存分割出来的每个字符
    char_index = 0    #记录进入字符区的索引
    blank_index = 0   #记录进入空白区域的索引
    char_number = 0   #记录字符的行数
    in_char = False   #是否遍历到了字符区内

    #设置最大分割数目
    if number == -1:
        number = 2048

    for i in range(0, src.shape[0]):
        #进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            char_index = i
        #进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            row_image = src[char_index: blank_index + 1, 0: src.shape[1]]
            row_list.append(row_image)
            char_number = char_number + 1
            if char_number >= number:
                break

    for i in range(0, len(row_list)):

        # 展示垂直分割的效果
        if show is True:
            window_name = "Vertical Split Window %d" % i
            show_img(row_list[i],window_name)

        # 存储图片
        if store is True:
            vertical_id = vertical_id + 1
            store_img(row_list[i],vertical_id)

    return row_list, vertical_id

#judge line is number or name
#return 1:number
#return 0:name
#return -1:wrong
def locate_line(text):
    bussiness_number1 = "注册号"
    bussiness_number2 = "册号"
    bussiness_number3 = "号"

    bussiness_name1 = "名称"
    bussiness_name2 = "名"
    bussiness_name3 = "称"

    if text.find(bussiness_number1) != -1:
        return 1
    elif text.find(bussiness_number2) != -1:
        return 1
    elif text.find(bussiness_number3) != -1:
        return 1
    elif text.find(bussiness_name1) != -1:
        return 0
    elif text.find(bussiness_name2) != -1:
        return 0
    elif text.find(bussiness_name3) != -1:
        return 0
    else:
        return -1

#函数功能：将文本根据符号进行水平方向分割
def sign_split(src):
    color_number = get_pixel_matrix(src, 0) / 250
    column_list = []  # 用于储存分割出来的每个字符
    char_index = 0  # 记录进入字符区的索引
    blank_index = 0  # 记录进入空白区域的索引
    in_char = False  # 是否遍历到了字符区内
    standard_width = int(src.shape[0]*1.1)
    number = 0
    for i in range(0, src.shape[1]):
        # 进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            char_index = i
        # 进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            width = blank_index - char_index
            if width < standard_width:
                column_image = src[0: src.shape[0], char_index - 1: blank_index + 1]
                column_list.append(column_image)
                number = number + 1
                if number == 6:
                    break
            else:
                column_image = src[0: src.shape[0], char_index - 1: int(char_index + width/2)]
                column_list.append(column_image)
                number = number + 1
                if number == 6:
                    break
                column_image = src[0: src.shape[0], int(char_index + width/2): blank_index + 1]
                column_list.append(column_image)
                number = number + 1
                if number == 6:
                    break
    return column_list

#函数功能：将文本进行水平方向分割
#src:原始图片
#limit:颜色的阈值
#store:是否存储
#show:是否显示
#horizontal_id:生成图片编号
def horizontal_split_char(src, store, show, horizontal_id):
    limit = -1
    # 设置颜色限制
    # if limit == -1:
    #     limit = 5

    # 腐蚀图像
    # element = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # erode_image = cv2.erode(src, element)


    #color_number = np.sum(erode_image,axis=0) / 250
    color_number = get_pixel_matrix(src, 0) / 250
    column_list = []  # 用于储存分割出来的每个字符
    char_index = 0  # 记录进入字符区的索引
    blank_index = 0  # 记录进入空白区域的索引
    in_char = False  # 是否遍历到了字符区内
    start_flag = False  # 是否开始分割
    limit_width = src.shape[0] * 0.2  # 字符宽度限制
    start_location = src.shape[0] * 4  # 记录的起始位置
    standard_width = int(src.shape[0])
    current_width = 0
    # 进行数字与字母的分割
    for i in range(start_location, src.shape[1]):
        # 进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            char_index = i
        # 进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            width = blank_index - char_index
            if start_flag is True:
                if width < standard_width:
                    column_image = src[0: src.shape[0], char_index - 1: blank_index + 1]
                    column_list.append(column_image)
                else:
                    column_image = src[0: src.shape[0], char_index - 1: int(char_index + width/2)]
                    column_list.append(column_image)
                    column_image = src[0: src.shape[0], int(char_index + width/2): blank_index + 1]
                    column_list.append(column_image)
            if width < limit_width:
                start_flag = True

    for i in range(0, len(column_list)):
        # 展示水平分割的效果
        if show is True:
            window_name = "Horizontal Split Char Window %d" % i
            show_img(column_list[i],window_name)

        # 存储图片
        if store is True:
            horizontal_id = horizontal_id + 1
            store_img(column_list[i], horizontal_id)

    return column_list, horizontal_id


#函数功能：将文本进行水平方向分割(升级版)
#src:原始图片
#limit:颜色的阈值
#store:是否存储
#show:是否显示
#horizontal_id:生成图片编号
def horizontal_split_chinese(src, store, show, horizontal_id):
    limit = 5
    k_left = 0
    k_right = 2
    #设置颜色限制
    if limit == -1:
        limit = 20
    #腐蚀图像
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    erode_image = cv2.erode(src, element)
    margin = 0
    #color_number = np.sum(erode_image,axis=0) / 250
    color_number = get_pixel_matrix(src, 0) / 250
    column_list = []                     #用于储存分割出来的每个字符
    char_index = 0                       #记录进入字符区的索引
    blank_index = 0                      #记录进入空白区的索引
    low_value = src.shape[0] * 0.6       #宽度的下限
    high_value = src.shape[0] * 1.7      #宽度的上限
    bracket_limit = src.shape[0] * 1.1   #括号宽度限制
    bracket_start = 0                    #括号的开始
    bracket_end = 0                      #括号的结束
    min_width = src.shape[0] * 0.2       #字符宽度限制
    start_location = int(src.shape[0] * 4.5)    #记录的起始位置
    standard_width = src.shape[0]        #标准字宽
    in_char = False                      #是否遍历到了字符区内
    start_flag = True                   #是否开始分割
    record_char = True                   #是否可以记录字符起始位置
    bracket_flag = False                 #是否可以记录括号的结束
    min_value = src.shape[0] * 0.3
    temp = 0

    for k in range(start_location, erode_image.shape[1]):
        if (in_char is False) and (color_number[k] != 0):
            in_char = True
            if record_char is True:
                char_index = k
        elif (color_number[k] == 0) and (in_char is True):
            blank_index = k
            in_char = False
            width = blank_index - char_index
            if start_flag is True:
                if width <= low_value:
                    record_char = False
                else:
                    record_char = True
                    if width >= high_value:

                        temp_width = width
                        while temp_width >= high_value:
                            column_split_image = src[0: src.shape[0], char_index - k_left: char_index + standard_width + k_right + margin]
                            column_list.append(column_split_image)
                            char_index = char_index + standard_width
                            temp_width = blank_index - char_index

                        temp = blank_index - char_index
                        if temp > min_value:
                            column_last_image = src[0: src.shape[0], char_index - k_left: blank_index + k_right + margin]
                            column_list.append(column_last_image)
                    else:
                        result_width = blank_index - char_index
                        if result_width >= bracket_limit:
                            bracket_flag = False
                            for r in range(char_index, blank_index):
                                if (bracket_flag is True) and (color_number[r] != 0):
                                    bracket_end = r
                                    break
                                if color_number[r] == 0:
                                    bracket_start = r
                                    bracket_flag = True
                            bracket_image = src[0: src.shape[0], char_index - k_left: bracket_start + k_right+margin]
                            column_list.append(bracket_image)
                            temp = blank_index - char_index
                            if temp > min_value:
                                chinese_image = src[0: src.shape[0], bracket_end - k_left: blank_index + k_right+margin]
                                column_list.append(chinese_image)
                        else:
                            temp = blank_index - char_index
                            if temp > min_value:
                                column_image = src[0: src.shape[0], char_index - k_left: blank_index + k_right + margin]
                                column_list.append(column_image)
            else:
                if width <= min_width:
                    start_flag = True

    for l in range(0, len(column_list)):

        # 展示水平分割的效果
        if show is True:
            window_name = "Horizontal Split Chinese Window %d" % l
            show_img(column_list[l],window_name)
        # 存储图片
        if store is True:
            horizontal_id = horizontal_id + 1
            store_img(column_list[l], horizontal_id)
    return column_list, horizontal_id

