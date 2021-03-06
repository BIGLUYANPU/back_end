from flask import Flask, request, session, render_template
from flask_cors import CORS
from flask_mail import Mail
from werkzeug.utils import secure_filename
from tools.tools import encryption, send_mail, reset1, reset2
from datetime import timedelta, datetime
from dateutil.parser import parse
from dateutil import tz
import logging
import os
import redis
import random
from db.db_sql import *
from .parser import *
import json
import pickle

# 日志的配置
log_handle = logging.FileHandler('my.log', encoding='utf-8')
log_handle.setLevel(logging.INFO)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
log_handle.setFormatter(logging_format)
# redis的配置
redis_con = redis.Redis(host="127.0.0.1", port=6379)
# 只是更改了静态链接，static_floder 并没有改变
# 注意静态文件还是放到了static里 但是url不用加statc了
app = Flask(__name__, static_url_path="")
app.logger.addHandler(log_handle)
# 邮箱的配置
app.config.update(dict(
    MAIL_SERVER='smtp.163.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='lyp_user@163.com',
    MAIL_PASSWORD='luyanpu1996729',
    MAIL_DEFAULT_SENDER='lyp_user@163.com'
))
# mail对应APP实例
mail = Mail(app)
# 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除
app.config['SECRET_KEY'] = os.urandom(6)
# 设置session的保存时间。
# 解决跨域和cookie
CORS(app, supports_credentials=True)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/account_ver', methods=['POST'])
def account_verification():
    """
    注册页面用户名唯一性的验证
    :return:
    """
    try:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7)
        data_json = request.get_json()
        account = data_json.get('account')
        if account is None:
            return json.dumps({'status': 400, 'args': 0}, ensure_ascii=False)
        user_account = select_user_account(account)
        if user_account is None:
            app.logger.info(account + '用户名可以使用')
            session['regist_account'] = account
            return json.dumps({'status': 200, 'message': '用户名可以使用', 'args': 1}, ensure_ascii=False)
        else:
            app.logger.info(account + '用户名不可以使用')
            return json.dumps({'status': 200, 'message': '用户名重复', 'args': 0}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/mail', methods=['GET'])
def to_user_send_mail():
    """
    注册,邮件发送验证码
    :return:
    """
    try:
        # 获取用户名
        usermail = session.get('regist_account')
        if usermail is None:
            app.logger.info('缺失account参数')
            return json.dumps({'status': 200, 'message': '参数错误', 'args': 0}, ensure_ascii=False)
        # 获取验证码
        code = ''
        for i in range(0, 4):
            code = code + str(random.randrange(0, 10))
        # 邮件的标题
        title = "注册激活"
        # 邮件的内容
        text = '<p>尊敬的' + usermail + '您的验证码为:' + code + '(有效期为5分钟)' + '</p>'
        # 发送邮件
        send_mail(mail, usermail, title, text)
        # 二进制形式存储key value
        redis_con.set(usermail + 'code', code)
        # 过期时间5分钟
        redis_con.expire(usermail + 'code', 300)
        app.logger.info('邮件发送成功')
        return json.dumps({'status': 200, 'message': '验证码发送成功', 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 200, 'message': '验证码发送失败', 'args': 0}, ensure_ascii=False)


@app.route('/regist', methods=['POST'])
def user_register():
    """
    用户注册
    :return:
    """
    try:
        data_json = request.get_json()
        # 获取用户名
        usermail = session.get('regist_account')
        # 获取密码
        password = data_json.get('passwd')
        # 获取昵称
        name = data_json.get('name')
        # 验证码
        usercode = data_json.get('code')
        if usermail is None or password is None or name is None or usercode is None:
            return json.dumps({'status': 400, 'args': 0, 'message': '密码或账号不能为空', }, ensure_ascii=False)
        if redis_con.get(usermail + 'code') is None:
            app.logger.info(usermail + '验证码失效')
            return json.dumps({'status': 200, 'message': '验证码已经过期', 'args': 0}, ensure_ascii=False)
        else:
            # 获取验证码
            code = redis_con.get(usermail + 'code').decode('utf-8')
            # 验证码校验不成功
            if usercode != code:
                app.logger.info(usermail + '验证码验证失败')
                return json.dumps({'status': 200, 'message': '验证码输入错误', 'args': 0}, ensure_ascii=False)
            salt = os.urandom(64)
            hash_password = encryption(password, salt)
            # 账号的存储
            add_user_account(usermail, hash_password, salt)
            # 用户名的添加
            user_account = select_user_account(usermail)
            # 生成uid
            uid = ''
            for i in range(0, 8):
                uid = uid + str(random.randint(0, 9))
            add_user(user_account.id, uid=int(uid), name=name, img='deful.jpeg')
            # 用户个人信息存储到session里
            session['user'] = pickle.dumps(select_user(user_id=user_account.id))
            app.logger.info(usermail + '注册成功')
            return json.dumps({'status': 200, 'message': '注册成功', 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/login_success', methods=['GET'])
def login_success():
    """
    判断是否为登录状态
    :return:daka是True代表今天打卡
    """
    account = session.get('account')
    user = session.get('user')
    if user is None or account is None:
        return json.dumps({'status': 401, 'message': '没有登录', 'args': 0}, ensure_ascii=False)
    user = pickle.loads(user)
    # 得到用户最后一次打卡的时间
    daka = True
    daka_list = select_daka(user.id)
    if len(daka_list) == 0:
        daka = False
    else:
        update_time = str(daka_list[-1].update_time).split(' ')[0]
        # 得到当前时间
        time_now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # 得到当前时间和用户最后一次打卡时间的差值
        days = (parse(time_now) - parse(str(update_time))).days
        # 默认为True 打卡
        # 如果天数不同，则没有打卡
        if days > 0:
            daka = False
    return json.dumps({'status': 200, 'message': '登录成功', 'daka': daka, 'args': 1,
                       'user': {'src': 'http://127.0.0.1:3333/uploads/' + user.img, 'honey': user.honey,
                                'coin': user.money}}, ensure_ascii=False)


@app.route('/user_login', methods=['POST'])
def user_login():
    """
    用户登录
    :return:
    """
    try:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7)
        data_json = request.get_json()
        # 用户名
        account = data_json['account']
        # 密码
        password = data_json['passwd']
        # 用户名和密码不为空时
        if account is not None and password is not None:
            # 查询数据库看有没有这个用户
            user_account = select_user_account(account)
            if user_account is None:
                # 没有用户
                app.logger.info(account + '登录失败,' + 'error:' + '没有' + account)
                return json.dumps({'status': 200, 'message': '用户名没有注册,请先注册', 'args': 0}, ensure_ascii=False)
            # 对输入密码进行加密
            hash_password = encryption(password, user_account.salt)
            # 输入密码的加密版和数据库的密码进行比对
            if hash_password == user_account.password:
                # 将用户的账号存在session里面
                session['account'] = account
                # 根据user_id这个外键 查询user
                query_result = select_user(user_id=user_account.id)
                # 将user存到session里
                session['user'] = pickle.dumps(query_result)
                # print(session[str(user_account.id)])
                app.logger.info(account + '登录成功')
                return json.dumps(
                    {'status': 200, 'message': '登录成功', 'args': 1}, ensure_ascii=False)
            else:
                logging.info(account + '登录失败,' + 'error:密码错误')
                return json.dumps(
                    {'status': 200, 'message': '用户名或密码错误', 'args': 0}, ensure_ascii=False)
        else:
            return json.dumps(
                {'status': 200, 'message': '参数错误', 'args': 0}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/quit', methods=['GET'])
def user_quit():
    """
    用户退出
    :return:
    """
    try:
        account = session.get('account')
        session.pop('account')
        session.pop('user')
        app.logger.info(str(account) + '退出了')
        return json.dumps({'status': 200, 'message': '退出成功', 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '退出失败', 'args': 0}, ensure_ascii=False)


@app.route('/logoff', methods=['GET'])
def logoff():
    """
    注销账户
    :return:
    """
    try:
        account = session.get('account')
        user = pickle.loads(session.get('user'))
        # 删除账户
        user_account_cancel(account)
        # 删除user
        user_cancel(user.user_id)
        # 清除session
        session.pop(account)
        session.pop(user)
        app.logger.info(account + '用户销毁')
        return json.dumps({'status': 200, 'message': '操作成功', 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error' + str(e))
        return json.dumps({'status': 200, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/reset_mail', methods=['GET'])
def to_user_send_reset_mail():
    """
    重置密码,邮件发送验证码
    :return:
    """
    try:
        # 获取用户名
        usermail = session.get('account')
        if usermail is None:
            app.logger.info('缺失account参数')
            return json.dumps({'status': 401, 'message': '请重新登录', 'args': 0}, ensure_ascii=False)
        # 获取验证码
        code = ''
        for i in range(0, 4):
            code = code + str(random.randrange(0, 10))
        # 邮件的标题
        title = "修改密码"
        # 邮件的内容
        text = reset1 + code + reset2
        # 发送邮件
        send_mail(mail, usermail, title, text)
        # 二进制形式存储key value
        redis_con.set(usermail + 'code', code)
        # 过期时间5分钟
        redis_con.expire(usermail + 'code', 300)
        app.logger.info('邮件发送成功')
        return json.dumps({'status': 200, 'message': '验证码发送成功', 'args': 0}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 200, 'message': '验证码发送失败', 'args': 0}, ensure_ascii=False)


@app.route('/reset', methods=['POST'])
def reset_password():
    """
    修改密码
    :return:
    """
    try:
        # 用户名
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'args': 0, 'message': '请先登录'}, ensure_ascii=False)
        data_json = request.get_json()
        salt = os.urandom(64)
        # 密码
        password = data_json['passwd']
        hash_password = encryption(password, salt)
        update_user_account(account, hash_password, salt)
        app.logger.info(account + '密码修改成功')
        return json.dumps({'status': 200, 'message': '修改成功', 'args': 0}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error' + str(e))
        return json.dumps({'status': 500, 'message': '修改失败'}, ensure_ascii=False)


@app.route('/percentage', methods=['GET'])
def percent():
    """
    百分比
    :return:
    """
    user = session.get('user')
    if user is None:
        return json.dumps({'status': 401, 'message': '重新登录', 'args': 0}, ensure_ascii=False)
    user = pickle.loads(user)
    count = 76
    if user.name is not None and user.name != '':
        count = count + 3
    if user.city is not None and user.city != '':
        count = count + 3
    if user.birthday is not None and user.birthday != '':
        count = count + 3
    if user.introduction is not None and user.introduction != '':
        count = count + 10
    if user.img is not None and user.img != '':
        count = count + 5
    return json.dumps({'status': 200, 'percentage': int(float('%.2f' % (count / 100)) * 100), 'args': 1},
                      ensure_ascii=False)


@app.route('/option', methods=['GET', 'POST'])
def option():
    """
    设置默认页 我的信息
    :return:
    """
    try:
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'message': '请登录', 'args': 0}, ensure_ascii=False)
        # 如果是get方法
        if request.method == 'GET':
            user = pickle.loads(session.get('user'))
            # 格式化时间
            birthday = None if user.birthday is None else datetime.strftime(user.birthday, "%Y-%m-%d")
            app.logger.info(account + '用户个人信息首页查询')
            return json.dumps({'status': 200, 'user': {'name': user.name, 'city': user.city, 'sex': user.sex,
                                                       'birthday': birthday,
                                                       'introduction': user.introduction}, 'args': 1},
                              ensure_ascii=False)
        else:
            data_json = request.get_json()
            data_key = dict(data_json).keys()
            # 得到post参数
            for key in data_key:
                if key == 'birthday':
                    # 0000-9999位 01-12 0-31
                    birthday = parse(data_json[key])
                    to_zone = tz.gettz('CST')
                    birthday = birthday.astimezone(to_zone).strftime("%Y-%m-%d")
                    data_json[key] = birthday
                if key == 'passwd' or key == 'code':
                    # 从redis中获取code
                    code = redis_con.get(account + 'code')
                    # 如果code为空
                    if code is None:
                        return json.dumps({'status': 200, 'message': '验证码已经过期', 'args': 0}, ensure_ascii=False)
                    else:
                        if code == data_json['code']:
                            salt = os.urandom(64)
                            # 密码
                            password = data_json['passwd']
                            hash_password = encryption(password, salt)
                            update_user_account(account, hash_password, salt)
                            app.logger.info(account + '修改密码')
                            break
                        else:
                            return json.dumps({'status': 200, 'message': '验证码输入错误', 'args': 0}, ensure_ascii=False)
            # 获得用户的user_id外键
            user_id = pickle.loads(session.get('user')).user_id
            # 修改用户的个人信息
            update_user(user_id, data_json)
            # 重新放到session里
            session['user'] = pickle.dumps(select_user(user_id=user_id))
            app.logger.info(account + '用户修改个人信息')
            return json.dumps({'status': 200, 'message': '修改成功', 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 200, 'message': '修改失败', 'args': 0}, ensure_ascii=False)


@app.route('/user_img_up', methods=['POST'])
def img_up():
    """
    用户上传图片
    :return:
    """
    try:
        # 获取图片
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'args': 0, 'message': '请登录'}, ensure_ascii=False)
        user = pickle.loads(session.get('user'))
        # 图片上传  参数的名字 file
        mode_list = ['.jpg', '.png', '.jpeg']
        file = request.files['file']
        # 图片的格式
        mode = '.' + secure_filename(file.filename).split('.')[1]
        if mode not in mode_list:
            app.logger.info(account + '用户上传头像失败，不支持' + mode + '格式')
            return json.dumps({'status': 400, 'message': '图片支持jpg,jpeg,png', 'args': 0}, ensure_ascii=False)
        file.save('static/uploads/' + account + mode)
        update_user(user.user_id, {'img': account + mode})
        session.pop('user')
        session['user'] = pickle.dumps(select_user(id=user.id))
        app.logger.info(account + '用户头像上传成功')
        return json.dumps({'status': 200, 'message': '上传成功', 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.error('error' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/user_img', methods=['GET'])
def user_img():
    """
    获得用户的头像信息
    图片的命名方式为：账户名+jpg/png
    :return:
    """
    try:
        # 获取图片
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'args': 0, 'message': '请先登录'}, ensure_ascii=False)
        user = pickle.loads(session.get('user'))
        img = 'http://127.0.0.1:3333/uploads/deful.jpeg'
        if user.img != "" and user.img is not None:
            img = 'http://127.0.0.1:3333/uploads/' + user.img
        app.logger.info(account + '用户查询个人头像')
        return json.dumps(
            {'status': 200, 'message': '查询成功', 'user': {'imageUrl': img}, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/user_bind', methods=['GET'])
def user_bind():
    """
    查询用户的绑定账号
    :return:
    """

    try:
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'message': '请登录', 'args': 0}, ensure_ascii=False)
        user = pickle.loads(session.get('user'))
        app.logger.info(account + '查询用户的绑定信息')
        return json.dumps(
            {'status': 200, 'message': '查询成功', 'user': {'weibo': user.weibo, 'qq': user.qq}, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/user_safe', methods=['GET'])
def user_safe():
    """
    账户安全
    :return:
    """
    try:
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'message': '请登录', 'args': 0}, ensure_ascii=False)
        user = pickle.loads(session.get('user'))
        app.logger.info(account + '查询用户的安全信息')
        return json.dumps(
            {'status': 200, 'message': '查询成功', 'user': {'phone': user.phone, 'email': account}, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/user_url', methods=['GET'])
def user_url():
    """
    我的窝
    :return:
    """
    try:
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'args': 0, 'message': '请登录'}, ensure_ascii=False)
        user = pickle.loads(session.get('user'))
        app.logger.info(account + '我的窝信息')
        return json.dumps(
            {'status': 200, 'message': '查询成功',
             'user': {'wdo': 'http://127.0.0.1:8080/u/' + str(user.uid) + '.html'}, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/user_wallet', methods=['GET'])
def user_wallet():
    """
    用户的钱包
    :return:
    """
    try:
        account = session.get('account')
        if account is None:
            return json.dumps({'status': 401, 'args': 0, 'message': '请登录'}, ensure_ascii=False)
        user = pickle.loads(session.get('user'))
        list = select_wallet_detail(user.id)
        detail = []
        detail_index = 1
        for wallet_detail in list:
            detail.append({'key': detail_index, 'time': str(wallet_detail.update_time), 'num': wallet_detail.add_num,
                           'detail': wallet_detail.detail})
            detail_index = detail_index + 1
        app.logger.info(account + '用户的钱包信息')
        return json.dumps(
            {'status': 200, 'message': '查询成功',
             'user': {'money': user.money, 'honey': user.honey, 'args': 1, 'detail': detail},
             'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/daka', methods=['GET'])
def daka():
    """
    打卡
    :return:
    """
    try:
        user = pickle.loads(session.get('user'))
        num = add_daka(user.id)
        add_wallet_detail(user.id, num, '打卡')
        app.logger.info(str(session.get('account')) + '打卡成功')
        # 蜂蜜值已经改变了 所以user需要重新获取
        session['user'] = pickle.dumps(select_user(id=user.id))
        return json.dumps({'status': 200, 'message': '打卡成功', 'args': 1, 'num': num}, ensure_ascii=False)
    except Exception as e:
        app.logger.info(session.get('account') + '打卡失败' + 'error:' + str(e))
        return json.dumps({'status': 500, 'message': '打卡失败', 'args': 0}, ensure_ascii=False)


@app.route('/home', methods=['GET'])
def get_index():
    """
    主页热门游记还有头图
    :return:
    """
    try:
        # 有page的时候 它是一个空串
        page = request.values.get('page')
        # 首页的头图
        result = get_head_show_image()
        show_image = result[0]['head_info']
        fil = result[1]
        # 首页的页面游记
        hot_list, hot_list_count = get_head_tn_list(page)
        add_hot_data_img(str(hot_list), str(hot_list))
        app.logger.info('主页游记还有头图')
        return json.dumps(
            {'status': 200, 'args': 1, 'hot_data': hot_list, 'dataimg': show_image, 'hot_count': hot_list_count,
             'filter': fil},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/home_new', methods=['GET'])
def get_home_new():
    """
    # 主页最新发表游记
    :return:
    """
    try:
        # 有page的时候 它是一个空串
        page = request.values.get('page')
        new_list, new_list_count = get_head_tn_list0(page)
        add_hot_new_data(str(new_list))
        app.logger.info('主页最新发表游记')
        return json.dumps({'status': 200, 'new_data': new_list, 'new_count': new_list_count, 'args': 1},
                          ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/youji_head', methods=['GET'])
def get_youji_head():
    try:
        youji_id = request.values.get('id')
        """
        游记的头部解析
        游记的出发时间 人均费用等解析
        """
        contentHead = parser_youji_head(youji_id)
        app.logger.info('游记Head抓取')
        # add_youji(str(contentHead), str(contentText), contentDetail)
        return json.dumps(
            {'status': 200, 'contentHead': contentHead, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/youji_text', methods=['GET'])
def get_youji_text():
    try:
        youji_id = request.values.get('id')
        """
        游记的头部解析
        游记的出发时间 人均费用等解析
        """
        contentText = parser_youji_text(youji_id)
        """
        游记的正文部分解析
        """
        app.logger.info('游记正文开头内容(人物，时间)抓取')
        # add_youji(str(contentHead), str(contentText), contentDetail)
        return json.dumps(
            {'status': 200, 'contentText': contentText, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/youji', methods=['GET'])
def get_youji():
    """
    游记内容抓取
    contentHead 游记的头部
    contentText 游记开始的出发时间等等信息
    contentDetail 游记的正文
    id 为游记的id
    :return:
    """
    try:
        youji_id = request.values.get('id')
        contentDetail = ''
        data = ([], None)
        while True:
            data = parser_youji_detail(youji_id, data[1])
            contentDetail = contentDetail + data[0]
            if data[1] == '':
                break
        app.logger.info('游记内容抓取')
        # add_youji(str(contentHead), str(contentText), contentDetail)
        return json.dumps(
            {'status': 200, 'contentDetail': contentDetail, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/youji_related', methods=['GET'])
def youji_related():
    """
    :return:游记右侧相关
    """
    try:
        id = request.values.get('id')
        mdd, gonglve, youji_list = parser_youji_related(id)
        return json.dumps({'mdd': mdd, 'gonglve': gonglve, 'youji': youji_list, 'status': 200, 'args': 1},
                          ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/mdd', methods=['GET'])
def get_destination():
    """
    目的地页面的抓取
    :return:
    """
    try:
        result = destination_parser()
        head = result[0]
        hot_poi_result = result[1]['hot_list_result']
        season_recommend = result[2]['season_recommend']
        add_destination(str(head), str(hot_poi_result), str(season_recommend))
        app.logger.info("目的地页面的抓取")
        return json.dumps(
            {'status': 200, 'head': head, 'season_recommend': season_recommend, 'hot_poi_result': hot_poi_result,
             'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.error('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/gong_lve', methods=['GET'])
def get_gong_lve():
    """
    攻略页面的抓取
    :return:
    """
    try:
        result = gong_lve_parser()
        nav_left = result[0]['nav']
        nav_right_img = result[1]['img']
        content = result[2]['content']
        add_gong_lve(str(nav_left), str(nav_right_img), str(content))
        app.logger.info('攻略页面的抓取')
        return json.dumps(
            {'status': 200, 'gonglve_nav': nav_left, 'dataimg': nav_right_img, 'content': content, 'args': 1},
            ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/ziyouxinggonglver', methods=['GET'])
def ziyouxingr():
    try:
        id = request.values.get('id')
        ziyouxingr = ziyouxingr_parser(id)
        app.logger.info('message:' + 'ziyouxing')
        return json.dumps({'status': 200, 'ziyouxingr': ziyouxingr, 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/ziyouxinggonglvel', methods=['GET'])
def ziyouxingl():
    try:
        id = request.values.get('id')
        ziyouxingl = ziyouxingl_parser(id)
        app.logger.info('message:' + 'ziyouxing')
        return json.dumps({'status': 200, 'ziyouxingl': ziyouxingl, 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/ziyouxinggonglve_related', methods=['GET'])
def ziyouxing_related():
    try:
        id = request.values.get('id')
        ziyouxing_related = ziyouxing_related_parser(id)
        app.logger.info('message:' + 'ziyouxing')
        return json.dumps({'status': 200, 'ziyouxing_related': ziyouxing_related, 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/ziyouxinggonglve', methods=['GET'])
def ziyouxing():
    try:
        id = request.values.get('id')
        location = ziyouxing_location_parser(id)
        app.logger.info('message:' + 'ziyouxing')
        return json.dumps({'status': 200, 'location': location, 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0})


@app.route('/wenda/hot', methods=['GET'])
def wenda_hot():
    try:
        hot_question = wenda_hot_parser()
        return json.dumps({'status': 200, 'args': 1, 'hot_question': hot_question}, ensure_ascii=False)
    except Exception as e:
        app.logger.info("error:" + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/wenda/new', methods=['GET'])
def wenda_new():
    try:
        new_question = wenda_new_parser()
        return json.dumps({'status': 200, 'args': 1, 'new_question': new_question}, ensure_ascii=False)
    except Exception as e:
        app.logger.info("error:" + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/wenda/wait', methods=['GET'])
def wenda_wait():
    try:
        wait_question = wenda_wait_parser()
        return json.dumps({'status': 200, 'args': 1, 'wait_question': wait_question}, ensure_ascii=False)
    except Exception as e:
        app.logger.info("error:" + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/wenda_detail')
def wenda_detail():
    try:
        id = request.values.get('id')
        mdd, mdd_href, title, detail, tags, user, time, liulan_num, guanzhu_num, num, answer_list = wenda_detail_parser(
            id)
        return json.dumps(
            {'status': 200, 'mdd': mdd, 'mdd_href': mdd_href, 'title': title, 'detail': detail, 'tags': tags,
             'user_name': user.get('user_name'), 'user_href': user.get('user_href'),
             'user_img': user.get('user_img'),
             'time': time, 'liulan_num': liulan_num, 'guanzhu_num': guanzhu_num, 'num': num,
             'answer_list': answer_list, 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.info("error:" + str(e))
        return json.dumps({'status': 500, 'message': '系统错误', 'args': 0}, ensure_ascii=False)


@app.route('/wenda_related', methods=['GET'])
def wenda_related():
    try:
        id = request.values.get('id')
        activity, related_questions = wenda_related_parser(id)
        return json.dumps({'status': 200, 'args': 1, 'activity': activity, 'related_questions': related_questions},
                          ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'args': 0}, ensure_ascii=False)


@app.route('/write_gonglve', methods=['POST'])
def write_gonglve():
    try:
        data = request.get_json()
        content = data.get('content')
        title = data.get('title')
        user = pickle.loads(session['user'])
        add_write_gonglve(user.id, title, content)
        return json.dumps({'status': 200, 'args': 1}, ensure_ascii=False)
    except Exception as e:
        app.logger.info('error:' + str(e))
        return json.dumps({'status': 500, 'args': 0}, ensure_ascii=False)


# @app.route('/code_ver', methods=['POST'])
# def code_verification():
#     """
#     注册页面验证码的验证
#     :return:
#     """
#     try:
#         data_json = request.get_json()
#         # 获得用户名
#         usermail = data_json.get('account')
#         # 获得密码
#         usercode = data_json.get('code')
#         if usermail is None or usercode is None:
#             return json.dumps({'status': 400, 'args': 0}, ensure_ascii=False)
#         # 从redis中获取code
#         code = redis_con.get(usermail + 'code')
#         # 如果code为空
#         if code is None:
#             return json.dumps({'status': 200, 'message': '验证码已经过期', 'args': 0}, ensure_ascii=False)
#         else:
#             if code == usercode:
#                 return json.dumps({'status': 200, 'message': '验证通过', 'args': 1}, ensure_ascii=False)
#             else:
#                 return json.dumps({'status': 200, 'message': '验证码输入错误', 'args': 0}, ensure_ascii=False)
#     except Exception as e:
#         print(e)
#         return json.dumps({'status': 500, 'message': '系统错误'}, ensure_ascii=False)
if __name__ == '__main__':
    app.run()
