import cv2
import numpy as np
from tools import *

def locate_picture1(src, limit_color, limit_number, limit, up_limit, down_limit):
    src = cv2.resize(src, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    start_x = int(src.shape[0] * 0.1)
    end_x = int(src.shape[0] * 0.5)
    start_y = int(src.shape[0] * 0.1)
    end_y = int(src.shape[1] * 0.5)
    dst = src[start_x:end_x, start_y:end_y]

    process_image = cv2.adaptiveThreshold(dst, limit_color, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    color_number = get_pixel_matrix(process_image, 1) / limit_color
    '''
    no error
    print(color_number[0:100])
    # 按行统计图片的像素信息
    color_number = [0 for k in range(0, process_image.shape[0])]
    for i in range(0, process_image.shape[0]):
        for j in range(0, process_image.shape[1]):
            value = process_image[i][j]
            if value == limit_color:
                color_number[i] = color_number[i] + 1
    print(color_number)

    '''

    for l in range(0, process_image.shape[0]):
        if color_number[l] <= limit_number:
            color_number[l] = 0

    char_index = 0
    blank_index = 0
    max_width = 0
    count = 0
    record = 0
    split_list = []
    in_char = False
    for k in range(0, dst.shape[0]):
        if (in_char is False) and (color_number[k] != 0):
            in_char = True
            char_index = k
        elif (color_number[k] == 0) and (in_char is True):
            blank_index = k
            if color_number[blank_index + limit] == 0:
                in_char = False
                width = blank_index - char_index
                count = count + 1
                if width > max_width:
                    record = count
                    max_width = width
                temp_list = [char_index - up_limit, blank_index + down_limit]
                split_list.append(temp_list)

    start_location = split_list[record + 1][0]
    end_location = split_list[record + 1][1]
    number_image = process_image[start_location:end_location, 0:process_image.shape[1]]
    start_location = split_list[record + 2][0]
    end_location = split_list[record + 2][1]
    name_image = process_image[start_location:end_location, 0:process_image.shape[1]]
    return number_image, name_image




#函数功能：将文本进行水平方向分割
#src:原始图片
#limit_color:颜色的阈值
#limit_number:数量的阈值
#store:是否存储
#show:是否显示
#scope:量化范围
#horizontal_id:生成图片编号
def horizontal_split_chinese3(src, store, show, horizontal_id):
    limit_color = 250
    limit_number = 10
    scope = 4
    #腐蚀图像
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    erode_image = cv2.erode(src, element)
   # show_img(erode_image)
    color_number = get_pixel_matrix(erode_image, 0) / limit_color
    '''
    #print(color_number[0:150])

    #按行统计图片的像素信息
    color_number = [0 for k in range(0, erode_image.shape[1])]
    for i in range(0, erode_image.shape[0]):
        for j in range(0, erode_image.shape[1]):
            value = erode_image[i][j]
            if value == limit_color:
                color_number[j] = color_number[j] + 1
    #print(color_number)
    '''

    for l in range(0, src.shape[0]):
        if color_number[l] <= limit_number:
            color_number[l] = 0

    for l in range(0, src.shape[1] - scope):
        next_total = 0
        for r in range(0, scope):
            next_total = next_total + color_number[l + r]
        if next_total != 0:
            color_number[l] = 5

    column_list = []                     #用于储存分割出来的每个字符
    char_index = 0                       #记录进入字符区的索引
    blank_index = 0                      #记录进入空白区域的索引
    in_char = False                      #是否遍历到了字符区内
    record_char = True                   #是否可以记录字符
    standard_width = int(src.shape[0] * 0.75)      #字符宽度限制
    min_width = int(src.shape[0] * 0.2)           #字符最小宽度限制
    middle_width = int(src.shape[0] * 0.5)
    max_width = src.shape[0]

    #进行数字与字母的分割
    for i in range(0, erode_image.shape[1]):

        #进入字符区
        if (in_char is False) and (color_number[i] != 0):
            in_char = True
            char_index = i

        #进入空白区
        elif (color_number[i] == 0) and (in_char is True):
            blank_index = i
            in_char = False
            width = blank_index - char_index
            if width > min_width:
                if width > max_width:
                    while width > max_width:
                        column_image = src[0: src.shape[0], char_index: char_index + standard_width]
                        column_list.append(column_image)
                        char_index = char_index + standard_width
                        width = blank_index - char_index
                    column_image = src[0: src.shape[0], char_index: blank_index]
                    column_list.append(column_image)
                else:
                    column_image = src[0: src.shape[0], char_index: blank_index]
                    column_list.append(column_image)

    for i in range(0, len(column_list)):

        # 展示水平分割的效果
        if show is True:
            window_name = "Horizontal Split Char Window %d" % i
            show_img(column_list[i], window_name)
        # 存储图片
        if store is True:
            horizontal_id = horizontal_id + 1
            store_img(column_list[i], horizontal_id)

    return column_list, horizontal_id


#函数功能：将文本进行水平方向分割
#src:原始图片
#limit_color:颜色的阈值
#limit_number:数量的阈值
#store:是否存储
#show:是否显示
#horizontal_id:生成图片编号
def horizontal_split_char3(src, store, show, horizontal_id):
    limit_color = 250
    limit_number = 15
    #腐蚀图像
    #element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    #erode_image = cv2.erode(src, element)
    color_number = get_pixel_matrix(src, 0) / limit_color
    '''
    print(color_number[0:400])

    #按行统计图片的像素信息
    color_number = [0 for k in range(0, src.shape[1])]
    for i in range(0, src.shape[0]):
        for j in range(0, src.shape[1]):
            value = src[i][j]
            if value == limit_color:
                color_number[j] = color_number[j] + 1
    print(color_number)
    '''

    for l in range(0, src.shape[0]):
        if color_number[l] <= limit_number:
            color_number[l] = 0

    column_list = []  # 用于储存分割出来的每个字符
    char_index = 0  # 记录进入字符区的索引
    blank_index = 0  # 记录进入空白区域的索引
    restart_location = 0  # 重启位置索引
    in_char = False  # 是否遍历到了字符区内
    start_flag = False  # 是否开始分割
    first_flag = True
    limit_width = src.shape[0] * 0.2           # 字符宽度限制
    start_location = int(src.shape[1] * 0.45)   # 记录的起始位置
    standard_width = int(src.shape[0] * 0.44)  # 标准的字符宽度
    min_width = int(src.shape[0] * 0.2)        #最小宽度
    max_width = int(src.shape[0] * 0.8)

    # 进行数字与字母的分割
    for index in range(start_location, src.shape[1]):
        # 进入字符区
        if (in_char is False) and (color_number[index] != 0):
            in_char = True
            char_index = index
        # 进入空白区
        elif (color_number[index] == 0) and (in_char is True):
            blank_index = index
            in_char = False
            width = blank_index - char_index
            if width > min_width:
                if width > max_width:
                    while width > max_width:
                        column_image = src[0: src.shape[0], char_index: char_index + standard_width]
                        column_list.append(column_image)
                        char_index = char_index + standard_width
                        width = blank_index - char_index
                    column_image = src[0: src.shape[0], char_index: blank_index]
                    column_list.append(column_image)
                else:
                    column_image = src[0: src.shape[0], char_index: blank_index]
                    column_list.append(column_image)

    for i in range(0, len(column_list)):

        # 展示水平分割的效果
        if show is True:
            window_name = "Horizontal Split Char Window %d" % i
            show_img(column_list[i], window_name)

        # 存储图片
        if store is True:
            horizontal_id = horizontal_id + 1
            store_img(column_list[i], horizontal_id)

    return column_list, horizontal_id