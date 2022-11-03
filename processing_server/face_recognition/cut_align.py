from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
import cv2
import time
import sys
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
tf.reset_default_graph()
from . import FaceDetection_mtcnn
import argparse
import shutil
from tqdm import tqdm
def get_session():
    config = tf.ConfigProto()
    # tf.get_variable_scope().reuse_variables()
    config.gpu_options.allow_growth = True
    session = tf.Session(config=config)
    return session
    
def get_new_box(box, margin, image_size):
    image_width, image_height = image_size
    x1, y1, x2, y2 = box
    new_x1 = max(0, x1 - margin/2)
    new_y1 = max(0, y1 - margin/2)
    new_x2 = min(image_width, x2 + margin/2)
    new_y2 = min(image_height, y2 + margin/2)
    new_box = new_x1, new_y1, new_x2, new_y2
    return new_box 


class FaceDetector(object):
    def __init__(self, model_dirPath = './resources/mtcnn_model'):
        self.session = get_session()
        with self.session.as_default():
            self.pnet, self.rnet, self.onet = FaceDetection_mtcnn.create_mtcnn(
                self.session, model_dirPath)
    
    def detect_image(self, image_3d_array, margin=8):
        min_size = 20
        threshold_list = [0.6, 0.7, 0.7]
        factor = 0.7
        box_2d_array, point_2d_array = FaceDetection_mtcnn.detect_face(
            image_3d_array, min_size, 
            self.pnet, self.rnet, self.onet,
            threshold_list, factor)
        box_2d_array_1 = box_2d_array.reshape(-1, 5)
        box_2d_array_2 = box_2d_array_1[:, 0:4]
        box_list = []
        image_height, image_width, _ = image_3d_array.shape
        image_size = image_width, image_height
        for box in box_2d_array_2:
            new_box = get_new_box(box, margin, image_size)
            box_list.append(new_box)
        box_2d_array_3 = np.array(box_list).astype('int')
        if len(point_2d_array) == 0:
            point_2d_array_1 = np.empty((0, 10))
        else:
            point_2d_array_1 = np.transpose(point_2d_array, [1, 0])    
        return box_2d_array_3, point_2d_array_1
 

def get_affine_image_3d_array(original_image_3d_array, box_1d_array, point_1d_array):
    
    affine_percent_1d_array = np.array([0.3333, 0.3969, 0.7867, 0.4227, 0.7, 0.7835])
    
    x1, y1, x2, y2 = box_1d_array
    clipped_image_3d_array = original_image_3d_array[y1:y2, x1:x2]
    clipped_image_width = x2 - x1
    clipped_image_height = y2 - y1
    clipped_image_size = np.array([clipped_image_width, clipped_image_height])
    
    old_point_2d_array = np.float32([
        [point_1d_array[0]-x1, point_1d_array[5]-y1],
        [point_1d_array[1]-x1, point_1d_array[6]-y1],
        [point_1d_array[4]-x1, point_1d_array[9]-y1]
        ])   

    new_point_2d_array = (affine_percent_1d_array.reshape(-1, 2)
        * clipped_image_size).astype('float32')
    affine_matrix = cv2.getAffineTransform(old_point_2d_array, new_point_2d_array)    
    new_size = (112, 112)

    clipped_image_size = (clipped_image_width, clipped_image_height)
    affine_image_3d_array = cv2.warpAffine(clipped_image_3d_array, 
        affine_matrix, clipped_image_size)
    affine_image_3d_array_1 = cv2.resize(affine_image_3d_array, new_size)
    return affine_image_3d_array_1
  
    
def get_time(x):
    hour,minute,second=0,0,0
    if x>3600:
        hour=x//3600
        x%=3600
    if x>60:
        minute=x//60
        x%=60
    second=x
    return "{}h, {}m, {}s".format(hour,minute,second)

