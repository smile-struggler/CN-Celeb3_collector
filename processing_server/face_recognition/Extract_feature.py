import numpy as np
import os
import cv2
from PIL import Image
import time
import mxnet as mx
import mxnet.ndarray as nd
import argparse

from sklearn import preprocessing
from sklearn.model_selection import KFold
from tqdm import tqdm

def load_model(prefix = './resources/insightFace_model/model', epoch = 0, batch_size=10):
    symbol, arg_params, auxiliary_params = mx.model.load_checkpoint(prefix, epoch)
    all_layers = symbol.get_internals()
    output_layer = all_layers['fc1_output']
    context = mx.gpu(0)
    model = mx.mod.Module(symbol=output_layer, context=context, label_names=None)
    model.bind(data_shapes=[('data', (batch_size, 3, 112, 112))])
    model.set_params(arg_params, auxiliary_params)
    return model

def get_time(x):
    hour,minute,second=0,0,0
    if x>3600:
        hour=x//3600
        x%=3600
    if x>60:
        minute=x//60
        x%=60
    second=x
    return "{}小时{}分{}秒".format(hour,minute,second)

class FaceVectorizer(object):
    def __init__(self):
        self.batch_size = 1
        self.model = None
     
    def get_feedData(self, image_4d_array):
        image_list = []
        for image_3d_array in image_4d_array:
            height, width, _ = image_3d_array.shape
            if height!= 112 or width != 112:
                image_3d_array = cv2.resize(image_3d_array, (112, 112))
            image_list.append(image_3d_array)
        image_4d_array_1 = np.array(image_list)
        image_4d_array_2 = np.transpose(image_4d_array_1, [0, 3, 1, 2])
        image_4D_Array = nd.array(image_4d_array_2)
        image_quantity = len(image_list)
        label_1D_Array = nd.ones((image_quantity, ))
        feed_data = mx.io.DataBatch(data=(image_4D_Array,), label=(label_1D_Array,))
        return feed_data
        
    def get_feature_2d_array(self, image_4d_array):
        if len(image_4d_array.shape) ==  3:
            image_4d_array = np.expand_dims(image_4d_array, 0)
        assert len(image_4d_array.shape) == 4, 'image_ndarray shape length is not 4'
        image_quantity = len(image_4d_array)
        if image_quantity != self.batch_size or not self.model:
            self.batch_size = image_quantity
            self.model = load_model(batch_size=self.batch_size)
        feed_data = self.get_feedData(image_4d_array)
        self.model.forward(feed_data, is_train=False)
        outputs = self.model.get_outputs()
        output_2D_Array = outputs[0]
        output_2d_array = output_2D_Array.asnumpy()
        feature_2d_array = preprocessing.normalize(output_2d_array)
        return feature_2d_array

def get_file_path(root_path,dir_list, image_list):
    dir_or_files = os.listdir(root_path)
    dir_or_files.sort()
    for dir_file in dir_or_files:
        dir_file_path = os.path.join(root_path, dir_file)
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            get_file_path(dir_file_path, dir_list, image_list)
        else:
            image_list.append(dir_file_path)
    
class FaceRecognizer(object):
    def __init__(self, face_dirPath, BV_number, score_dict, face_vectorizer):
        self.feature_dimension = 512
        self.face_vectorizer = face_vectorizer
        enroll_embedding = self.extract_enroll_feature(face_dirPath, BV_number)
        self.get_score(face_dirPath, BV_number, enroll_embedding, score_dict)
    
    def extract_enroll_feature(self, face_dirPath, BV_number):
        Path_enroll_facepic = os.path.join(face_dirPath, BV_number + '.jpg')
        image_list = [Path_enroll_facepic]
        self.image_quantity = len(image_list)
        batch_size = 25
        imageData_list = []
        count = 0
        self.database_2d_array = np.empty((self.image_quantity, self.feature_dimension))

        for id,i in tqdm(enumerate(image_list)):
            image_3d_array = np.array(Image.open(i))
            image_3d_array = cv2.resize(image_3d_array, (112, 112))
            imageData_list.append(image_3d_array)
            count += 1
            if count % batch_size == 0:
                image_4d_array = np.array(imageData_list)   
                self.database_2d_array[count-batch_size: count] = self.face_vectorizer.get_feature_2d_array(image_4d_array)
                imageData_list.clear()

        if count % batch_size != 0:
            image_4d_array = np.array(imageData_list)
            remainder = count % batch_size
            self.database_2d_array[count-remainder: count] = self.face_vectorizer.get_feature_2d_array(image_4d_array)

        return self.database_2d_array[0]

    def get_score(self, face_dirPath, BV_number, enroll_embedding, score_dict):
        image_list = []
        dir_list = []

        Path_test_facepic = os.path.join(face_dirPath, BV_number)
        get_file_path(Path_test_facepic, dir_list, image_list)  
            

        self.image_quantity = len(image_list)
        batch_size = 25
        imageData_list = []
        count = 0
        self.database_2d_array = np.empty((self.image_quantity, self.feature_dimension))

        for id,i in tqdm(enumerate(image_list)):
            image_3d_array = np.array(Image.open(i))
            image_3d_array = cv2.resize(image_3d_array, (112, 112))
            imageData_list.append(image_3d_array)
            count += 1
            if count % batch_size == 0:
                image_4d_array = np.array(imageData_list)   
                self.database_2d_array[count-batch_size: count] = self.face_vectorizer.get_feature_2d_array(image_4d_array)
                imageData_list.clear()

        if count % batch_size != 0:
            image_4d_array = np.array(imageData_list)
            remainder = count % batch_size
            self.database_2d_array[count-remainder: count] = self.face_vectorizer.get_feature_2d_array(image_4d_array)

        for i,data in enumerate(image_list):
            temp = data.split("_")
            frameid = int(temp[-2])

            score = np.dot(self.database_2d_array[i], enroll_embedding)/(np.linalg.norm(self.database_2d_array[i])*np.linalg.norm(enroll_embedding))
            if frameid not in score_dict:
                score_dict[frameid] = score
            else:
                score_dict[frameid] = max(score_dict[frameid], score)
    
# if __name__ == '__main__':
#     do_list = ['enroll','test']
#     for do_file in do_list:
#         face_dirPath = f'/nfs/data/raid01/temp/for-chenrenmiao/TESTBIG/{do_file}'
#         out_filePath = f'./feature/{do_file}.npy'
#         face_recognizer = FaceRecognizer(face_dirPath = face_dirPath, out_filePath = out_filePath)
        
#         print('注册集特征提取已完成！')