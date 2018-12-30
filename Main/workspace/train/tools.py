import cv2
import numpy as np
import re
import os
import xlrd,xlwt
import random
from preprocess import *
def show_img(img,window_name="tmp"):
    cv2.namedWindow(window_name)
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)

def store_img(img,id,path = './out_pic/'):
    store_name = path + str(id) + ".jpg"
    cv2.imwrite(store_name, img)

def get_pixel_matrix(img,mark):
    #add column:
    if(mark == 1):
        mtx = np.sum(img, axis=1)
    #add row:
    elif(mark == 0):
        mtx = np.sum(img, axis=0)
    return mtx

def is_char_elements(char):
    #print("char is " + char)
    if char.isdigit() or (char >= 'A' and char <= 'Z') or (char == "一"):
        #print("is a line1 element")
        return True
    else:
        #print("not a line1 element")
        return False
def is_chi_elements(char):
    #print(char)
    if (not char.isdigit()):
        return True
    else:
        return False
def info_process(dic):
    str_mingcheng = "名称"
    str_yxgs = "有限公司"
    str_you = "有"
    str_xian = "限"
    str_gong = "公"
    str_si = "司"
    str_mao = "贸"
    str_hai = "海"
    for k,v in dic.items():
        count = 0
        tmp = 0
        if(v[1].find(str_mingcheng) != -1):
            dic[k][1] = v[1][2:]
        loc_you = v[1].find(str_you)
        loc_xian = v[1].find(str_xian)
        loc_gong = v[1].find(str_gong)
        loc_si = v[1].find(str_si)
        loc_mao = v[1].find(str_mao)
        loc_hai = v[1].find(str_hai)
        #print(loc_you,loc_xian,loc_gong,loc_si)
        if(loc_you != -1):
            dic[k][1] = v[1][0:loc_you] + str_yxgs
            count = 1
        if (loc_xian != -1 and count == 0):
            dic[k][1] = v[1][0:loc_xian - 1] + str_yxgs
            count = 1
        if (loc_gong != -1 and count == 0):
            dic[k][1] = v[1][0:loc_gong - 2] + str_yxgs
            count = 1
        if (loc_you != -1 and count == 0):
            dic[k][1] = v[1][0:loc_si - 3] + str_yxgs
            count = 1
        if(loc_mao != -1):
            if(v[1][loc_mao+1] != "易" and v[1][loc_mao-1] != "商"):
                dic[k][1] = v[1][0:loc_mao-1] + "商" + v[1][loc_mao:]
        if(loc_hai != -1):
            if (v[1][loc_hai + 1] == ")"):
                dic[k][1] = v[1][0:loc_hai-1] + "上" + v[1][loc_hai:]

        for j in v[0]:
            if( (not j.isdigit()) and (j != '一')):
                dic[k][0] = v[0][:tmp] + v[0][tmp + 1:]
                tmp = tmp - 1
            if(j == '一'):
                dic[k][0] = dic[k][0].replace("一", "-")
            tmp = tmp + 1
        dic[k][0] = complete_num(dic[k][0])
    return dic
def info_clear(dic):
    for k, v in dic.items():
        count = 0
        for j in v[1]:
            if((j >= 'a' and j <= 'z') or (j >= 'A' and j <= 'Z')):
                dic[k][1] = v[1][:count] + v[1][count+1:]
            count = count + 1
    return dic

def get_filelist(input_path):
    dic = {}
    file_name = []
    for i in os.listdir(input_path):
        if(i.split('.')[1] == "png" or i.split('.')[1] == "jpg" or i.split('.')[1] == "jpeg"):
            m = i.split('.')[0]
            num = m
            if len(m) > 2:
                #print(m)
                num = re.sub('\D',"",m)
                name = m
                dic[num] = name
            else:
                dic[num] = 0
            file_name.append(int(num))
    h = sorted(file_name)
    files = []
    for k in h:
        if(dic[str(k)] == 0):
            fname = input_path + "/" + str(k) + ".png"
        else:
            fname = input_path + "/" + dic[str(k)] + ".png"
        files.append(fname)
    #print(files)
    return files
    #print(files)
