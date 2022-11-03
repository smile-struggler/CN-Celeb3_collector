# This script is for LiRAVD acquisition
from logging import raiseExceptions
import download_video
import transform_video
import transform_audio
import Audio_driven_collect
import Get_segments
import Video_driven_collect
import Result_merge
import os
import time
import my_utils
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = '3'

# ---------------------------------------------
# Path Setting
# The path for face enroll picture
Data_root_path = './DATA'

Video_enroll_path = './static/media/image/'

# The list containing all BV numbers
# BV_list_txt = './Data/BV_list.txt' 
# BV_list_txt = '%s/demo_bv_list.txt'%Data_root_path

# The directory containing all BV numbers
# BV_list_dir = '%s/demo_bdaima hav_dir'%Data_root_path

# The path for Origin_video
Origin_video_path = '%s/Origin_video'%Data_root_path

# The path for Transformed video
Transformed_video_path = '%s/Transformed_video'%Data_root_path

# The path for Audio
Audio_path = '%s/Audio_file'%Data_root_path

Result_path = '%s/result.txt'%Data_root_path

def run(BV_data):
    

    # Details can be viewed in the Audio-Driven and Video-Driven section
    # common
    window_size = 5
    segment_size = 5

    # Video_driven
    frame_frequence = 25
    # Unqualified enroll picture txt
    Path_Unq_enroll = '%s/Path_Unq_enroll.txt'%Data_root_path
    # The path to save face after cutting align
    Path_facepic = '%s/facepic'%Data_root_path
    # Path_Video_Driven_Result = './Data/Video_Driven_Result'

    start = time.time()

    # ---------------------------------------------
    # 0. Getting BVlist
    BV_list = []
    Audio_enroll_dict = {}
    for i in BV_data:
        print(i)
        BV_number = i.strip().split()[0]
        BV_list.append(BV_number)
        Audio_enroll_dict[BV_number] = [float(r) for r in i.strip().split()[-1].split(',')]

    # ---------------------------------------------
    # 1. Download videos
    # 1. BVLIST 2. Original video save location 3. The number of download threads
    download_video.run(BV_list, Origin_video_path, 4)

    # 2. Transforming videos and videos
    # Adjust video frame rate to 25fps
    # Tranform video to audio
    transform_video.run(BV_list, Origin_video_path, Transformed_video_path, 8)
    transform_audio.run(BV_list, Origin_video_path, Audio_path, 8)

    print(BV_list)

    # ---------------------------------------------
    # 3. Audio-Driven
    # This part gets segments by audio, and each segment has a fixed length of segment_size seconds, window size is window_size seconds. 
    # Segments are numbered according to the start time, starting from 0. If the number be n, the selected segment starts at window_size * n and ends at window_size * n + segment_size
    # The Reserved_ratio segment with the highest score will be reserved.

    # Output: Audio_Driven_Result.txt, The first column is BV number, and then the number of the selected segment

    # # ---------------------------------------------
    Audio_Driven_BV = Audio_driven_collect.run(Audio_path, BV_list, window_size, segment_size, Audio_enroll_dict)

    # # Get segments by audio_driven_result
    # Get_segments.run(Origin_video_path, Path_Audio_Driven_BV, window_size, segment_size,  Path_Audio_Driven_Result)



    # ---------------------------------------------
    # 4. Video-Driven
    # This part gets segments by video, and each segment has a fixed length of segment_size seconds, window size is window_size seconds. 
    # The enroll process detects the face with the largest area in a picture as the registered face
    # In the test process, the face with the highest score by scored with enroll embedding is taken in each frame
    # Segments are numbered according to the start time, starting from 0. If the number be n, the selected segment starts at window_size * n and ends at window_size * n + segment_size
    # The Reserved_ratio segment with the highest score will be reserved.

    # ---------------------------------------------
    Video_Driven_BV = Video_driven_collect.run(Video_enroll_path, Transformed_video_path, BV_list, window_size, segment_size, frame_frequence, 
                                Path_facepic, Path_Unq_enroll)

    # # Get segments by video_driven_result
    # Get_segments.run(Origin_video_path, Path_Video_Driven_BV, window_size, segment_size,  Path_Video_Driven_Result)
    Time = my_utils.get_time(time.time() - start)
    print(Time)
    return Result_merge.run(Audio_Driven_BV, Video_Driven_BV)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--BV_list', type=str)
    arg = parser.parse_args()

    in_BV_list = arg.BV_list
    in_BV_list = in_BV_list.replace("Live Broadcast","Live_Broadcast")
    BV_list_temp = in_BV_list.split()
    temp_str = ""
    BV_list = []
    for id,i in enumerate(BV_list_temp):
        if id % 4 == 0:
            temp_str = i
        elif id % 4 == 1 or id % 4 == 2:
            temp_str = temp_str + ' ' + i
        else:
            temp_str = temp_str + ' ' + i
            BV_list.append(temp_str)

    lastresult = run(BV_list)
    with open(Result_path, 'w') as writer:
        for i in lastresult:
            writer.write(i + '\n')