import cv2
import numpy as np
from tools import *
def locate_picture0(src, src_n):
    threshold_min = 5
    threshold_max = 250
    gray_image = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
    #gray_image = src
    #gray_image = src
    #show_img(gray_image)
    dst_image = cv2.resize(gray_image, (0, 0), fx=0.7, fy=0.7, interpolation=cv2.INTER_AREA)
    #src_n = cv2.resize(src_n, (0, 0), fx=0.7, fy=0.7)

    cv2.threshold(dst_image, threshold_min, threshold_max, 0, dst_image)
    dst_image = gray_image[int(gray_image.shape[0] * 0.1): int(gray_image.shape[0] * 0.5),
                 int(gray_image.shape[1] * 0.1): int(gray_image.shape[1] * 0.9)]

    src_n = src_n[int(gray_image.shape[0] * 0.1): int(gray_image.shape[0] * 0.5),
                 int(gray_image.shape[1] * 0.1): int(gray_image.shape[1] * 0.9)]
    color_number = [0 for k in range(0, dst_image.shape[0])]
    for i in range(0, dst_image.shape[0]):
        for j in range(0, dst_image.shape[1]):
            value = dst_image[i][j]
            if value <= 200:
                color_number[i] = color_number[i] + 1

    for l in range(0, dst_image.shape[0]):
        if color_number[l] <= 20:
            color_number[l] = 0

    row_list = []     #用于储存分割出来的每个字符
    row_list_n = []
    char_index = 0    #记录进入字符区的索引
    blank_index = 0   #记录进入空白区域的索引
    char_number = 0   #记录字符的行数
    in_char = False   #是否遍历到了字符区内
    max_width = 0    #最大宽度
    width = 0
    count = 0
    current = -1

    for i in range(0, dst_image.shape[0]):
        #进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            char_index = i
        #进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            width = blank_index - char_index
            row_image = dst_image[char_index: blank_index + 1, 0: dst_image.shape[1]]
            row_list.append(row_image)
            row_image_n = src_n[char_index: blank_index + 1, 0: dst_image.shape[1]]
            row_list_n.append(row_image_n)
            count = count + 1
            char_number = char_number + 1
            if width >= max_width:
                max_width = width
                current = count

    return row_list[current], row_list[current+2],row_list_n[current],row_list_n[current+2]

