# This script is used to get segments by segment_number.

import subprocess
import os
import my_utils
import time
from tqdm import tqdm



def run(Origin_video_path, Path_Audio_Driven_BV, window_size, segment_size, Path_Audio_Driven_Result):
    with open(Path_Audio_Driven_BV) as lines:
        for content in lines:
            BV_result = content.split(",")
            BV_number = BV_result[0]
            my_utils.remake_dir(os.path.join(Path_Audio_Driven_Result, BV_number))

            for i in tqdm(range(1, len(BV_result))):
                command = ("ffmpeg -v error -ss %d -t %d -i %s %s" % (int(BV_result[i]) * window_size, segment_size, os.path.join(Origin_video_path, BV_number + '.mp4'), os.path.join(Path_Audio_Driven_Result, BV_number, str(i) + '.mp4'))) 
                output = subprocess.call(command, shell=True, stdout=None)


if __name__ == '__main__':
    Origin_video_path = './Data/Origin_file'
    Path_Audio_Driven_BV = './Data/Audio_Driven_BV.txt'
    Path_Audio_Driven_Result = './Data/Audio_Driven_Result'
    run(Origin_video_path, Path_Audio_Driven_BV, Path_Audio_Driven_Result)