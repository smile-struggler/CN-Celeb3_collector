import subprocess
import os
import multiprocessing
from tqdm import tqdm
from pathlib import Path
import time
import shutil



def download_worker(BV_number, url, save_dir):
    if os.path.exists(os.path.join(save_dir, f"{BV_number}.mp4")):
        os.remove(os.path.join(save_dir, f"{BV_number}.mp4"))

    if os.path.exists(os.path.join(save_dir, f"{BV_number}.flv")):
        os.remove(os.path.join(save_dir, f"{BV_number}.flv"))

    print(os.path.join(save_dir, f"{BV_number}.mp4"))
    cmd = f'you-get --format=dash-flv360 "{url}" -o "{save_dir}" -O "{BV_number}"'
    res = subprocess.call(cmd, shell=True)
    if res != 0:
        cmd = f'you-get --format=flv360 "{url}" -o "{save_dir}" -O "{BV_number}"'
        res = subprocess.call(cmd, shell=True)
    
    if not os.path.exists(os.path.join(save_dir, f"{BV_number}.mp4")) and os.path.exists(os.path.join(save_dir, f"{BV_number}.flv")):
        cmd = 'ffmpeg -v error -i %s -y -vcodec copy -acodec copy %s' % (os.path.join(save_dir, f"{BV_number}.flv"), os.path.join(save_dir, f"{BV_number}.mp4"))
        res = subprocess.call(cmd, shell=True)

    if not os.path.exists(os.path.join(save_dir, f"{BV_number}.mp4")):
        return [BV_number]
    return []

def run(BV_list, save_dir, worker_num):
    os.makedirs(save_dir, exist_ok=True)
    bv_set = []
    result = []

    p = multiprocessing.Pool(processes=worker_num)
    
    pbar = tqdm(total=len(BV_list), desc='download')
    update = lambda *args: pbar.update()
    for BV_number in BV_list:
        url = 'https://www.bilibili.com/video/%s' % BV_number
        result.append(p.apply_async(download_worker, (BV_number, url, save_dir), callback=update))
        
    p.close()
    p.join()