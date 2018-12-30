# -*- coding: utf-8 -*-
import socket
import threading
import datetime
import struct
import os
import time
import pickle
from main import start

# listen all ip
HOST = '127.0.0.1'
# set port
PORT = 8888
# store path
STORE_PATH = ''
# store path list
STORE_PATH_LIST = []
# server running state
SERVER_RUN_FLAG = True
# set thread lock
flag_lock = threading.Lock()
# client path number
PATH_NUMBER = -1

L = threading.Lock()
# client operation
def client_operate(client_socket, path_number):
    L.acquire()
    # send server store file path
    server_path = STORE_PATH_LIST[path_number]
    client_socket.sendall(server_path[-12:].encode('utf-8'))
    # receive client transform finish singal
    message = client_socket.recv(4)
    # analyse picture
    xls_path = server_path + "/result"
    if message is not None:
        start(server_path,xls_path)
        # finish analyse picture
        print("Finish Analyse Picture.")
        client_socket.sendall(b'ok')
        #time.sleep(20)
    else:
        print("Transform File Fail.")
    client_socket.close()
    L.release()  # 释放锁

# start socket communication
def start_socket(host,port):
    print('Server Is Starting ...\n')
    # create server socket
    server_socket = socket.socket()
    # set socket timeout
    server_socket.settimeout(100)
    # bind socket ip and port
    server_socket.bind((host,port))
    # set socket listen queue
    server_socket.listen(5)
    # acquire thread lock
    flag_lock.acquire()
    # loop accpet client
    while SERVER_RUN_FLAG:
        flag_lock.release()
        client = None
        try:
            client, address = server_socket.accept()
            print("Establish A New Socket , IP is ", address)
        except socket.timeout:
            print("Wait For Timeout!")
            pass
        if client:
            # set store_path for each client
            global STORE_PATH
            STORE_PATH = "/home/nansang/socket/original_picture/" + datetime.datetime.now().strftime('%y%m%d%H%M%S')
            STORE_PATH_LIST.append(STORE_PATH)
            global PATH_NUMBER
            PATH_NUMBER = PATH_NUMBER + 1
            # judge floder whether exist
            if not os.path.exists(STORE_PATH):
                os.mkdir(STORE_PATH)
            # create new client socket thread
            t = threading.Thread(target=client_operate, args=(client, PATH_NUMBER))
            # synchronize thread
            t.setDaemon(True)
            # start new client thread
            t.start()
        flag_lock.acquire()
    # close server socket
    server_socket.close()


if __name__ == '__main__':
    # task
    start_socket(HOST, PORT)

    # thread
    # #create thread
    # server = threading.Thread(target=start_socket, args=(HOST, PORT))
    # #run thread
    # server.start()




