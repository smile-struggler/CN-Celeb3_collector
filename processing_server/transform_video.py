import subprocess
import os
import multiprocessing
from tqdm import tqdm
from pathlib import Path
from moviepy.editor import *


def transform_worker(BV_number, Origin_video_path, Transformed_video_path):
    Origin_path = os.path.join(Origin_video_path , BV_number + '.mp4')
    Transformed_path = os.path.join(Transformed_video_path, BV_number + '.mp4')

    if os.path.exists(Transformed_path):
        os.remove(Transformed_path)
        # return

    # cap = cv2.VideoCapture(Origin_path)
    # if cap.get(cv2.CAP_PROP_FPS) == 25:
    #     shutil.copyfile(Origin_path, Transformed_path)
    #     return
    clip = VideoFileClip(Origin_path)
    # clip.write_videofile(Transformed_path, verbose=False, fps=25, codec = 'libx264', audio_fps = 16000)
    clip.write_videofile(Transformed_path, verbose=False, fps=25, codec = 'libx264', audio=False)

def run(BV_list, Origin_video_path, Transformed_video_path, worker_num):
    os.makedirs(Transformed_video_path, exist_ok=True)

    p = multiprocessing.Pool(processes=worker_num)
    
    pbar = tqdm(total=len(BV_list), desc='transform video')
    update = lambda *args: pbar.update()
    for BV_number in BV_list:
        p.apply_async(transform_worker, (BV_number, Origin_video_path, Transformed_video_path), callback=update)

    p.close()
    p.join()