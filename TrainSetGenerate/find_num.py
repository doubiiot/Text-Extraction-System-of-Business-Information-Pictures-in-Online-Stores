import pickle
def get_dic():
    f = open('./label_name', 'r')
    num = 0
    dic = {}
    for i in f.read()[0:-1]:
        dic[num] = i
        num = num + 1
    return dic
def generate_pickle():
    dic = get_dic()
    f = open('./chinese_labels', 'wb')
    pickle.dump(dic, f)
def read_pickle():
    f = open('./chinese_labels', 'rb')
    dic = pickle.load(f)
    print(dic)
def find_loc(tmp):
    dic = get_dic()
    for key, value in dic.items():
        if(value == tmp):
            print(str(tmp + " folder is " + str(key)))

if __name__ == "__main__":
    #generate_pickle()
    read_pickle()
    find_loc("有")
    find_loc("限")
    find_loc("公")
    find_loc("司")
    find_loc("州")
    find_loc("圳")
    find_loc("芙")
    find_loc("祺")
    find_loc("象")
    find_loc("中")
    find_loc("品")
    find_loc("广")
    find_loc("泰")
    find_loc("东")
    find_loc("伯")

