import json
import requests
from flask import Flask, render_template, request, g, redirect, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib import sqla
from flask_basicauth import BasicAuth
from flask_apscheduler import APScheduler
from werkzeug.exceptions import HTTPException, Response
import sqlite3
import random
import re
import time
import datetime
import os
import Get_result

DATABASE = 'static/test.db'
PROCESS_SERVER = 'http://127.0.0.1:11111'
PORT = 22222

app = Flask(__name__)
# for session / cookie
app.secret_key = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
# 中文显示
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
# admin账号密码
app.config['BASIC_AUTH_USERNAME'] = 'username'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
# 使用BasicAuth做后台的权限验证
basic_auth = BasicAuth(app)


# 定时任务
def scheduler():
    with app.app_context():
        num = 0
        now = datetime.date.today()
        today = now.strftime('%y%m%d')
        now = datetime.datetime.now()
        if os.path.exists(f'./bak/{today}') is False:
            conn = sqlite3.connect(DATABASE)
            with open(f'./bak/{today}','w') as f:
                f.write("")
            with open(f'./bak/{today}_{os.getpid()}.bak','wb') as f:
                for line in conn.iterdump():
                    data = line + '\n'
                    data = data.encode("utf-8")
                    f.write(data)
            conn.close()

class APSchedulerJobConfig(object):
    JOBS = [{
        'id': 'backup',
        'func': scheduler,
        'args': None,
        'trigger': {
            'type': 'cron',  # cron类型
            'day_of_week': "0-6",  # 每周一到周日
            'hour': '3',  # 的第8小时
            'minute': '0'  # 的第0分钟
        }
    }]

    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_ECHO = True


# 设置定时任务
app.config.from_object(APSchedulerJobConfig())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


class AuthException(HTTPException):

    def __init__(self, message):
        super().__init__(
            message,
            Response("You could not be authenticated. Please refresh the page.", 401,
                     {'WWW-Authenticate': 'Basic realm="Login Required"'}))


# 设置数据库主页显示


class ModelView(sqla.ModelView):
    column_display_pk = True
    can_set_page_size = True
    can_export = True

    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class UserModelView(ModelView):
    column_display_pk = True
    column_filters = ("USERID", "USERNAME", "TELPHONE")


class DataModelView(ModelView):
    column_display_pk = True
    column_filters = ("BVID", "SPKNAME", "USERNAME", "DURATION", "COLLECTRES", "ANNOTATION", "PROCESSRES", "AUDIT", "DELMARK")


class RecordModelView(ModelView):
    column_display_pk = True
    column_filters = ("RECORDID", "CONTENT", "UPDATETIME")

class DataViewModelView(ModelView):
    column_display_pk = True
    column_filters = ("BVID", "SPKNAME", "USERNAME", "DURATION", "COLLECTRES", "ANNOTATION", "PROCESSRES", "AUDIT", "DELMARK")


admin = Admin(app, name=u'后台管理系统')


class PanelView(BaseView):

    @expose('/')
    @basic_auth.required
    def index_panel(self):
        self.extra_js = [
            url_for("static", filename="js/admin_panel.js"),
            url_for("static", filename="js/jquery.js"),
        ]
        return self.render('admin_panel.html')


class AuditView(BaseView):

    @expose('/')
    @basic_auth.required
    def index_audit(self):
        self.extra_js = [
            url_for("static", filename="js/admin_audit.js"),
            url_for("static", filename="js/jquery.js"),
        ]
        return self.render('admin_audit.html')

class Spk_auditView(BaseView):

    @expose('/')
    @basic_auth.required
    def index_audit(self):
        self.extra_js = [
            url_for("static", filename="js/admin_spk_audit.js"),
            url_for("static", filename="js/jquery.js"),
        ]
        return self.render('admin_spk_audit.html')

admin.add_view(PanelView(name='控制台'))
admin.add_view(AuditView(name='审核'))

# 设置数据库

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, DATABASE)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)


class user(db.Model):
    USERID = db.Column(db.Integer, primary_key=True)
    USERNAME = db.Column(db.Text)
    PASSWORD = db.Column(db.Text)
    TELPHONE = db.Column(db.Text)


