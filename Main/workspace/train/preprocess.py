import cv2
import os
import numpy as np
import compute_watermark as cmw
from tools import *


def remove_illumination(img_gray, size):
    row = img_gray.shape[0]
    col = img_gray.shape[1]
    m = int((row - 1) / size[0]) + 1
    n = int((col - 1) / size[1]) + 1
    E = np.zeros((m, n))
    global_grey = np.mean(img_gray)
    operation_in_divide(remove_illumination_in_divide, img_gray, size, E)
    E = E - global_grey
    R = cv2.resize(E, (img_gray.shape[1], img_gray.shape[0]), cv2.INTER_CUBIC)
    img_gray = 1.0 * img_gray - R
    img_gray = matrix_to_pic(img_gray)
    return img_gray


def remove_illumination_in_divide(img_gray, *para):
    E, x0, x1, y0, y1, i, j = para
    E[i, j] = np.mean(img_gray[x0:x1, y0:y1])


def gamma(img_gray):
    img_gray = 1.0 * img_gray * img_gray
    img_gray = matrix_to_pic(img_gray)
    return img_gray


'''def thresh(img, low, high):
    if low == 0:
        low += 1
    ret, img_th = cv2.threshold(img, high-1, 255, cv2.THRESH_TOZERO_INV)
    ret, img_th = cv2.threshold(img_th, low-1, 255, cv2.THRESH_BINARY)
    return img_th'''


def sharpen(img):
    img_blur = cv2.blur(img, (3, 3))
    img_mask = img - img_blur
    # k = np.min((255 - img) / (img_mask + 0.1))
    # print(k)
    k = 1.0
    img = img - k * img_mask
    img = matrix_to_pic(img)
    return img


'''def get_thresh_one(img_gray, labels):
    images = []
    for i in range(len(labels)-1):
        img = thresh(img_gray, labels[i], labels[i+1])
        images.append(img)
        cv2.imshow("imgth"+str(i), img)
    img_re = images[0] + images[1]
    return img_re'''


def improve(img_gray):
    # img_gray = cv2.medianBlur(img_gray, 3)
    lap_mask = cv2.Laplacian(img_gray, cv2.CV_16S)
    img_lap = 1.0 * img_gray - lap_mask
    img_lap = matrix_to_pic(img_lap)
    cv2.imshow("img_lap", img_lap)
    cv2.waitKey()
    gradx = cv2.Sobel(img_gray, cv2.CV_16S, 1, 0)
    grady = cv2.Sobel(img_gray, cv2.CV_16S, 0, 1)
    grad = np.abs(gradx) + np.abs(grady)
    img_grad = 1.0 * img_gray - grad
    img_grad = matrix_to_pic(img_grad)
    img_grad = cv2.medianBlur(img_grad, 3)
    cv2.imshow("img_grad", img_grad)
    cv2.waitKey()
    img_grad = cv2.medianBlur(img_grad, 3)
    cv2.imshow("img_grad", img_grad)
    cv2.waitKey()
    img_mask = 1.0 * img_lap * img_grad
    img_mask = matrix_to_pic(img_mask)
    cv2.imshow("img_mask", img_mask)
    cv2.waitKey()
    img_gray = 1.0 * img_gray + img_mask
    img_gray = matrix_to_pic(img_gray)
    cv2.imshow("img_gray", img_gray)
    cv2.waitKey()
    img_gray = gamma(img_gray)
    cv2.imshow("img_gray", img_gray)
    cv2.waitKey()
    '''img_gray = thresh(img_gray)
    wm_gray = resize_watermark(img_gray.shape)
    ret, wm_gray = cv2.threshold(wm_gray, 0, 255, cv2.THRESH_OTSU)
    cv2.imshow("img_gray", wm_gray)
    cv2.waitKey()
    img_gray = 255 - img_gray
    labels = np.where(wm_gray == 0, 1, 0)
    wm_gray = 1.0 * wm_gray / 255
    img_gray = labels * img_gray
    img_gray = matrix_to_pic(img_gray)
    img_gray = 255 - img_gray'''

    return img_gray


def get_background_light(img_gray):
    img = img_gray.reshape((1, -1))
    num = int(img.shape[1] / 5)
    img = np.sort(img)
    light = int(np.mean(img[0, img.shape[1] - num:img.shape[1]]) + 0.5)
    return light


def resize_watermark(size):
    wm_path = "wm_element.png"
    if not os.path.exists(wm_path):
        cmw.compute_w_element()
    wm_element = cv2.imread(wm_path)
    wm_element = cv2.cvtColor(wm_element, cv2.COLOR_BGR2GRAY)
    wm = wm_element
    while wm.shape[0] < size[0]:
        wm = np.vstack((wm, wm))
    while wm.shape[1] < size[1]:
        wm = np.hstack((wm, wm))
    wm = wm[0:size[0], 0:size[1]]
    return wm


def remove_watermark(img_gray, size):
    wm_gray = resize_watermark(img_gray.shape)
    ret, wm_gray = cv2.threshold(wm_gray, 0, 255, cv2.THRESH_OTSU)
    labels = np.where(wm_gray == 0, 1, 0)
    wm_gray = 1.0 * wm_gray / 255
    img_gray = labels * img_gray

    operation_in_divide(remove_watermark_in_divide, img_gray, size, wm_gray)
    img_gray = matrix_to_pic(img_gray)
    return img_gray


