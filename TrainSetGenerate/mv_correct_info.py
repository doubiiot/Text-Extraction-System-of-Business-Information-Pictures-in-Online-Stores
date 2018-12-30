import pickle
import shutil
import os
def get_dic():
    f = open('./label_name', 'r')
    num = 0
    dic = {}
    for i in f.read()[0:-1]:
        dic[num] = i
        num = num + 1
    return dic
def read_pickle():
    f = open('./chinese_labels', 'rb')
    dic = pickle.load(f)
    print(dic)
def find_loc(tmp):
    dic = get_dic()
    for key, value in dic.items():
        if(value == tmp):
            #print(str(tmp + " folder is " + str(key)))
            break
    return key

if __name__ == "__main__":
    #generate_pickle()
    path = "/home/nansang/Desktop/correct2"
    target_path = "/home/nansang/Desktop/workspace/train/dataset/train"
    read_pickle()
    for dirpath, dirnames, filenames in os.walk(path):
        #print(dirnames)
        for i in dirnames:
            print(i)
            loc = find_loc(i)
            path_orignal = os.path.join(path,str(i))
            path_files = os.path.join(target_path,str(loc).zfill(5))
            for file_correct in os.listdir(path_orignal):
                tmp_file = i + "/" + file_correct
                src_file = os.path.join(path,tmp_file)  #original file to move
                dst_file = os.path.join(path_files,file_correct)
                #print("src file is :  " + str(src_file))
                print("dst file is :  " + str(dst_file))
                #print("dst folder is :  " + str(path_files))
                if not os.path.exists(path_files):
                    os.makedirs(path_files)
                shutil.copyfile(src_file,dst_file)