class data(db.Model):
    BVID = db.Column(db.Text, primary_key=True)
    SPKNAME = db.Column(db.Text)
    DURATION = db.Column(db.Integer)  # duration in seconds, 10~14s -> 10s
    USERNAME = db.Column(db.Text)
    COLLECTRES = db.Column(db.Text)
    PROCESSRES = db.Column(db.Text)
    ANNOTATION = db.Column(db.Text)
    AUDIT = db.Column(db.Text)
    DELMARK = db.Column(db.Text)



class record(db.Model):
    RECORDID = db.Column(db.Integer, primary_key=True)
    CONTENT = db.Column(db.Text)
    UPDATETIME = db.Column(db.DateTime)

class data_view(db.Model):
    BVID = db.Column(db.Text, primary_key=True)
    SPKNAME = db.Column(db.Text)
    DURATION = db.Column(db.Integer)  # duration in seconds, 10~14s -> 10s
    USERNAME = db.Column(db.Text)
    COLLECTRES = db.Column(db.Text)
    PROCESSRES = db.Column(db.Text)
    ANNOTATION = db.Column(db.Text)
    AUDIT = db.Column(db.Text)
    DELMARK = db.Column(db.Text)


# 添加数据表到后台主页
admin.add_view(UserModelView(user, db.session))
admin.add_view(DataViewModelView(data_view, db.session))
admin.add_view(RecordModelView(record, db.session))
admin.add_view(DataModelView(data, db.session))
admin.add_view(Spk_auditView(name='审核情况'))

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)
    print("datebase connected")


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
        print("datebase closed")

"""#########################################################
login & register
"""#########################################################


# 正则判断是否由 0~9, a~z, A~Z, _ 组成
def validStr(s):
    return re.match("^[a-z0-9A-Z_]{2,10}$", s)


# login
# GET method: get html
# POST method: send username and password to verify
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        # 不正确的输入格式
        if not (validStr(userid) and validStr(password)):
            return render_template(
                'login.html',
                message='账户和密码由 2~10个 大小写英文字母、数字、下划线组成',
            )
        # 查询数据库内用户表
        c = g.db.cursor()
        c.execute("SELECT * FROM user WHERE USERNAME=? AND PASSWORD=?", (userid, password))
        dataArray = c.fetchall()
        if len(dataArray) == 1:
            # 用户注册且密码正确
            session['username'] = userid
            return redirect('/')
        else:
            # 查询登陆失败原因
            c.execute("SELECT * FROM user WHERE USERNAME=\'" + userid + "\';")
            if len(c.fetchall()) == 1:
                # 有此用户
                return render_template('login.html', message='密码错误')
            else:
                # 无此用户
                return render_template('login.html', message='此用户尚未注册')


# reginster
# GET method: get html
# POST method: send username and password to verify
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        print("register")
        userid = request.form['userid']
        password = request.form['password']
        password2 = request.form['password2']
        telphone = request.form['telphone']
        if password != password2:
            return render_template('register.html', message='两次密码不一致')
        if len(userid) == 0 or len(password) == 0:
            return render_template('register.html', message='请填写用户名和密码')
        if not (validStr(userid) and validStr(password)):
            return render_template('register.html', message='账户和密码由 2~10个 大小写英文字母、数字、下划线组成')
        session['username'] = userid
        # 尝试插入用户表
        c = g.db.cursor()
        # 查询用户名是否存在
        c.execute("SELECT * FROM user WHERE USERNAME=\'" + userid + "\';")
        g.db.commit()
        dataArray = c.fetchall()
        print(json.dumps(dataArray))
        if (len(dataArray) == 0):
            # 新用户名，插入用户表
            c.execute("INSERT INTO user (USERNAME,PASSWORD,TELPHONE) VALUES (?,?,?)", (userid, password, telphone))
            g.db.commit()
            session['username'] = userid
            return redirect('/')
        else:
            # 用户名重复
            return render_template('register.html', message='用户名重复，注册失败')
"""#########################################################
Get Information
"""#########################################################


@app.route('/collect_video/check_image_upload', methods=['GET'])
def check_image_upload():
    bvid = request.values.get('bvid')
    if not os.path.exists(f'static/media/image/{bvid}.png'):
        return 'fail'
    return 'success'


