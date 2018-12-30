# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QDesktopWidget, \
    QMessageBox, QLineEdit, QFileDialog, QProgressBar
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
import threading
import os
import socket
import paramiko
import time
import pickle
# recv info from server 
SOCKET_HOST = 'h215335d32.iask.in'
SSH_HOST = '115.159.22.181'
SOCKET_PORT = 21423
SSH_PORT = 6789
USERNAME = 'nansang'
PASSWORD = '123'
src_path = ''
result_path = ''
server_path = ''
server_prefix = r'/home/nansang/socket/original_picture/'
files_name = []
files_path = []


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.txt_src = QLineEdit(self)
        self.txt_src.setGeometry(QtCore.QRect(20, 20, 280, 30))
        self.txt_src.setPlaceholderText("请选择您想要提取的图片文件夹")

        self.btn_browse = QPushButton("浏览", self)
        self.btn_browse.move(310, 20)
        self.btn_browse.setFixedWidth(80)
        self.btn_browse.setFixedHeight(30)
        self.btn_browse.clicked.connect(self.btn_browse_clicked)

        self.txt_dst = QLineEdit(self)
        self.txt_dst.setGeometry(QtCore.QRect(20, 70, 280, 30))
        self.txt_dst.setPlaceholderText("请选择您想要存储识别结果的文件夹")

        self.btn_browse_result = QPushButton("存储", self)
        self.btn_browse_result.move(310, 70)
        self.btn_browse_result.setFixedWidth(80)
        self.btn_browse_result.setFixedHeight(30)
        self.btn_browse_result.clicked.connect(self.btn_browse_result_clicked)

        self.btn_identify = QPushButton("识别", self)
        self.btn_identify.move(30, 120)
        self.btn_identify.setFixedWidth(130)
        self.btn_identify.setFixedHeight(40)
        self.btn_identify.clicked.connect(self.btn_identify_clicked)

        self.btn_exit = QPushButton("退出", self)
        self.btn_exit.move(240, 120)
        self.btn_exit.setFixedWidth(130)
        self.btn_exit.setFixedHeight(40)
        self.btn_exit.clicked.connect(self.btn_exit_clicked)

        self.bar = QProgressBar(self)
        self.bar.setFixedSize(400, 20)
        self.bar.move(20, 175)

        self.statusBar()
        self.setFixedSize(425, 220)
        self.center()
        self.setWindowTitle("网店工商信息图片文字提取器")
        self.setWindowIcon(QIcon('image/computer.png'))
        self.show()

    # get client file information
    def get_files_info(self, path):
        # judge file whether exist
        if not path or not os.path.exists(path):
            self.statusBar().showMessage("不存在这样的路径")
            return None
        # ergodic all files in floder
        files = os.walk(path)
        global files_name
        files_name = []
        global files_path
        files_path = []
        for p, ds, fs in files:
            # get floder's all file path
            for f in fs:
                # get each absolute path
                file_path = os.path.join(p, f)
                file_path = file_path.replace('\\', '/')
                files_path.append(file_path)
                # get each file name
                file_name = file_path[len(path) + 1:]
                files_name.append(file_name)

    # start socket task
    def start_socket(self, src):
        # judge file path
        if not os.path.exists(src):
            self.statusBar().showMessage("图片文件夹不存在")
            return
        # get host and port info
        info_transport = paramiko.Transport(('115.159.31.212', 22))
        info_transport.connect(username='root', password='lyk27038LYK')
        sftp = paramiko.SFTPClient.from_transport(info_transport)
        sftp.get('/root/information.pkl', './information.pkl')
        info_transport.close()
        file = open('./information.pkl', 'rb')
        message = pickle.load(file)
        SOCKET_HOST = message['SOCKET_HOST']
        SSH_HOST = message['SSH_HOST']
        SOCKET_PORT = int(message['SOCKET_PORT'])
        SSH_PORT = int(message['SSH_PORT'])
        file.close()
        # establish socket and recv server_path
        self.statusBar().showMessage("正在建立socket连接")
        client = socket.socket()
        client.connect((SOCKET_HOST, int(SOCKET_PORT)))
        global server_path
        server_path = client.recv(256).decode('utf-8')
        # establish ssh
        transport = paramiko.Transport((SSH_HOST, SSH_PORT))
        transport.connect(username=USERNAME, password=PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        # read file list
        self.statusBar().showMessage("正在读取文件列表")
        self.get_files_info(src)
        # transform file
        self.statusBar().showMessage("正在上传图片")
        files_number = len(files_name)
        ratio = int(100 / files_number)
        for number in range(0, files_number):
            self.bar.setValue(number * ratio)
            server_file = server_prefix + server_path + r'/' + files_name[number]
            try:
                sftp.put(files_path[number], server_file)
            except Exception as e:
                print(e)
                print("Put File Path Error.")
                print("server_file: ", server_file)
                print("files_path: ", files_path[number])
                self.statusBar().showMessage("服务器端文件路径错误.")
                transport.close()
                client.close()
                return
        self.bar.setValue(100)
        client.send(b'ok')
        # analyse picture
        self.statusBar().showMessage("正在提取图片信息")
        start_time = time.time()
        # receive result
        result = client.recv(4)
        if result is not None:
            end_time = time.time()
            analyse_time = end_time - start_time
            server_file = server_prefix + server_path + r'/' + 'result.xls'
            result_file = result_path + 'result.xls'
            try:
                sftp.get(server_file, result_file)
            except:
                print("Get File Path Error.")
                self.statusBar().showMessage("下载结果失败")
                transport.close()
                client.close()
                return
            message = "完成识别,本次识别共用时:" + str(analyse_time)
            self.statusBar().showMessage(message)
            transport.close()
            client.close()

    #退出设置
    def btn_exit_clicked(self):
        QtCore.QMetaObject.connectSlotsByName(self.close())

    #识别设置
    def btn_identify_clicked(self):
        global src_path
        client_thread = threading.Thread(target=self.start_socket, args=(src_path, ))
        self.statusBar().showMessage("启动socket连接")
        client_thread.start()
        client_thread.join()

    #浏览原始文件夹设置
    def btn_browse_clicked(self):
        self.bar.setValue(0)
        global src_path
        src_path = QFileDialog.getExistingDirectory(self, caption="选择图片文件夹", directory=".")
        if src_path is None:
            self.statusBar().showMessage("您未选择任何图片文件夹")
        else:
            self.txt_src.setText(src_path)
            message = "您选择了" + src_path
            self.statusBar().showMessage(message)


    #浏览存储文件夹设置
    def btn_browse_result_clicked(self):
        self.bar.setValue(0)
        global result_path
        result_path = QFileDialog.getExistingDirectory(self, caption="选择图片文件夹", directory=".")
        if result_path is None:
            self.statusBar().showMessage("您未选择任何图片文件夹")
        else:
            value = result_path[-1:]
            if value != '/':
                result_path = result_path + '/'
            self.txt_dst.setText(result_path)
            message = "您选择了" + result_path
            self.statusBar().showMessage(message)

    #退出时进行提示
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "您确定要退出该程序?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_ui = ClientWindow()
    sys.exit(app.exec_())
