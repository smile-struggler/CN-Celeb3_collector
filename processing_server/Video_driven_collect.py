# This script is for Audio_driven_collect

# Get the enroll embedding through the enroll video. Divide the segments according to windows_size and segment_size, each segment gets the embedding separately, score by enroll embedding, 
# and retain the reserved_ratio * segment number with the highest score.
import shutil
import numpy as np
from tqdm import tqdm
import my_utils
import os
import cv2
from moviepy.editor import *
from face_recognition import cut_align
from face_recognition import Extract_feature

seg_dict = {}
def cut_enroll_and_test(Video_enroll_path, Transformed_video_path, BV_list, Path_facepic, Path_Unq_enroll, frame_frequence, window_size, segment_size):   
    face_detector = cut_align.FaceDetector()

    # enroll
    print("cut aline for enroll")
    
    # Record the list of unqualified images
    Unq_list = []

    with open(Path_Unq_enroll, 'w+') as Unqwriter:
        for BV_number in tqdm(BV_list):
            file_path = os.path.join(Video_enroll_path , BV_number + '.png')
            Path_enroll_facepic = os.path.join(Path_facepic, BV_number + '.jpg')
            cut_align.run_for_enroll(file_path, Path_enroll_facepic, BV_number, Unqwriter, face_detector, Unq_list, is_reserved = False)

    if len(Unq_list) == 0:
        print("All pictures are qualified")
    else:
        print("--------------------------------------")
        print("There are %d pictures are unqualified!!!"%len(Unq_list))
        print("--------------------------------------")

    # test
    print("cut aline for test")
    for BV_number in tqdm(BV_list):
        file_path = os.path.join(Transformed_video_path , BV_number + '.mp4')
        seg_dict[BV_number] = cut_align.run_for_test(file_path, Path_facepic, frame_frequence, BV_number, window_size, segment_size, face_detector, is_reserved = False)

def Get_result(BV_list, window_size, segment_size, frame_frequence, Path_facepic):
    face_vectorizer = Extract_feature.FaceVectorizer()
    Video_Driven_BV = []
    for BV_number in tqdm(BV_list):
        Path_enroll_facepic = os.path.join(Path_facepic, BV_number + '.jpg')
        if os.path.exists(Path_enroll_facepic) == False:
            continue
        score_dict = {}

        Extract_feature.FaceRecognizer(face_dirPath = Path_facepic, BV_number = BV_number, score_dict = score_dict, face_vectorizer = face_vectorizer)            
        
        seg_count = seg_dict[BV_number]

        seg_score = {}
        for seg_num in range(seg_count):
            for frame_id in range(seg_num * window_size * frame_frequence + 1, (seg_num * window_size + segment_size) * frame_frequence + 1, frame_frequence):
                if frame_id in score_dict:
                    if seg_num not in seg_score:
                        seg_score[seg_num] = score_dict[frame_id]
                    else:
                        seg_score[seg_num] = max(seg_score[seg_num], score_dict[frame_id])
            seg_num += 1
            
        temp_list_sort = sorted(seg_score.items(), key = lambda kv:(kv[1], kv[0]), reverse = True)

        # determine the number of segments

        ans_len = len(temp_list_sort)
        video_driven_result = BV_number
        for i in range(ans_len):
            video_driven_result = video_driven_result + " " + str(temp_list_sort[i][0])
        
        Video_Driven_BV.append(video_driven_result)

    return Video_Driven_BV

    #----------------------

    # # Sort by face score
    # temp_list_sort = sorted(score_dict.items(), key = lambda kv:(kv[1], kv[0]), reverse = True)
    # image_list = []
    # dir_list = []
    # my_utils.get_file_path('/work100/chenrenmiao/Project/220721-LiRAVD/Data/facepic/%s'%BV_number, image_list, dir_list)
    
    # if os.path.exists(os.path.join('/work100/chenrenmiao/Project/220721-LiRAVD/TEMP_DATA/FACE_threshold', BV_number)) is False:
    #     os.makedirs(os.path.join('/work100/chenrenmiao/Project/220721-LiRAVD/TEMP_DATA/FACE_threshold', BV_number))

    # for id,i in enumerate(temp_list_sort):
    #     frameid = str(i[0])
    #     for image_name in image_list:
    #         image_name = image_name.split('/')[-1]
    #         image_fid = image_name.split('_')[-2]
    #         if frameid == image_fid:
    #             src = os.path.join('/work100/chenrenmiao/Project/220721-LiRAVD/Data/facepic/%s'%BV_number,image_name)
    #             dst = os.path.join('/work100/chenrenmiao/Project/220721-LiRAVD/TEMP_DATA/FACE_threshold', BV_number,'%s_%s'%(id,image_name))
    #             shutil.copyfile(src,dst)
    
    # ans_len = int(len(temp_list_sort) * Reserved_ratio)

    # with open('./TEMP_DATA/Video_score/%s.txt'%BV_number,'w') as score_writer:
    #     for i in range(ans_len):
    #         score_writer.write('%d, %s\n' % (i, str(temp_list_sort[i])))

    #----------------------

def run(Video_enroll_path, Transformed_video_path, BV_list, window_size, segment_size, frame_frequence, Path_facepic, Path_Unq_enroll):  
    os.makedirs(Path_facepic, exist_ok=True)

    # Cut align
    cut_enroll_and_test(Video_enroll_path, Transformed_video_path, BV_list, Path_facepic, Path_Unq_enroll, frame_frequence, window_size, segment_size)

    # Get result
    return Get_result(BV_list, window_size, segment_size, frame_frequence, Path_facepic )