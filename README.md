该项目为CNC3数据采集网站，用于数据的采集和处理，分为**processing_server**和**web_server**两个部分。其中processing_server用于后台数据处理，web_server用于启动网页。

采集者在安装项目中给出的**videospeed-master.zip**插件后，网页上先进行初步采集，经由后台数据处理后再完成最后的标注。详细过程请参考[CN-Celeb-AV: A Multi-Genre Audio-Visual Dataset for Person Recognition](https://arxiv.org/pdf/2305.16049.pdf)。

该项目用户端使用的方法请于【链接: https://pan.baidu.com/s/1kcPl96Wb8HbUd_WdfaZdXA 提取码: 6t19】下载使用教程查看。

管理端为网址加"/admin"，进入后根据内部提示操作即可。
- 控制台的按钮会向processing_server发送所有无结果采集数据，用于processing_server出问题后的重发。
- 点击“审核”即可开始审核，操作方式与用户端标注一致。
- data_view展示未被用户删除的数据。
- record记录所有操作。
- data展示所有数据（包括已被用户删除的数据），审核情况说明目前审核的情况。

接下来将说明该项目的部署方式

# 准备工作

## processing_server

在部署前，请使用**端口映射**，确保外网访问端口A时，内网可以在端口B上监听到。

将【链接: https://pan.baidu.com/s/1bUkmzw3CWUeFqxZLb3r_jw 提取码: akiq】中的resources放到目录下解压，里面是人脸检测和人脸识别的模型。

## web_server

将**web_server_nginx.conf**文件中的内容复制到本地nginx的配置文件中。

自行创建**log文件夹**以及**static/media文件夹**。



# processing_server

首先根据requirements安装环境

python app.py即可

**如果使用GTX 3090等无法支持CUDA 10.1的显卡，会导致tensorflow和mxnet出现问题，需要替换人脸检测和人脸识别模块。**

### 重要文件说明

```
processing_server
├── DATA                       // 数据目录
│  ├── Origin_video            // 原始视频，视频会被下到这里
│  ├── Transformed_video       // 对原始视频做帧率转换后的结果，统一成25fps
│  ├── Audio_file              // 从原始视频中提取的语音
│  ├── result.txt              // 最终得到的结果会放在该文件中
├── face_recognition           // 人脸识别相关模块
├── resources                  // 人脸识别所用模型
├── static
│  ├── media
│  ├──  ├── image              // 注册人脸所在位置，会从web_server传过来
├── app.py                     // 启动监听，当有web_server的数据传来时执行run.py
├── run.py                     // 负责processing_server的所有流程

```





# web_server

首先根据requirements安装环境

第一次使用需要先运行initdb.py生成数据库

启动：sh run.sh，会自动生成一个gunicorn.pid，这就是网页在后台的进程号

关闭：查看gunicorn.pid的内容，kill掉

### 文件说明

HTML位于templates下

JS位于static/js下

```
web_server
├── templates                  // 存储html文件
│  ├── admin_audit.html        // 管理员审核页面
│  ├── admin_panel.html        // 管理员重发所有无结果采集数据页面
│  ├── admin_spk_audit.html    // 管理员获取审核情况页面
│  ├── anno_index.html         // 用户标注管理页面
│  ├── annotate.html           // 用户标注页面
│  ├── collect.html            // 用户采集页面
│  ├── index.html              // 系统主页
│  ├── login.html              // 登陆页面
│  ├── register.html           // 用户注册页面
├── static
│  ├── test.db                 // 除人脸外所有数据保存位置
│  ├── js                      // 参照html的名字，为对应内核功能的实现
│  ├──  ├── admin_audit.js        
│  ├──  ├── admin_panel.js 
│  ├──  ├── admin_spk_audit.js
│  ├──  ├── anno_index.js
│  ├──  ├── annotate.js
│  ├──  ├── collect.js
│  ├──  ├── index.js
│  ├──  ├── jquery.js
│  ├── media
│  ├──  ├── image              // 注册人脸所在位置

```

