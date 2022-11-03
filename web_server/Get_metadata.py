# 用于得到发布数据的信息

import sqlite3
from sys import argv
import os
import hashlib
import random
import pandas as pd
import json

DATABASE = "static/test.db"
skip_spk_txt = './result/skip_spkname.txt'

def get_result():
    # 跳过的说话人
    skip_spk_list = []
    with open(skip_spk_txt) as lines:
        for i in lines:
            skip_spk_list.append(i.strip())

    metadata = []

    db = sqlite3.connect(DATABASE)

    sql_get_data = """
        SELECT * FROM data_view
        """

    c = db.cursor()
    c.execute(sql_get_data)
    dataArray = c.fetchall()

    spk_dict = {}
    compliant_spklist = []
    total_speaker_list = []
    
    
    for index,i in enumerate(dataArray):
        bvid = i[0]
        spkname = i[1]
        duration= i[2]
        username = i[3]
        collectres = i[4]
        processres = i[5]
        annotation = i[6]
        audit = i[7]

        if spkname in skip_spk_list:
            continue

        total_speaker_list.append(spkname)

        # if processres is None:
        #     print(bvid)

        if spkname not in spk_dict:
            spk_dict[spkname] = []
        spk_dict[spkname].append(index)
    
    compliance = {}

    # print("超过2小时：")
    for spkname in spk_dict:
        video_num = 0
        video_length = 0
        genre_set = set()
        
        # 统计当前说话人的情况
        for index in spk_dict[spkname]:
            i = dataArray[index]
            bvid = i[0]
            spkname = i[1]
            duration= i[2]
            username = i[3]
            collectres = i[4]
            processres = i[5]
            annotation = i[6]
            audit = i[7]
            if annotation is None or annotation == "":
                continue

            # 标注时长
            annotation_list = annotation.split()
            video_length += (len(annotation_list) - 1) * 5

            # 视频数量
            video_num += 1

            # 场景数量
            genre_list = collectres.split()[2].split(',')
            for genre_temp in genre_list:
                genre_set.add(genre_temp)

        # 当前说话人采集完毕
        if video_length >= 1.5 * 3600 and video_num >= 10 and len(genre_set) >= 3:
            compliant_spklist.append(spkname)
            if username not in compliance:
                compliance[username] = [spkname]
            else:
                compliance[username].append(spkname)

    spkid_dict = {}

    for index,i in enumerate(dataArray):
        bvid = i[0]
        spkname = i[1]
        duration= i[2]
        username = i[3]
        collectres = i[4]
        processres = i[5]
        annotation = i[6]
        audit = i[7]

        if spkname not in compliant_spklist:
            continue
        
        if spkname not in spkid_dict:
            spkid_dict[spkname] = 'id' + str.zfill(str(len(spkid_dict) + 1), 5)

        data = {}
        data['BVid'] = bvid
        data['Spkid'] = spkid_dict[spkname]
        data['GenreType'] = collectres.split()[2].split(",")
        data['Enroll'] = collectres.split()[3].split(",")

        if annotation is None or annotation == "":
            continue

        if audit is None or audit == "":
            data['Annotation'] = annotation.split()[1:]
        else:
            data['Annotation'] = audit.split()[1:]

        data['Duration'] = duration
        metadata.append(data)

    db.close()
    
    with open('./result/metadata.json','w') as f:
        json.dump(metadata, f, ensure_ascii=False, indent = 2)

    with open('./result/id_name_list.txt','w') as writer:
        for i in spkid_dict:
            writer.write('%s %s\n'%(spkid_dict[i], i))


if __name__ == "__main__":
    get_result()