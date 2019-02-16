from db.db_con import *
from datetime import datetime
from dateutil.parser import parse
from db.db_class import *
import time


# 查询user表
def select_user(user_id):
    """
    查询user
    :param user_id:
    :return:
    """
    # 创建Session:
    session = get_con()
    try:
        # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
        result = session.query(User).filter(User.user_id == user_id).all()
        if len(result) == 0:
            return None
        else:
            return result[0]
    except Exception as e:
        print(e)
    finally:
        session.close()

# 查询user表
def select_user_by_Id(id):
    """
    查询user
    :param user_id:
    :return:
    """
    # 创建Session:
    session = get_con()
    try:
        # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
        result = session.query(User).filter(User.id == id).all()
        if len(result) == 0:
            return None
        else:
            return result[0]
    except Exception as e:
        print(e)
    finally:
        session.close()

# user增加数据
def add_user(user_id, uid=0, name=None, sex=None, city=None, birthday=None, introduction=None, address=None, img=None,
             weibo=None, qq=None,
             money=None, honey=None, phone=None):
    """
    添加user
    :param user_id:
    :param name:
    :param sex:
    :param city:
    :param birthday:
    :param introduction:
    :param img:
    :param weibo:
    :param qq:
    :param money:
    :param honey:
    :param phone
    :return:
    """
    session = get_con()
    try:
        new_user = User(uid=uid, name=name, sex=sex, city=city, birthday=birthday, introduction=introduction,
                        address=address,
                        img=img,
                        weibo=weibo, qq=qq, honey=honey, money=money, user_id=user_id, phone=phone)
        session.add(new_user)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def user_cancel(user_id):
    session = get_con()
    try:
        user = select_user(user_id)
        session.delete(user)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def update_user(user_id, kwargs):
    """
    更新user
    :param user_id:
    :param kwargs:
    :return:
    """
    session = get_con()
    try:
        user = select_user(user_id)
        if kwargs.get('uid') is not None:
            user.uid = kwargs['uid']
        if kwargs.get('name') is not None:
            user.name = kwargs['name']
        if kwargs.get('sex') is not None:
            user.sex = kwargs['sex']
        if kwargs.get('city') is not None:
            user.city = kwargs['city']
        if kwargs.get('birthday') is not None:
            user.birthday = kwargs['birthday']
        if kwargs.get('introduction') is not None:
            user.introduction = kwargs['introduction']
        if kwargs.get('address') is not None:
            user.introduction = kwargs['address']
        if kwargs.get('img') is not None:
            user.img = kwargs['img']
        if kwargs.get('weibo') is not None:
            user.weibo = kwargs['weibo']
        if kwargs.get('qq') is not None:
            user.qq = kwargs['qq']
        if kwargs.get('money') is not None:
            user.money = kwargs['money']
        if kwargs.get('phone') is not None:
            user.phone = kwargs['phone']
        if kwargs.get('honey') is not None:
            user.honey = kwargs['honey']
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def user_account_cancel(account):
    session = get_con()
    try:
        user_account = select_user_account(account)
        session.delete(user_account)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_user_account(account, password, salt):
    """
    添加账户
    :param account:
    :param password:
    :param salt:
    :return:
    """
    session = get_con()
    try:
        new_user_account = UserAccount(account=account, password=password, salt=salt)
        session.add(new_user_account)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def select_user_account(mail_number):
    """
    根据邮箱查询账户
    :param mail_number:邮箱
    :return:
    """
    session = get_con()
    try:
        result = session.query(UserAccount).filter(UserAccount.account == mail_number).all()
        if len(result) == 0:
            return None
        return result[0]
    except Exception as e:
        print(e)
    finally:
        session.close()


def update_user_account(mail_number, password=None, salt=None):
    """
    更新用户的账户
    :param mail_number:
    :param password:
    :param salt:
    :return:
    """
    session = get_con()
    try:
        user_account = session.query(UserAccount).filter(UserAccount.account == mail_number).one()
        if password is not None:
            user_account.password = password
        if salt is not None:
            user_account.salt = salt
        session.add(user_account)
        session.commit()
        return user_account
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_daka(user_id):
    """

    :param user_id:user的id
    :return:
    """
    session = get_con()
    try:
        # 得到最后一次的打卡时间
        last_daka = select_daka(user_id)[-1]
        last_time = last_daka.update_time
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        a = parse(update_time)
        b = parse(str(last_time))
        sub = (a-b).days
        days = 1
        # 连续打卡了
        if sub <=1:
            days = last_daka.days+1
        num = days%7 if days%7!=0 else 7
        user = select_user_by_Id(user_id)
        honey = user.honey+num
        add_user(user.user_id,{'honey':honey})
        daka = DaKa(user_id=user_id,update_time=update_time,last_time=last_time,days=days)
        session.add(daka)
        session.commit()
        return num
    except Exception as e:
        print(e)
    finally:
        session.close()


def select_daka(user_id):
    session = get_con()
    try:
        list = session.query(DaKa).filter(DaKa.user_id == user_id).all()
        return list
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_hot_data_img(hot_data, hot_img):
    """
    首页的热门游记还有头图
    :param hot_data:
    :param hot_img:
    :return:
    """
    session = get_con()
    try:
        print(datetime.now())
        new_hot_data_img = HomeDataImg(hot_data=hot_data, hot_img=hot_img, update_time=datetime.now())
        session.add(new_hot_data_img)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_hot_new_data(new_data):
    """
    首页最先发表
    :param new_data:
    :return:
    """
    session = get_con()
    try:
        print(datetime.now())
        new_hot_new_data = HomeNewData(new_data=new_data, update_time=datetime.now())
        session.add(new_hot_new_data)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_youji(content_head, content_text, content_detail):
    """
    游记内容页
    :param content:
    :return:
    """
    session = get_con()
    try:
        new_content = YouJi(content_head=content_head, content_text=content_text, content_detail=content_detail,
                            update_time=datetime.now())
        session.add(new_content)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_destination(head_img_info, hot_poi_info, season_recommend):
    """
    目的地
    :param head_img_info:
    :param hot_poi_info:
    :param season_recommend:
    :return:
    """
    session = get_con()
    try:
        new_destination = Destination(head_img_info=head_img_info, hot_poi_info=hot_poi_info,
                                      season_recommend=season_recommend, update_time=datetime.now())
        session.add(new_destination)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


def add_gong_lve(nav_left, nav_right_img, content):
    """
    攻略页
    :param nav_left:
    :param nav_right_img:
    :param content:
    :return:
    """
    session = get_con()
    try:
        new_gong_lve = GongLve(nav_left=nav_left, nav_right_img=nav_right_img,
                               content=content, update_time=datetime.now())
        session.add(new_gong_lve)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


if __name__ == '__main__':
    # a = parse('2018-10-10 12:02:11')
    # b = parse('2018-10-10 12:02:11')
    # print((a-b).days)
    add_daka(1)