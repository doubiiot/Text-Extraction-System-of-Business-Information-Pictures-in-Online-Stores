import cv2
import numpy as np


def rotate_clockwise_90(src):
    src = cv2.transpose(src)
    src = cv2.flip(src, 1)
    return src


def rotate_clockwise_180(src):
    src = cv2.flip(src, -1)
    return src


def rotate_clockwise_270(src):
    src = cv2.transpose(src)
    src = cv2.flip(src, 0)
    return src

def rotate_clockwise(src,angle):
    if angle == 90:
        src = cv2.transpose(src)
        src = cv2.flip(src, 1)
        return src
    elif angle == 180:
        src = cv2.flip(src, -1)
        return src
    elif angle == 270:
        src = cv2.transpose(src)
        src = cv2.flip(src, 0)
        return src
    else:
        return src

def rotate_image(src, show):

    image_center_x = np.round(src.shape[0] / 2)
    image_center_y = np.round(src.shape[1] / 2)

    smooth_image = cv2.GaussianBlur(src, (9, 9), 4, 4)
    circles = cv2.HoughCircles(smooth_image, cv2.HOUGH_GRADIENT, 1, 200, param1=200, param2=90,
                               minRadius=50, maxRadius=500)

    distance = 65535
    location = 3

    if circles is None:
        return src

    circle_center_x = np.uint16(np.around(circles[0][0][0]))
    circle_center_y = np.uint16(np.around(circles[0][0][1]))

    if show is True:
        radius = np.uint16(np.around(circles[0][0][2]))
        dst = cv2.circle(src, (circle_center_x, circle_center_y), radius, (0, 255, 0), 20, 8, 0)
        show_image = cv2.resize(dst, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        cv2.imshow('rotate image', show_image)
        cv2.waitKey(0)

    if circle_center_x < image_center_x:
        if circle_center_y < image_center_y:
            temp_distance = np.uint16(np.round(np.sqrt(np.power(circle_center_x, 2) + np.power(circle_center_y, 2))))
            if temp_distance < distance:
                distance = temp_distance
                location = 2
        else:
            temp_distance = np.uint16(np.round(np.sqrt(np.power(circle_center_x, 2) + np.power(image_center_y - circle_center_y, 2))))
            if temp_distance < distance:
                distance = temp_distance
                location = 3
    else:
        if circle_center_y < image_center_y:
            temp_distance = np.uint16(np.round(np.sqrt(np.power(image_center_x - circle_center_x, 2) + np.power(circle_center_y, 2))))
            if temp_distance < distance:
                distance = temp_distance
                location = 1
        else:
            temp_distance = np.uint16(np.round(np.sqrt(np.power(image_center_x - circle_center_x, 2) + np.power(image_center_y - circle_center_y, 2))))
            if temp_distance < distance:
                distance = temp_distance
                location = 4

    if location == 1:
        return rotate_clockwise(src,90),90
    elif location == 2:
        return rotate_clockwise(src,180),180
    elif location == 3:
        return rotate_clockwise(src,270),270
    else:
        return src,0