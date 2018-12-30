import cv2
import numpy as np
import os
import math
import scipy


def compute_w_element():
    print("compute water mark.........")
    k = 1
    height = 200
    width = 520
    src_folder_name = "./src_p"
    folder_name = "./w_p"
    KERNEL_SIZE = 3
    for root, dirs, files in os.walk(src_folder_name):
        for file in files:
            img = cv2.imread(os.sep.join([root, file]))
            for i in range(int(img.shape[0] / height)):
                for j in range(int(img.shape[1] / width)):
                    result = img[i * height:(i + 1) * height, j * width:(j + 1) * width]
                    cv2.imwrite(folder_name + "/" + str(k) + ".png", result)
                    k += 1
    images = []
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            img = cv2.imread(os.sep.join([root, file]))
            if img is not None:
                images.append(img)
            else:
                print("%s not found." % (file))


    gradx = map(lambda x: cv2.Sobel(x, cv2.CV_64F, 1, 0, ksize=KERNEL_SIZE), images)
    grady = map(lambda x: cv2.Sobel(x, cv2.CV_64F, 0, 1, ksize=KERNEL_SIZE), images)
    wm_x = np.median(np.array(list(gradx)), axis=0) * 0.8
    wm_y = np.median(np.array(list(grady)), axis=0) * 0.8



    fxx = cv2.Sobel(wm_x, cv2.CV_64F, 1, 0, ksize=KERNEL_SIZE)
    fyy = cv2.Sobel(wm_y, cv2.CV_64F, 0, 1, ksize=KERNEL_SIZE)
    laplacian = fxx + fyy
    m, n, p = laplacian.shape

    est = np.zeros(laplacian.shape)
    est[1:-1, 1:-1, :] = np.random.random((m - 2, n - 2, p))
    loss = []

    for i in range(10000):
        old_est = est.copy()
        est[1:-1, 1:-1, :] = 0.25 * (
                    est[0:-2, 1:-1, :] + est[1:-1, 0:-2, :] + est[2:, 1:-1, :] + est[1:-1, 2:, :] - 0.1 * 0.1 * laplacian[1:-1,
                                                                                                            1:-1, :])
        error = np.sum(np.square(est - old_est))
        loss.append(error)

    print(loss)
    est = (est - np.min(est))/(np.max(est) - np.min(est))*255
    est = est.astype(int)

    cv2.imwrite("wm_element.png", est)