def sort_by(ret_spk, spk, target, reverse=False):
    ret_spk_collect_list = sorted(ret_spk.items(), key=lambda d: d[1][target], reverse=reverse)
    # print(ret_spk_collect_list)
    ret_spk_collect = {}
    for r in ret_spk_collect_list:
        ret_spk_collect[r[0]] = r[1]
    for s in spk:
        ret_spk_collect[s] = {
            'video_count': ret_spk_collect[s]['video_count'],
            'allow_annot': ret_spk_collect[s]['allow_annot'],
            'todo_count': ret_spk_collect[s]['todo_count'],
            'annotated': ret_spk_collect[s]['annotated'],
            'total_dur': str(datetime.timedelta(seconds=ret_spk_collect[s]['total_dur'])),
            'todo_dur': str(datetime.timedelta(seconds=ret_spk_collect[s]['todo_dur'])),
            'annotated_dur': str(datetime.timedelta(seconds=ret_spk_collect[s]['annotated_dur'])),
            'genre_list': ret_spk_collect[s]['genre_list'],
            'genre_num': ret_spk_collect[s]['genre_num'],
        }
    return ret_spk_collect


@app.route('/userinfo', methods=['GET'])
def get_user_info():
    print('get user info')
    username = request.values.get('username')
    c = g.db.cursor()
    c.execute(f"SELECT BVID,SPKNAME,DURATION,PROCESSRES,ANNOTATION,COLLECTRES FROM data_view WHERE USERNAME='{username}';")
    result = c.fetchall()
    ret = {}
    spk = [res[1] for res in result]
    spk = list(set(spk))
    ret_spk = {}
    for s in spk:
        ret_spk[s] = {
            'video_count': 0,
            'allow_annot': 0,
            'todo_count': 0,
            'annotated': 0,
            'total_dur': 0,
            'todo_dur': 0,
            'annotated_dur': 0,
            'genre_list': [],
            'genre_num': 0,
        }
    # 整体统计
    ret['video_count'] = len(result)
    ret['allow_annot'] = sum([res[3] is not None and res[3] != "" for res in result])
    ret['todo_count'] = sum([res[4] is None or res[4] == "" for res in result])
    ret['annotated'] = sum([res[4] is not None and res[4] != "" for res in result])
    ret['total_dur'] = str(datetime.timedelta(seconds=sum([res[2] for res in result])))
    todo_dur = 0
    annotated_dur = 0
    for res in result:
        bvid = res[0]
        spkname = res[1]
        dur = res[2]

        genre_text = res[5].split()[2].split(',')
        for genre_temp in genre_text:
            ret_spk[spkname]['genre_list'].append(genre_temp)
        ret_spk[spkname]['genre_num'] = len(set(ret_spk[spkname]['genre_list']))

        ret_spk[spkname]['video_count'] += 1
        ret_spk[spkname]['total_dur'] += dur
        if res[4] is None or res[4] == "":
            todo_dur += dur
            ret_spk[spkname]['todo_count'] += 1
            ret_spk[spkname]['todo_dur'] += dur
        else:
            annotated_dur += 5 * (len(res[4].split(' ')) - 1)
            ret_spk[spkname]['annotated'] += 1
            ret_spk[spkname]['annotated_dur'] += 5 * (len(res[4].split(' ')) - 1)
    ret['todo_dur'] = str(datetime.timedelta(seconds=todo_dur))
    ret['annotated_dur'] = str(datetime.timedelta(seconds=annotated_dur))

    ret['spk_collect'] = sort_by(ret_spk, spk, target='total_dur', reverse=False)
    ret['spk_todo'] = sort_by(ret_spk, spk, target='todo_dur', reverse=True)
    ret['spk_annotate'] = sort_by(ret_spk, spk, target='annotated_dur', reverse=False)
    ret['spk_genre'] = sort_by(ret_spk, spk, target='genre_num', reverse=False)

    print(ret)
    return json.dumps(ret)


@app.route('/annotate/get_video_list', methods=['GET'])
def get_video_list():
    print('get_video_list')
    username = request.values.get('username')
    c = g.db.cursor()
    c.execute(f"SELECT BVID,SPKNAME,PROCESSRES,ANNOTATION FROM data_view WHERE USERNAME='{username}';")
    result = c.fetchall()
    print(result)
    ret = []

    ret_temp = {}
    ret_temp[0] = []
    ret_temp[1] = []
    ret_temp[2] = []
    for res in result:
        print(res)
        bvid = res[0]
        spkname = res[1]
        process_res = res[2]
        annotation = res[3]
        ret_id = 0
        if process_res is None or process_res == "":
            status = '暂时无法标注'
            ret_id = 1
        else:
            if annotation is None or annotation == "":
                status = '需要标注'
                ret_id = 0
            else:
                status = '已标注'
                ret_id = 2
        ret_temp[ret_id].append({
            'bvid': bvid,
            'spkname': spkname,
            'status': status,
        })
    for i in range(3):
        for j in ret_temp[i]:
            ret.append(j)
    print(ret)
    return json.dumps(ret)


