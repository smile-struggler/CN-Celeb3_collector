import json
from flask import Flask, render_template, request
from flask.helpers import url_for
import random
import re
import time
import datetime
import os
import requests
import json

from multiprocessing import Queue
from multiprocessing import Process
import multiprocessing
import subprocess

os.environ["CUDA_VISIBLE_DEVICES"] = '3'
PORT = 11111
DOMAIN_NAME = 'http://collect.cslt.org/'
Result_path = './DATA/result.txt'

def process_data(q):

    while(True):
        if(q.empty() == False):
            task_list = []
            # while(q.empty() == False):
            task_list.append(q.get())
            cmd = 'python run.py --BV_list "%s"'%(' '.join(task_list))
            if subprocess.call(cmd, shell=True):
                print("Running error, please check!")
                # exit()
            else:
                with open(Result_path) as lines:
                    for ans in lines:
                        ans = ans.strip()
                        result = json.dumps({'processres': ans, 'bvid': ans.split()[0]})
                        requests.post(f'{DOMAIN_NAME}process/video/meta', data=result)

DATABASE = 'static/test.db'

app = Flask(__name__)
app.static_folder = 'static/'

"""
POST Route
"""
# upload methods
@app.route('/upload/information', methods=['POST'])
def upload_information():
    data = request.get_data().decode('UTF-8')
    q.put(data)
    print(q.qsize())
    return 'success'

@app.route('/upload/image', methods=['POST'])
def post_image_file():
    file = request.files['file']
    file.save(f"./static/media/image/{file.filename}")
    return 'accept image file'
    
"""
Page Route
"""
# index page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template(
        "index.html",
    )

if __name__ == '__main__':
    try:
        multiprocessing.set_start_method('spawn', force=True)
        q = Queue()
        thread = Process(target = process_data,args=(q,))
        thread.start()
        app.run(host='0.0.0.0', port=PORT)
    
    except:
        thread.terminate()