def run_for_enroll(file_path, Path_facepic, BV_number, Unqwriter, face_detector, Unq_list, is_reserved = True):
    # tf.reset_default_graph()
    margin = 8

    if os.path.exists(Path_facepic):
        if is_reserved:
            return
        else:
            os.remove(Path_facepic)

    bgr_3d_array = cv2.imread(file_path)
    rgb_3d_array = cv2.cvtColor(bgr_3d_array, cv2.COLOR_BGR2RGB)
    image_3d_array = np.array(rgb_3d_array)
    box_2d_array, point_2d_array = face_detector.detect_image(image_3d_array, margin)
    face_quantity = len(box_2d_array)
    if face_quantity == 0:
        Unqwriter.write('%s\n'%BV_number)
        Unq_list.append(BV_number)
        return

    temp_Index = 0
    face_Index = 0
    max_area = 0
    for box_1d_array, point_1d_array in zip(box_2d_array, point_2d_array):
        x1, y1, x2, y2 = box_1d_array
        clipped_image_width = x2 - x1
        clipped_image_height = y2 - y1
        area = clipped_image_width * clipped_image_height
        if area > max_area:
            max_area = area
            face_Index = temp_Index
        temp_Index += 1

    temp_Index = 0
    for box_1d_array, point_1d_array in zip(box_2d_array, point_2d_array):
        if temp_Index == face_Index:
            affine_image_3d_array = get_affine_image_3d_array(image_3d_array, 
                box_1d_array, point_1d_array)
            affine_image = Image.fromarray(affine_image_3d_array)   
            affine_image.save(Path_facepic)
        temp_Index += 1

def run_for_test(file_path, Path_facepic, frame_frequence, BV_number, window_size, segment_size, face_detector, is_reserved = True):
    # tf.reset_default_graph()
    print(BV_number)
    margin = 8

    Path_test_facepic = Path_facepic
    Path_facepic = os.path.join(Path_facepic, BV_number)

    # print("???%s"%Path_facepic)
    

    # start=time.time()
    #改成对视频的处理
    camera = cv2.VideoCapture(file_path)
    # # framenum = camera.get(cv2.CAP_PROP_FRAME_COUNT)
    # is_successful, image_3d_array = camera.read()
    # if is_successful == 0:
    #     print('加载失败')
    #     sys.exit()

    num = 0
    # startTime = time.time()
    try:
        framenum = camera.get(cv2.CAP_PROP_FRAME_COUNT)
        seg_count = int((framenum - frame_frequence * segment_size) / (window_size * frame_frequence))

        if os.path.exists(Path_facepic):
            if is_reserved:
                camera.release()
                cv2.destroyAllWindows()
                return int(seg_count + 1)
            else:
                shutil.rmtree(Path_facepic)
        os.makedirs(Path_facepic)
        
        framenum = seg_count * window_size * frame_frequence + frame_frequence * segment_size

        with tqdm(total = int(seg_count + 1) * 5) as qbar:
            while True:
                is_successful, bgr_3d_array = camera.read()
                if is_successful is False:
                    break
                if num % frame_frequence != 0:
                    num += 1
                    if num > framenum:
                        break
                    continue
                num += 1
                if num > framenum:
                    break
                qbar.update(1)
                rgb_3d_array = cv2.cvtColor(bgr_3d_array, cv2.COLOR_BGR2RGB)
                image_3d_array = np.array(rgb_3d_array)
                box_2d_array, point_2d_array = face_detector.detect_image(image_3d_array, margin)
                face_quantity = len(box_2d_array)
                if face_quantity == 0:
                    # print('文件路径为%s的视频的第%d帧检测出的人脸数目等于%d，跳过该帧' %(in_filePath, frameid, face_quantity))
                    continue

                personId = 0
                for box_1d_array, point_1d_array in zip(box_2d_array, point_2d_array):
                    personId += 1
                    affine_image_3d_array = get_affine_image_3d_array(image_3d_array, 
                        box_1d_array, point_1d_array)
                    affine_image = Image.fromarray(affine_image_3d_array)   
                    save_path = os.path.join(Path_facepic, '_%d_%d.jpg'%(num, personId))
                    affine_image.save(save_path)

    except Exception as e:
        print(e)
        # print(num)
        # print(framenum)
    finally:
        camera.release()
        cv2.destroyAllWindows()
    
    return int(seg_count + 1)

