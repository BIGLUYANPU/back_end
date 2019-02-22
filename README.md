# back_end
# 项目包
flask

flask-cors

flask-mail

python-dateutil

requests

beautifulsoup4

werkzeug

redis

sqlalchemy

pymysql
# 所有接口一览表
## 非用户行为和信息相关的url(爬虫获取的数据url)
1.**问答相关**

/wenda 方法get 获取热门问题 最新问题 待回答问题

/wenda/detail?id= 方法get 获取具体问答

/wenda_related?id= 方法get 获取具体问答右侧的推荐

2.**写攻略**

/write_gonglve 方法post 参数title(标题) content(内容)

3.**自由行详情页面**

/ziyouxing?id= 方法get 获取具体的自由行页面

4.**攻略大类页面获取(自由行 游记 问答)**

/gong_lve 方法get 获取攻略推荐页面

5.**目的地**

/mdd 方法get 目的地页面的抓取

6.**游记相关**

/youji_related 方法get 游记右侧推荐

/youji 方法get 游记页面详情

7.**主页相关**

/home_new 方法get 主页中间最新游记模块的抓取

/home 方法get 主页的头图和主页的热门游记抓取
## 用户相关接口一览表
1.**注册前的邮箱验证**

/account_ver 方法post 参数:account(邮箱)

2.**注册发送邮件**

/mail 方法get

3.**注册**

/regist 方法post 参数:passwd(密码) name(用户昵称) code(邮箱验证码)

4.**用户登录检测**

/login_success 方法get status:200 args:1 daka:True 用户登录且已经打卡

5.**用户登录**

/user_login  方法post 参数:account:邮箱账号 passwd:密码

6.**用户退出**

/quit 方法get status:200 args:1 用户退出成功

7.**用户注销**

/logoff  方法get status:200 args:1 用户注销成功

8.**用户个人资料相关**

/percentage 方法get 获得用户个人信息资料完善度

/option 方法get和方法post

&emsp;&emsp;方法为get时:获取我的信息相关内容

&emsp;&emsp;方法为post时:

&emsp;&emsp;&emsp;&emsp;1.用于我的信息页面 个人信息的更改

&emsp;&emsp;&emsp;&emsp;2.用于我的账号 密码的更改

/user_img 方法get 获取用户头像信息

/user_img_up 方法post 参数:file用户上传头像

/user_wallet 方法get 获取用户的蜂蜜数目

/daka 方法get 用户打卡
# 2月20日更新日志
## 修改bug:
/gong_lve
/daka
/home
## 优化:
db/db_class.py 可以实现全部删除表/创建表
## 新增:
根目录下setting.py可以配置数据库的用户名和密码
# 2月21日更新日志
## 修改bug:
/mdd：season_recommend字段改成数组(key值改为数字)

/gong_lve 修复部分gonglve_url获取不到的问题

/user_wallet 打卡完成之后,user重新获取，解决bug
## 新增
/wenda 增加wenda 获取hot_questions,new_questions,wait_questions

/write_gonglve 增加写攻略这个接口
# 2月22日更新日志
## 修改bug：
1.用户信息的修改sql 做更改

2.问答 用户头像获取的bug修改

3.用户默认头像 找不到的问题
## 新增
1.readme 写明目前用到的接口

2.write_gonglve表 增加title

3.增加wallet_detail表
## 优化
1.对目前接口的重新做了次测试

2./user_wallet 增加detail字段[{'key':,'detail':,'num':,'time':}]