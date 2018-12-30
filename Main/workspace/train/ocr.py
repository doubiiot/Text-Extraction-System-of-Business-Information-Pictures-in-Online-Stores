import os


import random
import tensorflow.contrib.slim as slim
import time
import logging
import numpy as np
import tensorflow as tf
import pickle
from PIL import Image
import cv2
from tensorflow.python.ops import control_flow_ops
import sys
from tools import *
from tensorflow.python.ops import variable_scope as vs
test_file_content = "./tmp"
from preprocess import *

img_size = 64
logger = logging.getLogger('Training a chinese write char recognition')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

'''
tf.app.flags.DEFINE_string('checkpoint_dir', './checkpoint/', 'the checkpoint dir')
tf.app.flags.DEFINE_integer('', 64, "Needs to provide same value as in training.")
tf.app.flags.DEFINE_integer('charset_size', 3792, "Choose the first `charset_size` characters only.")
'''


checkpoint_dir = './checkpoint/'
image_size = 64
charset_size = 3793
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
FLAGS = tf.app.flags.FLAGS

def do_build_graph(top_k):
    keep_prob = tf.placeholder(dtype=tf.float32, shape=[], name='keep_prob')  # dropout打开概率
    images = tf.placeholder(dtype=tf.float32, shape=[None, img_size, img_size, 1], name='image_batch')
    labels = tf.placeholder(dtype=tf.int64, shape=[None], name='label_batch')
    is_training = tf.placeholder(dtype=tf.bool, shape=[], name='train_flag')
    with tf.device('/gpu:0'):
        # network: conv2d->max_pool2d->conv2d->max_pool2d->conv2d->max_pool2d->conv2d->conv2d->
        # max_pool2d->fully_connected->fully_connected
        # 给slim.conv2d和slim.fully_connected准备了默认参数：batch_norm
        with slim.arg_scope([slim.conv2d, slim.fully_connected],
                            normalizer_fn=slim.batch_norm,
                            normalizer_params={'is_training': is_training}):
            #with tf.variable_scope("graph"):
            conv3_1 = slim.conv2d(images, img_size, [3, 3], 1, padding='SAME', scope='conv3_1')
            max_pool_1 = slim.max_pool2d(conv3_1, [2, 2], [2, 2], padding='SAME', scope='pool1')
            conv3_2 = slim.conv2d(max_pool_1, 128, [3, 3], padding='SAME', scope='conv3_2')
            max_pool_2 = slim.max_pool2d(conv3_2, [2, 2], [2, 2], padding='SAME', scope='pool2')
            conv3_3 = slim.conv2d(max_pool_2, 256, [3, 3], padding='SAME', scope='conv3_3')
            max_pool_3 = slim.max_pool2d(conv3_3, [2, 2], [2, 2], padding='SAME', scope='pool3')
            conv3_4 = slim.conv2d(max_pool_3, 512, [3, 3], padding='SAME', scope='conv3_4')
            conv3_5 = slim.conv2d(conv3_4, 512, [3, 3], padding='SAME', scope='conv3_5')
            max_pool_4 = slim.max_pool2d(conv3_5, [2, 2], [2, 2], padding='SAME', scope='pool4')

            flatten = slim.flatten(max_pool_4)
            fc1 = slim.fully_connected(slim.dropout(flatten, keep_prob), 1024,
                                       activation_fn=tf.nn.relu, scope='fc1')
            logits = slim.fully_connected(slim.dropout(fc1, keep_prob),charset_size, activation_fn=None,
                                          scope='fc2')
        # 因为我们没有做热编码，所以使用sparse_softmax_cross_entropy_with_logits
        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels))
        accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(logits, 1), labels), tf.float32))

        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        if update_ops:
            updates = tf.group(*update_ops)
            loss = control_flow_ops.with_dependencies([updates], loss)

        global_step = tf.get_variable("step", [], initializer=tf.constant_initializer(0.0), trainable=False)
        optimizer = tf.train.AdamOptimizer(learning_rate=0.1)
        train_op = slim.learning.create_train_op(loss, optimizer, global_step=global_step)
        probabilities = tf.nn.softmax(logits)

        # 绘制loss accuracy曲线
        tf.summary.scalar('loss', loss)
        tf.summary.scalar('accuracy', accuracy)
        merged_summary_op = tf.summary.merge_all()
        # 返回top k 个预测结果及其概率；返回top K accuracy
        predicted_val_top_k, predicted_index_top_k = tf.nn.top_k(probabilities, k=top_k)
        accuracy_in_top_k = tf.reduce_mean(tf.cast(tf.nn.in_top_k(probabilities, labels, top_k), tf.float32))

    return {'images': images,
            'labels': labels,
            'keep_prob': keep_prob,
            'top_k': top_k,
            'global_step': global_step,
            'train_op': train_op,
            'loss': loss,
            'is_training': is_training,
            'accuracy': accuracy,
            'accuracy_top_k': accuracy_in_top_k,
            'merged_summary_op': merged_summary_op,
            'predicted_distribution': probabilities,
            'predicted_index_top_k': predicted_index_top_k,
            'predicted_val_top_k': predicted_val_top_k}



