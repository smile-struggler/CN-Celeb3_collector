import sqlite3
from sys import argv
import os
import hashlib
import random
import pandas as pd
import json

DATABASE = "static/test.db"

def get_result():
    db = sqlite3.connect(DATABASE)

    sql_get_data = """
        SELECT * FROM data_view
        """

    c = db.cursor()
    c.execute(sql_get_data)
    dataArray = c.fetchall()

    # 读取已完成的说话人数量
    finish_spk_list = []
    with open('./result/finish_spk.txt') as lines:
        for i in lines:
            finish_spk_list.append(i.strip())


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

        total_speaker_list.append(spkname)
        if spkname in finish_spk_list:
            continue


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
    #     if video_length >= 2 * 3600:
    #         hours = video_length // 3600
    #         minutes = (video_length - hours * 3600) // 60
    #         second = video_length % 60
    #         print([username,spkname,f'{hours}:{minutes}:{second}'])

    # print("超过2小时输出完毕")

    total_num = 0
    compliance_result = {}
    compliance_result['采集人'] = []
    compliance_result['采集完成数量'] = []
    compliance_result['采集说话人列表'] = []


    for i in sorted(compliance.items(), key = lambda i: len(i[1]), reverse = True):
        print(i[0],len(i[1]),i[1])
        total_num += len(i[1])

        compliance_result['采集人'].append(i[0])
        compliance_result['采集完成数量'].append(len(i[1]))
        compliance_result['采集说话人列表'].append(i[1])
    
    compliance_result['采集人'].append('总计')
    compliance_result['采集完成数量'].append(total_num)
    compliance_result['采集说话人列表'].append(compliant_spklist)
    compliance_result = pd.DataFrame(compliance_result)
    compliance_result.to_excel('./result/compliance.xlsx', index=False)    

    
    spk_flag = 0
    for i in finish_spk_list:
        if i not in total_speaker_list:
            if spk_flag == 0:
                spk_flag = 1
                print()
                print("--------------------------------")
            print(i,"有问题！！！！")
    if spk_flag == 1:
        print("--------------------------------")
        print()

    
    print("新增完成目标说话人数量:",total_num)
    print(len(finish_spk_list))
    print("所有完成目标说话人数量:",total_num + len(finish_spk_list))

    BV_audit = {}
    BV_audit['采集人'] = []
    BV_audit['目标说话人'] = []
    BV_audit['BV号'] = []
    BV_audit['场景'] = []
    BV_audit['时长'] = []
    BV_audit['是否审查'] = []
    BV_audit['合格率'] = []

    spk_audit = {}
    spk_audit['采集人'] = []
    spk_audit['目标说话人'] = []
    spk_audit['审核率'] = []
    spk_audit_rate_dict = {}
    spk2user = {}

    for j in sorted(compliance.items(), key = lambda i: len(i[1]), reverse = True):
        username = j[0]
        spk_list = j[1]
        for spkname in spk_list:
            spk2user[spkname] = username
            audit_num = 0
            annotate_num = 0
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

                annotate_num += 1

                BV_audit['采集人'].append(username)
                BV_audit['目标说话人'].append(spkname)
                BV_audit['BV号'].append(bvid)

                if audit is None or audit == "":
                    BV_audit['是否审查'].append("否")
                    BV_audit['合格率'].append("")

                else:
                    audit_num += 1
                    BV_audit['是否审查'].append("是")
                    BV_audit['合格率'].append( (len(audit.split()) - 1) / (len(annotation.split()) - 1) )

                BV_audit['场景'].append(collectres.split()[2])
                temp_time = int(duration)
                minute = temp_time / 60
                second = temp_time % 60
                BV_audit['时长'].append('%dm:%ds'%(minute, second))

            spk_audit_rate_dict[spkname] = audit_num / annotate_num
    
    BV_audit = pd.DataFrame(BV_audit)
    BV_audit.to_excel('./result/BV_audit.xlsx', index=False)    


    # 采集人 目标说话人 审核率
    spk_audit_rate = dict(sorted(spk_audit_rate_dict.items(), key = lambda i: i[1]))
    for j in sorted(compliance.items(), key = lambda i: len(i[1]), reverse = True):
        username = j[0]
        for spkname in spk_audit_rate:
            if spk2user[spkname] == username:
                spk_audit['采集人'].append(username)
                spk_audit['目标说话人'].append(spkname)
                spk_audit['审核率'].append(round(spk_audit_rate[spkname],2))
                
    spk_audit_pd = pd.DataFrame(spk_audit)
    spk_audit_pd.to_excel('./result/spk_audit.xlsx', index=False)  
        

        

                

    # with open("./result/compliance.txt", 'w') as writer:


    # for i in dataArray:
    #     user_list.append(i[0])

    # 采集到的视频标注信息
    
        
    # # 创建user表，存储用户信息
    # sql_creat_user_table = """
    #     CREATE TABLE if not exists user(
    #         USERID    INTEGER PRIMARY KEY,  --user唯一id
    #         USERNAME  TEXT,             --用户账号 
    #         PASSWORD  TEXT,             --用户密码
    #         TELPHONE  TEXT              --手机号码
    #         );
    #     """
    # print(sql_creat_user_table)
    # db.execute(sql_creat_user_table)
    # db.commit()
    # # 创建data表，储存用的所有操作信息
    # sql_creat_data_table = """
    #     CREATE TABLE if not exists data(
    #         BVID       TEXT PRIMARY KEY, --data以BV号为唯一id以禁止重复
    #         SPKNAME    TEXT,                --目标说话人名字
    #         DURATION   INTEGER,             --此视频的有效时长，以段的数量进行存储
    #         USERNAME   TEXT,                --负责人名字
    #         COLLECTRES TEXT,                --采集结果
    #         PROCESSRES TEXT,                --预处理结果
    #         ANNOTATION TEXT                 --标注结果
    #         );
    #     """
    # print(sql_creat_data_table)
    # db.execute(sql_creat_data_table)
    # db.commit()
    
    # # 创建record表，储存用的所有操作信息
    # sql_creat_record_table = """
    #     CREATE TABLE if not exists record(
    #         RECORDID   INTEGER PRIMARY KEY,  --record唯一id
    #         CONTENT    TEXT,                 --record内容
    #         UPDATETIME DATETIME NULL DEFAULT CURRENT_TIMESTAMP -- 创建时间
    #         );
    #     """
    # print(sql_creat_record_table)
    # db.execute(sql_creat_record_table)
    # db.commit()
    # db.execute(
    #     "INSERT INTO user (USERNAME, PASSWORD) VALUES('csltroot', 'cslt@tsinghua.1303')"
    # )
    # db.execute(
    #     "INSERT INTO user (USERNAME, PASSWORD) VALUES('cchen', 'chen')"
    # )
    # db.commit()
    db.close()
    return [spk_audit, total_num, total_num + len(finish_spk_list)]

if __name__ == "__main__":
    get_result()