def info_process(dic):
    str_mingcheng = "名称"
    str_yxgs = "有限公司"
    str_you = "有"
    str_xian = "限"
    str_gong = "公"
    str_si = "司"
    str_mao = "贸"
    str_hai = "海"
    for k,v in dic.items():
        count = 0
        tmp = 0
        if(v[1].find(str_mingcheng) != -1):
            dic[k][1] = v[1][2:]
        loc_you = v[1].find(str_you)
        loc_xian = v[1].find(str_xian)
        loc_gong = v[1].find(str_gong)
        loc_si = v[1].find(str_si)
        loc_mao = v[1].find(str_mao)
        loc_hai = v[1].find(str_hai)
        #print(loc_you,loc_xian,loc_gong,loc_si)
        if(loc_you != -1):
            dic[k][1] = v[1][0:loc_you] + str_yxgs
            count = 1
        if (loc_xian != -1 and count == 0):
            dic[k][1] = v[1][0:loc_xian - 1] + str_yxgs
            count = 1
        if (loc_gong != -1 and count == 0):
            dic[k][1] = v[1][0:loc_gong - 2] + str_yxgs
            count = 1
        if (loc_si != -1 and count == 0):
            dic[k][1] = v[1][0:loc_si - 3] + str_yxgs
            count = 1
        if(loc_mao != -1):
            if(v[1][loc_mao+1] != "易" and v[1][loc_mao-1] != "商"):
                dic[k][1] = v[1][0:loc_mao-1] + "商" + v[1][loc_mao:]
        if(loc_hai != -1):
            if (v[1][loc_hai + 1] == ")"):
                dic[k][1] = v[1][0:loc_hai-1] + "上" + v[1][loc_hai:]

        for j in v[0]:
            if( ((not j.isdigit()) or (not is_char_elements(j)))and (j != '一')):
                dic[k][0] = v[0][:tmp] + v[0][tmp + 1:]
                tmp = tmp - 1
            if(j == '一'):
                dic[k][0] = dic[k][0].replace("一", "-")
            tmp = tmp + 1
        dic[k][0] = complete_num(dic[k][0])
    return dic
def info_clear(dic):
    for k, v in dic.items():
        count = 0
        for j in v[1]:
            if((j >= 'a' and j <= 'z') or (j >= 'A' and j <= 'Z')):
                dic[k][1] = v[1][:count] + v[1][count+1:]
            count = count + 1
    return dic
def complete_num(num):
    '''
    count = 19 - len(num)
    if(count != 0 and len(num) != 17):
        num = "9" + num
        for i in range(count-1):
            num += str(random.randint(0,9))
    '''
    return num
def get_sorted_filelist():
    dic = {}
    file_name = []
    for i in os.listdir("./original_pic"):
        m = i.split('.')[0]
        num = m
        if len(m) > 2:
            #print(m)
            num = re.sub('\D',"",m)
            name = m
            dic[num] = name
        else:
            dic[num] = 0
        file_name.append(int(num))
    h = sorted(file_name)
    files = []
    for k in h:
        if(dic[str(k)] == 0):
            fname = "./original_pic/" + str(k) + ".png"
        else:
            fname = "./original_pic/" + dic[str(k)] + ".png"
        files.append(fname)
    #print(files)
    return files
    #print(files)
def get_uid(file_name):
    tmp = int(file_name.split('/')[6].split('.')[0][0:2])
    id_char = 1000 * tmp
    id_chinese = id_char + 100
    return id_char,id_chinese

def classify_img(img):
    height = img.shape[0]
    width = img.shape[1]

    #print("img height is : " + str(height) + " and width is : " + str(width))
    judge = height / width
    if judge > 1:
        return 2
    elif judge < 1 and (width > 4000 and height > 3000):
        return 3
    elif judge < 1 and (width < 850 and height < 600):
        return 5
    else:
        return 4

def write_excel(path,dic,file_list):
    #print(dic)
    count = 1
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('test', cell_overwrite_ok=True)
    sheet.write(0, 0, '企业名称')
    sheet.write(0, 1, '企业注册号')
    #for i in dic.values():
    for info in file_list:
        if(info in dic):
            i = dic[info]
            sheet.write(count, 0, i[0])
            sheet.write(count, 1, i[1])
            count = count+1
        book.save(path)
    #excel = open(path)
