import sqlite3
from sys import argv
import os
import hashlib
import random
import json

DATABASE = "static/test.db"


def creat_table():
    db = sqlite3.connect(DATABASE)
    # 创建user表，存储用户信息
    sql_creat_user_table = """
        CREATE TABLE if not exists user(
            USERID    INTEGER PRIMARY KEY,  --user唯一id
            USERNAME  TEXT,                 --用户账号 
            PASSWORD  TEXT,                 --用户密码
            TELPHONE  TEXT                  --手机号码
            );
        """
    print(sql_creat_user_table)
    db.execute(sql_creat_user_table)
    db.commit()
    # 创建data表，储存用的所有操作信息
    sql_creat_data_table = """
        CREATE TABLE if not exists data(
            BVID       TEXT PRIMARY KEY, --data以BV号为唯一id以禁止重复
            SPKNAME    TEXT,             --目标说话人名字
            DURATION   INTEGER,          --此视频的有效时长，以段的数量进行存储
            USERNAME   TEXT,             --负责人名字
            COLLECTRES TEXT,             --采集结果
            PROCESSRES TEXT,             --预处理结果
            ANNOTATION TEXT,             --标注结果
            AUDIT      TEXT,             --审核结果
            DELMARK    TEXT             --删除结果
            );
        """
    print(sql_creat_data_table)
    db.execute(sql_creat_data_table)
    db.commit()

    # 创建record表，储存用的所有操作信息
    sql_creat_record_table = """
        CREATE TABLE if not exists record(
            RECORDID   INTEGER PRIMARY KEY,  --record唯一id
            CONTENT    TEXT,                 --record内容
            UPDATETIME DATETIME NULL DEFAULT CURRENT_TIMESTAMP -- 创建时间
            );
        """
    print(sql_creat_record_table)
    db.execute(sql_creat_record_table)
    db.commit()

    # 创建未删除数据的视图，直接展示未删除的信息
    sql_add_data_view = """
       CREATE VIEW data_view AS SELECT * FROM data where DELMARK is NULL;
        """
    print(sql_add_data_view)
    db.execute(sql_add_data_view)
    db.commit()
    
    db.execute("INSERT INTO user (USERNAME, PASSWORD) VALUES('username', 'password')")
    db.commit()
    db.close()


if __name__ == "__main__":
    creat_table()