@app.route('/collect_video/check_bvid', methods=['GET'])
def check_bvid():
    username = request.values.get('username')
    bvid = request.values.get('bvid')
    print(bvid, username)
    c = g.db.cursor()
    c.execute(f"SELECT BVID, USERNAME FROM data_view WHERE BVID='{bvid}';")
    result = c.fetchall()
    print(result)
    if len(result) == 0:
        return 'ok'
    if result[0][1] == username:
        return 'allow'
    return 'forbid'


@app.route('/collect_video/check_spk', methods=['GET'])
def check_spk():
    username = request.values.get('username')
    spk = request.values.get('spk')
    print(spk, username)
    c = g.db.cursor()
    c.execute(f"SELECT SPKNAME, USERNAME FROM data_view WHERE SPKNAME='{spk}';")
    result = c.fetchall()
    print(result)
    if len(result) == 0:
        return 'ok'
    if result[0][1] == username:
        return 'allow'
    return 'forbid'


@app.route('/annotate/video/get_process_res', methods=['GET'])
def get_process_res():
    username = request.values.get('username')
    bvid = request.values.get('bvid')
    print(username, bvid)
    c = g.db.cursor()
    c.execute(f"SELECT PROCESSRES FROM data_view WHERE BVID='{bvid}'")
    result = c.fetchall()
    if len(result) == 0:
        return json.dumps({"status": 'error'})
    return json.dumps({"status": 'success', 'res': result[0]})


@app.route('/annotate/video/get_annotation_by_bvid', methods=['GET'])
def get_annotation_by_bvid():
    bvid = request.values.get('bvid')
    print(bvid)
    c = g.db.cursor()
    c.execute(f"SELECT ANNOTATION FROM data_view WHERE BVID='{bvid}'")
    result = c.fetchall()
    if len(result) == 0:
        return json.dumps({"status": 'error'})
    return json.dumps({"status": 'success', 'res': result[0]})


@app.route('/annotate/video/get_process_by_bvid', methods=['GET'])
def get_process_by_bvid():
    bvid = request.values.get('bvid')
    print(bvid)
    c = g.db.cursor()
    c.execute(f"SELECT PROCESSRES FROM data_view WHERE BVID='{bvid}'")
    result = c.fetchall()
    if len(result) == 0:
        return json.dumps({"status": 'error'})
    return json.dumps({"status": 'success', 'res': result[0]})


@app.route('/annotate/video/get_collectres_by_bvid', methods=['GET'])
def get_collectres_by_bvid():
    bvid = request.values.get('bvid')
    print(bvid)
    c = g.db.cursor()
    c.execute(f"SELECT COLLECTRES FROM data_view WHERE BVID='{bvid}'")
    result = c.fetchall()
    if len(result) == 0:
        return json.dumps({"status": 'error'})
    return json.dumps({"status": 'success', 'res': result[0]})

@app.route('/annotate/video/get_duration_by_bvid', methods=['GET'])
def get_duration_by_bvid():
    bvid = request.values.get('bvid')
    print(bvid)
    c = g.db.cursor()
    c.execute(f"SELECT DURATION FROM data_view WHERE BVID='{bvid}'")
    result = c.fetchall()
    if len(result) == 0:
        return json.dumps({"status": 'error'})
    return json.dumps({"status": 'success', 'res': result[0]})


@app.route('/annotate/video/get_users_by_bvid', methods=['GET'])
def get_users_by_bvid():
    bvid = request.values.get('bvid')
    print(bvid)
    c = g.db.cursor()
    c.execute(f"SELECT USERNAME FROM data_view WHERE BVID='{bvid}'")
    result = c.fetchall()
    if len(result) == 0:
        return json.dumps({"status": 'error'})
    return json.dumps({"status": 'success', 'res': result[0]})

