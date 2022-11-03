import subprocess
import os
import multiprocessing
from tqdm import tqdm
from pathlib import Path
from moviepy.editor import *


def transform_worker(BV_number, Origin_video_path, Audio_path):
    Origin_path = os.path.join(Origin_video_path , BV_number + '.mp4')
    Transformed_path = os.path.join(Audio_path, BV_number + '.wav')

    if os.path.exists(Transformed_path):
        os.remove(Transformed_path)

    command = ("ffmpeg -i %s -v error -y -acodec pcm_s16le -ac 1 -ar 16000 %s" % (Origin_path, Transformed_path)) 
    output = subprocess.call(command, shell=True, stdout=None)

def run(BV_list, Origin_video_path, Audio_path, worker_num):
    os.makedirs(Audio_path, exist_ok=True)

    p = multiprocessing.Pool(processes=worker_num)
    
    pbar = tqdm(total=len(BV_list), desc='transform audio')
    update = lambda *args: pbar.update()
    for BV_number in BV_list:
        p.apply_async(transform_worker, (BV_number, Origin_video_path, Audio_path), callback=update)

    p.close()
    p.join()