# 获取汉字label映射表
def get_label_dict():
    #print(os.listdir('./code'))
    f = open('./chinese_labels', 'rb')
    label_dict = pickle.load(f, encoding='bytes')
    #pickle.load(str.encode(m))

    f.close()
    return label_dict

def make_session(type):
    #tf.get_variable_scope().reuse_variables()
    #graph = build_graph(top_k=3)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))
    if(type == 1):
        checkpoint_dir = './checkpoint1/'
    elif(type == 2):
        checkpoint_dir = './checkpoint2/'
    elif(type == 3):
        checkpoint_dir = './checkpoint3/'
    saver = tf.train.Saver()
    ckpt = tf.train.latest_checkpoint(checkpoint_dir)
    if ckpt:
        saver.restore(sess, ckpt)
    print("init sess"+ str(type) + " success!")
    return sess
    '''
    elif(type == 2):
        sess2 = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))
        checkpoint_dir = './checkpoint2/'
        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(checkpoint_dir)
        if ckpt:
            saver.restore(sess2, ckpt)
        print("init ocr2 success!")
        return sess2
    '''




def inference(name_list,sess,graph):
    s_t = time.time()
    image_set = []
    # 对每张图进行尺寸标准化和归一化
    for image in name_list:
        #show_img(image)
        image = Image.fromarray(image)
        #image.show()
        #temp_image = image.convert('L')
        temp_image = image.resize((image_size,image_size), Image.ANTIALIAS)
        temp_image = np.asarray(temp_image) / 255.0
        temp_image = temp_image.reshape([-1, img_size, img_size, 1])
        image_set.append(temp_image)


    val_list = []
    idx_list = []
    # 预测每一张图
    for item in image_set:
        temp_image = item
        predict_val, predict_index = sess.run([graph['predicted_val_top_k'], graph['predicted_index_top_k']],
                                              feed_dict={graph['images']: temp_image,
                                                         graph['keep_prob']: 1.0,
                                                         graph['is_training']: False})
        val_list.append(predict_val)
        idx_list.append(predict_index)
    e_t = time.time()
    #print(e_t - s_t)
    return val_list, idx_list

def do_ocr(img_list,judge,sess,graph,out):
    char_final = ""
    top_k = 3
    flag = 0
    c_list = []
    '''
        for p in img_list:
        c_pic = correcting(p)
        c_list.append(c_pic)
    '''

    label_dict = get_label_dict()
    final_predict_val, final_predict_index = inference(img_list,sess,graph)
    #final_predict_val, final_predict_index = inference(c_list, sess, graph)
    final_reco_text = []  # 存储最后识别出来的文字串

    # 给出预测，candidate1是概率最高的预测
    if judge == 0:
        #print(final_predict_index[0][0][0])
        for i in range(len(final_predict_val)):
            j = 0
            num = int(final_predict_index[i][0][0])
            while not is_char_elements(label_dict[num]):
                j = j + 1
                if j > top_k - 1:
                    break
                num = int(final_predict_index[i][0][j])

            if(j < top_k):
                final_reco_text.append(num)
            else:
                final_reco_text.append(int(final_predict_index[i][0][0]))
        for i in range(len(final_reco_text)):
            if(out == 1):
                print(label_dict[final_reco_text[i]], end="")
            char_final = char_final + str(label_dict[final_reco_text[i]])

    elif judge == 1:
        for i in range(len(final_predict_val)):
            j = 0
            num = int(final_predict_index[i][0][j])
            #print(label_dict[num])
            while not is_chi_elements(label_dict[num]):
                j = j + 1
                if j > top_k - 1:
                    break
                num = int(final_predict_index[i][0][j])

            if (j < top_k):
                final_reco_text.append(num)
            else:
                final_reco_text.append(int(final_predict_index[i][0][0]))

        for i in range(len(final_reco_text)):
            if(out == 1):
                print(label_dict[final_reco_text[i]], end="")
            char_final = char_final + str(label_dict[final_reco_text[i]])
        #print('\n')

    return char_final

    '''
    
    # 打印出所有识别出来的结果（取top 1）
    end_time = time.time()
    for i in range(len(final_reco_text)):
        print(final_reco_text[i], end="")
    '''
    '''
        candidate1 = final_predict_index[i][0][0]
        candidate2 = final_predict_index[i][0][1]
        candidate3 = final_predict_index[i][0][2]
        candidate4 = final_predict_index[i][0][3]
        candidate5 = final_predict_index[i][0][4]
        final_reco_text.append(label_dict[int(candidate1)])
        
    '''
    '''
        logger.info('[the result info] image: {0} predict: {1} {2} {3}; predict index {4} predict_val {5}'.format(
            name_list[i],
            label_dict[int(candidate1)], label_dict[int(candidate2)], label_dict[int(candidate3)],
            final_predict_index[i], final_predict_val[i]))
    '''

    '''
    #print('=====================OCR RESULT=======================\n')

    # 打印出所有识别出来的结果（取top 1）
    for i in range(len(final_reco_text)):
        print(final_reco_text[i],end="")
    '''

if __name__== '__main__':
    init_ocr()