def operation_in_divide(operation, img_gray, size, *para):
    row = img_gray.shape[0]
    col = img_gray.shape[1]
    m = int((row - 1) / size[0]) + 1
    n = int((col - 1) / size[1]) + 1
    for i in range(m - 1):
        for j in range(n - 1):
            x0 = i * size[0]
            x1 = (i + 1) * size[0]
            y0 = j * size[1]
            y1 = (j + 1) * size[1]
            operation(img_gray, *para, x0, x1, y0, y1, i, j)
        x0 = i * size[0]
        x1 = (i + 1) * size[0]
        y0 = (n - 1) * size[1]
        y1 = img_gray.shape[1]
        operation(img_gray, *para, x0, x1, y0, y1, i, n - 1)
    for j in range(n - 1):
        x0 = (m - 1) * size[0]
        x1 = img_gray.shape[0]
        y0 = j * size[1]
        y1 = (j + 1) * size[1]
        operation(img_gray, *para, x0, x1, y0, y1, m - 1, j)
    x0 = (m - 1) * size[0]
    x1 = img_gray.shape[0]
    y0 = (n - 1) * size[1]
    y1 = img_gray.shape[1]
    operation(img_gray, *para, x0, x1, y0, y1, m - 1, n - 1)


def test(img):
    img[0, 0] = 1


def remove_watermark_in_divide(img_gray, *para):
    wm_gray, x0, x1, y0, y1, i, j = para
    img = img_gray[x0:x1, y0:y1]
    wm = wm_gray[x0:x1, y0:y1]
    light = get_background_light(img)
    img_gray[x0:x1, y0:y1] = img + wm * light


def normlized(img_gray):
    img_gray = 1.0 * (img_gray - np.min(img_gray)) / (np.max(img_gray) - np.min(img_gray))
    return img_gray


def norm_to_pic(img_gray):
    img_gray = img_gray * 255 + 0.5
    img_gray = img_gray.astype(np.uint8)
    return img_gray


def matrix_to_pic(matrix):
    img_gray = norm_to_pic(normlized(matrix))
    return img_gray


def prepreocess_the_picture(img):
    size = (30, 30)
    # img_gray = gamma(img_gray)
    img = equal_BGR(img)
    img_gray = cv2.split(img)[2]
    img_gray = remove_watermark(img_gray, size)
    img_gray = remove_illumination(img_gray, size)
    ret, img_re = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)
    return img_re


def make_table():
    X = np.linspace(0, 255, 256)
    b = 4 * np.pi / 255
    a = 1 / 255
    Y = -1 * a / b * np.sin(b * X) + a * X
    Y = Y.reshape((-1, 1))
    Y = Y * 255 + 0.5
    Y = Y.astype(np.uint8)
    return Y


def equal_hist(img_gray):
    hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
    hist = hist / np.sum(hist)
    h = np.zeros((256, 1))
    for i in range(256):
        h[i, 0] = np.sum(hist[:i + 1, 0])
    h = h * 255 + 0.5
    h = h.astype(np.uint8)
    return h


def check_table(hist, table, value):
    E = 1.0 * (table - hist[value, 0]) * (table - hist[value, 0])
    m = np.min(E)
    pos = np.where(E == m)
    pos = pos[0][0]
    return pos


def match_hist(img_gray):
    hist = equal_hist(img_gray)
    table = make_table()
    row = img_gray.shape[0]
    col = img_gray.shape[1]
    for i in range(row):
        for j in range(col):
            value = check_table(hist, table, img_gray[i, j])
            img_gray[i, j] = value
    return img_gray


def equal_BGR(img):
    b, g, r = cv2.split(img)
    b_avg = np.mean(b)
    g_avg = np.mean(g)
    r_avg = np.mean(r)

    K = (b_avg + g_avg + r_avg) / 3
    Kb = K / b_avg
    Kg = K / g_avg
    Kr = K / r_avg
    img = Kb * b + Kg * g + Kr * r
    img = cv2.merge((b, g, r))
    return img


def thresh_in_divide(img_gray, *para):
    p1, p2, p3, x0, x1, y0, y1, i, j = para
    img = img_gray[x0:x1, y0:y1]
    ret, img_gray[x0:x1, y0:y1] = cv2.threshold(img, p1, p2, p3)


def thresh(img_gray, size):
    operation_in_divide(thresh_in_divide, img_gray, size, 0, 255, cv2.THRESH_OTSU)
    return img_gray

def correcting(img_gray):
    im = img_gray.copy()
    kernel = np.ones((2,2),np.uint8)
    img_gray = cv2.morphologyEx(img_gray, cv2.MORPH_OPEN, kernel)
    row_start = img_gray.shape[0]
    row_end = 0
    col_start = img_gray.shape[1]
    col_end = 0
    image, contours, hierarchy = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if x < col_start:
            col_start = x
        if x+w > col_end:
            col_end = x+w
        if y < row_start:
            row_start = y
        if y+h > row_end:
            row_end = y+h
    return im[row_start:row_end, col_start:col_end]

def convert_pic(img_list,id_num):
    c_list = []
    count = 0
    for pic in img_list:
        #store_img(correcting(pic),str(id_num) + str(count))
        c_list.append(correcting(pic))
        count += 1
    return c_list