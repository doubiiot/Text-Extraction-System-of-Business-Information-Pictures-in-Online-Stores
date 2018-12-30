import os
import re
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