@app.route('/admin/get_result', methods=['GET'])
def get_result():
    ans = Get_result.get_result()
    return json.dumps({'ans': json.dumps(ans[0]),'new_spk_num':ans[1],'total_spk_num':ans[2]})

"""#########################################################
Upload Function
"""#########################################################


@app.route('/collect_video/meta', methods=['POST'])
def upload_collect_meta():
    data = request.get_data().decode("UTF-8")
    meta = json.loads(data)
    print(data, meta)
    username = meta['username']
    bvid = meta['bv']
    genre = meta['genre']
    seconds = meta['second']
    spk = meta['speaker']
    txt = meta['txt']
    dur = int(meta['dur'])
    c = g.db.cursor()
    c.execute(f"SELECT BVID, USERNAME FROM data_view WHERE BVID='{bvid}';")
    result = c.fetchall()
    txt = txt.replace("Live Broadcast", "Live_Broadcast")
    if len(result) != 0:
        # 有人上传过
        if result[0][1] == username:
            # 本人曾上传过，可以覆盖更新data表
            c.execute(f"SELECT ANNOTATION FROM data_view WHERE BVID='{bvid}';")
            annotation_result = c.fetchall()
            
            # 如果还没有标注
            if annotation_result[0][0] is None or annotation_result[0][0] == "":
                c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'COLLECT|{data}');")
                g.db.commit()
                c.execute(
                    f"UPDATE data set BVID='{bvid}', SPKNAME='{spk}', DURATION='{dur}', COLLECTRES='{txt}', PROCESSRES=null, ANNOTATION=null, AUDIT=null, DELMARK=null WHERE BVID='{bvid}';"
                )
                g.db.commit()
                requests.post(f'{PROCESS_SERVER}/upload/information', data=txt.encode('utf-8'))
                return "success"

            # 如果已经完成标注
            else:
                c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'MODIFY|{data}');")
                g.db.commit()
                c.execute(
                    f"UPDATE data set SPKNAME='{spk}', DURATION='{dur}', COLLECTRES='{txt}' WHERE BVID='{bvid}';"
                )
                g.db.commit()
                return "success"
            

    else:
        # 无人上传过
        # 查看是否是被删除的
        c.execute(f"SELECT BVID FROM data WHERE BVID='{bvid}' AND DELMARK = 'YES';")
        result = c.fetchall()
        if len(result) != 0:
            # 有人删除过
            c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'COLLECT|{data}');")
            g.db.commit()
            c.execute(
                f"UPDATE data set BVID='{bvid}', SPKNAME='{spk}', DURATION='{dur}',USERNAME='{username}', COLLECTRES='{txt}', PROCESSRES=null, ANNOTATION=null, AUDIT=null, DELMARK=null WHERE BVID='{bvid}';"
            )
            g.db.commit()
        
        # 没人删除过
        else:
            c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'COLLECT|{data}');")
            g.db.commit()
            c.execute(
                f"INSERT INTO data (BVID, SPKNAME, DURATION, USERNAME, COLLECTRES) VALUES (?,?,?,?,?);",
                (bvid, spk, dur, username, txt),
            )
            g.db.commit()
        requests.post(f'{PROCESS_SERVER}/upload/information', data=txt.encode('utf-8'))
        return "success"
    return "fail"


@app.route('/collect_video/image', methods=['POST'])
def upload_collect_image():
    username = session['username']
    file = request.files['filepond']
    bvid = file.filename.split('.png')[0]
    c = g.db.cursor()
    c.execute(f"SELECT BVID, USERNAME FROM data_view WHERE BVID='{bvid}';")
    result = c.fetchall()
    allow = False
    if len(result) != 0:
        if result[0][1] == username:
            allow = True  # 自己上传过允许更新
    else:
        allow = True  # 没人上传过允许上传
    if allow:
        print(file.filename)
        file.save(f"./static/media/image/{file.filename}")
        to_server_file = {
            'file': open(f"./static/media/image/{file.filename}", 'rb'),
            'filename': file.filename,
        }
        requests.post(f'{PROCESS_SERVER}/upload/image', files=to_server_file)
        return "accept image file"
    return 'reject image file'


