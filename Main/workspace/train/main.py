import cv2
import os
import time
import threading
from clear_water_mark import *
from rotate_image import *
from preprocess import *
from tools import *
from ocr import *
from MyThread import *
from split_text import *
from split_text_advanced0 import *
from split_text_advanced1 import *
from split_text_advanced2 import *
from split3 import *


def process(file_list, graph, sess,sess_n, jug,t_id):

    time_start = time.time()
    dic = {}
    for file_name in file_list:
        image = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
        id_num,id_char = get_uid(file_name)
        num = len(cv2.split(image))
        #thread1
        if (num == 4 and jug == True):
            print("thread " + str(t_id) + " processing : " + file_name)
            gray_img = clear_water_mark_alpha(image, 250, False)
            pic_list, id = vertical_split(gray_img, False, False, 0)

            #start locate
            line_number = len(pic_list)
            number_flag = False
            name_flag = False
            for t in range(0, line_number):
                if number_flag is True and name_flag is True:
                    break
                sign_list = sign_split(pic_list[t])
                text = do_ocr(sign_list, 1, sess, graph, 0)
                judge_value = locate_line(text)
                if judge_value == 1:
                    img_list_num, k = horizontal_split_char(pic_list[t], False, False, id_num)
                    number_flag = True
                elif judge_value == 0:
                    img_list_char, k = horizontal_split_chinese(pic_list[t], False, False, id_char)
                    name_flag = True
            #end locate

            n = do_ocr(img_list_num, 0, sess, graph,0)
            c = do_ocr(img_list_char, 1, sess, graph,0)
            dic[file_name] = [n, c]
            dic = info_clear(dic)

        #thread2
        if(num != 4 and jug == False and classify_img(image)!=5):
            print("thread " + str(t_id) + " processing : " + file_name)
            pic_r = prepreocess_the_picture(image)
            pic,angel = rotate_image(pic_r,False)
            type = classify_img(pic)
            # 34.png
            if type == 2:
                number_img_w, name_img_w, number_img_n,name_img_n= locate_picture0(image, pic)
                img_list_char_w,img_list_char, k = horizontal_split_char2(number_img_w, number_img_n, True, False, id_num)
                img_list_chi_w,img_list_chi,l = horizontal_split_chinese2(name_img_w, name_img_n, True, False, id_char)
            # 50.png clear pic
            elif type == 3:
                number_img, name_img = locate_picture_high(pic)
                img_list_char, k = horizontal_split_char3(number_img,True, False, id_num)
                img_list_chi, l = horizontal_split_chinese3(name_img, True, False, id_char)
            # 40.png
            elif type == 4:
                number_img, name_img = locate_picture_low(pic)
                img_list_char, k = horizontal_split_char4(number_img, True, False, id_num)
                img_list_chi, l = horizontal_split_chinese4(name_img, True, False, id_char)
            if type == 2 or type == 4:
                n = do_ocr(img_list_char, 0, sess_n, graph, 0)
            else:
                n = do_ocr(img_list_char, 0, sess, graph, 0)
            print("\n")
            xx = 0
            if type == 4:
                img_list_chi = convert_pic(img_list_chi[1:], id_num)
                for zz in img_list_chi:
                    store_img(zz,xx)
                    xx+=1
            c = do_ocr(img_list_chi, 1, sess, graph, 0)
            dic[file_name] = [n, c]
            dic = info_process(dic)
    if(t_id == 1):
        print("thread1 time is : ")
        time_end = time.time()
        print(time_end-time_start)
    elif(t_id == 2):
        print("thread2 time is : ")
        time_end = time.time()
        print(time_end - time_start)
    else:
        print("thread else time is : ")
        time_end = time.time()
        print(time_end - time_start)
    print("\n")
    return dic




def start(input_path,output_path):
    output_path = output_path + ".xls"
    print(input_path,output_path)
    time_start = time.time()

    graph = do_build_graph(top_k=3)
    sess1 = make_session(1)
    sess2 = make_session(2)
    sess3 = make_session(3)
    file_list = get_filelist(input_path)
    print(file_list)
    t1 = MyThread(process,args=(file_list, graph, sess1, sess1,True,1,))
    t2 = MyThread(process,args=(file_list, graph, sess2, sess3, False,2,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


    final_dic = dict(t1.get_result(), **t2.get_result())
    write_excel(output_path,final_dic,file_list)
    time_end = time.time()
    return str(time_end - time_start)

if __name__ == '__main__':
    start("/home/nansang/socket/original_picture/180729230956","/home/nansang/socket/original_picture/180729230956/result")