#函数功能：将文本进行水平方向分割
#src:原始图片
#limit_color:颜色的阈值
#limit_number:数量的阈值
#store:是否存储
#show:是否显示
#horizontal_id:生成图片编号
def horizontal_split_char2(src, src_n, store, show, horizontal_id):
    # 腐蚀图像
    limit_color = 200
    limit_number = 20
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    erode_image = cv2.erode(src, element)

    # 按行统计图片的像素信息
    color_number = [0 for k in range(0, erode_image.shape[1])]
    for i in range(0, erode_image.shape[0]):
        for j in range(0, erode_image.shape[1]):
            value = erode_image[i][j]
            if value <= limit_color:
                color_number[j] = color_number[j] + 1

    for l in range(0, src.shape[0]):
        if color_number[l] <= limit_number:
            color_number[l] = 0

    count = 0  # 记录分割的数目
    column_list = []  # 用于储存分割出来的每个字符
    column_list_n = []
    char_index = 0  # 记录进入字符区的索引
    blank_index = 0  # 记录进入空白区域的索引
    in_char = False  # 是否遍历到了字符区内
    record_char = True  # 是否可以记录字符
    limit_width = int(src.shape[0] * 0.9)  # 字符宽度限制
    min_width = int(src.shape[0] * 0.8)  # 字符最小宽度限制
    start_location = int(src.shape[1] / 2)  # 记录的起始位置

    #src = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
    #current_element = cv2.getStructuringElement(cv2.MORPH_RECT,(1, 1))
    src = 255 - src
    src_n = 255 - src_n
    #src = 255 - erode_image
    #cv2.morphologyEx(src, image, cv2.MORPH_BLACKHAT, current_element)
    # 进行数字与字母的分割
    for i in range(start_location, erode_image.shape[1]):

        # 进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            if record_char is True:
                char_index = i

        # 进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            width = blank_index - char_index
            if limit_width >= width:
                if min_width >= width:
                    column_image = src[0: src.shape[0], char_index: blank_index]
                    column_list.append(column_image)
                    column_image_n = src_n[0: src.shape[0], char_index: blank_index]
                    column_list_n.append(column_image_n)

                    count = count + 1
                else:
                    ####
                    middle = int((char_index + blank_index) / 2)
                    column_image = src[0: src.shape[0], char_index: middle]
                    column_list.append(column_image)
                    column_image_n = src_n[0: src.shape[0], char_index: middle]
                    column_list_n.append(column_image_n)
                    ####
                    count = count + 1
                    ####
                    column_image = src[0: src.shape[0], middle: blank_index]
                    column_list.append(column_image)
                    column_image_n = src_n[0: src.shape[0], middle: blank_index]
                    column_list_n.append(column_image_n)
                    ####
                    count = count + 1
                if count >= 20:
                    break
    for i in range(0, len(column_list)):

        # 展示水平分割的效果
        if show is True:
            window_name = "Horizontal Split Char Window %d" % i
            show_img(column_list_n[i], window_name)
        # 存储图片
        if store is True:
            horizontal_id = horizontal_id + 1
            store_img(column_list_n[i], horizontal_id)
    #column_list
    return column_list,column_list_n,horizontal_id


#函数功能：将文本进行水平方向分割
#src:原始图片
#limit_color:颜色的阈值
#limit_number:数量的阈值
#store:是否存储
#show:是否显示
#scope:量化范围
#horizontal_id:生成图片编号
def horizontal_split_chinese2(src,src_n, store, show, horizontal_id):
    # 腐蚀图像
    limit_color = 200
    limit_number = 0
    scope = 3
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    erode_image = cv2.erode(src, element)

    # 按行统计图片的像素信息
    color_number = [0 for k in range(0, erode_image.shape[1])]
    for i in range(0, erode_image.shape[0]):
        for j in range(0, erode_image.shape[1]):
            value = erode_image[i][j]
            if value <= limit_color:
                color_number[j] = color_number[j] + 1

    for l in range(0, src.shape[0]):
        if color_number[l] <= limit_number:
            color_number[l] = 0

    for l in range(0, src.shape[1] - scope):
        next_total = 0
        for r in range(0, scope):
            next_total = next_total + color_number[l + r]
        if next_total != 0:
            color_number[l] = 5

    column_list = []  # 用于储存分割出来的每个字符
    column_list_n = []
    char_index = 0  # 记录进入字符区的索引
    blank_index = 0  # 记录进入空白区域的索引
    in_char = False  # 是否遍历到了字符区内
    record_char = True  # 是否可以记录字符
    limit_width = int(src.shape[0] * 0.8)  # 字符宽度限制
    src = 255 - src
    src_n = 255 - src_n
    # 进行数字与字母的分割
    for i in range(0, erode_image.shape[1]):

        # 进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            if record_char is True:
                char_index = i

        # 进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            width = blank_index - char_index
            column_image = src[0: src.shape[0], char_index: blank_index]
            column_list.append(column_image)

            column_image_n = src_n[0: src.shape[0], char_index: blank_index]
            column_list_n.append(column_image_n)

    for i in range(0, len(column_list)):

        # 展示水平分割的效果
        if show is True:
            window_name = "Horizontal Split Char Window %d" % i
            show_img(column_list_n[i],window_name)
        # 存储图片
        if store is True:
            horizontal_id = horizontal_id + 1
            store_img(column_list_n[i], horizontal_id)

    return column_list,column_list_n,horizontal_id