@app.route('/process/video/meta', methods=['POST'])
def upload_processres_meta():
    data = request.get_data().decode("UTF-8")
    meta = json.loads(data)
    processres = meta['processres']
    bvid = meta['bvid']
    c = g.db.cursor()
    c.execute(f"UPDATE data set PROCESSRES='{processres}' WHERE BVID='{bvid}';")
    c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'PROCESS|{data}');")
    g.db.commit()
    return 'success'


@app.route('/annotate/video/meta', methods=['POST'])
def upload_annotation_meta():
    data = request.get_data().decode("UTF-8")
    meta = json.loads(data)
    print(data, meta)
    annotation = meta['annotation']
    bvid = meta['bvid']
    c = g.db.cursor()
    c.execute(f"UPDATE data set ANNOTATION='{annotation}' WHERE BVID='{bvid}';")
    c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'ANNOTATION|{data}');")
    g.db.commit()
    return redirect('/annotate')


@app.route('/annotate/video/audit', methods=['POST'])
def upload_audit_meta():
    data = request.get_data().decode("UTF-8")
    meta = json.loads(data)
    print(data, meta)
    audit = meta['audit']
    bvid = meta['bvid']
    c = g.db.cursor()
    c.execute(f"UPDATE data set AUDIT='{audit}' WHERE BVID='{bvid}';")
    c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'AUDIT|{data}');")
    g.db.commit()
    return 'success'


@app.route('/audit/check_bvid', methods=['GET'])
def audit_check_bvid():
    bvid = request.values.get('bvid')
    print(bvid)
    c = g.db.cursor()
    c.execute(f"SELECT CONTENT FROM record;")
    result = c.fetchall()
    for res in result:
        record_type, content = res[0].split('|')
        if record_type == 'AUDIT':
            data = json.loads(content)
            if bvid == data['bvid']:
                return 'forbid'
    return 'ok'


@app.route('/resend_do', methods=['POST'])
def resend():
    c = g.db.cursor()
    c.execute(f'SELECT * FROM data_view WHERE PROCESSRES is NULL OR PROCESSRES = ""')
    result = c.fetchall()
    print(result)
    for res in result:
        fn = f'{res[0]}.png'
        if not os.path.exists(f'static/media/image/{fn}'):
            print(f'skipping {fn} because file not exists')
            continue
        files = {'file': open(f'static/media/image/{fn}', 'rb'), 'filename': fn}
        data = {'txt': res[4]}
        r = requests.post(f'{PROCESS_SERVER}/upload/image', files=files)
        r = requests.post(f'{PROCESS_SERVER}/upload/information', data=res[4].encode('utf-8'))
    return 'success'


@app.route('/clear_processres', methods=['POST'])
def clear_processres():
    c = g.db.cursor()
    c.execute(f"UPDATE data SET PROCESSRES=null")
    g.db.commit()
    return 'success'


"""#########################################################
Delete Function
"""#########################################################


@app.route('/delete/video/bv', methods=['POST'])
def delete_video_bv():
    data = request.get_data().decode("UTF-8")
    meta = json.loads(data)
    bvid = meta['bvid']
    username = meta['username']
    c = g.db.cursor()
    c.execute(f"UPDATE data SET DELMARK='YES' WHERE BVID='{bvid}';")
    c.execute(f"INSERT INTO record (RECORDID, CONTENT) VALUES (NULL, 'DELMARK|{username} {bvid}');")
    g.db.commit()
    return 'success'

"""#########################################################
Page Route
"""#########################################################


# logout
@app.route('/logout', methods=['GET', 'POST'])
def logout_route():
    session = {}
    return render_template("login.html")


# collect
@app.route('/collect', methods=['GET', 'POST'])
def collect_route():
    return render_template("collect.html", username=session['username'])

# collect modify
@app.route('/collect_modify', methods=['GET', 'POST'])
def collect_modify_route():
    username = request.values.get('username')
    bv = request.values.get('bv')
    return render_template("collect.html", username=username, bv=bv)

# annotate index
@app.route('/annotate', methods=['GET', 'POST'])
def annotate_index_route():
    return render_template("anno_index.html", username=session['username'])


# annotate
@app.route('/annotate_video', methods=['GET', 'POST'])
def annotate_video_route():
    username = request.values.get('username')
    bvid = request.values.get('bvid')
    return render_template("annotate.html", username=username, bvid=bvid)


# index
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    return render_template(
        "index.html",
        username=session['username'],
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PORT, debug=True)
