from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, BINARY, Text,TIMESTAMP

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    # 名字
    name = Column(String(50))
    # 性别
    sex = Column(String(10))
    # 城市
    city = Column(String(50))
    # 生日
    birthday = Column(DateTime)
    # 个人简介
    introduction = Column(String(255))
    # 收货地址
    address = Column(String(255))
    # 头像
    img = Column(String)
    # 微博
    weibo = Column(String(20))
    # qq
    qq = Column(String(15))
    # 手机
    phone = Column(String(15))
    # 金币
    money = Column(Integer)
    # 蜂蜜
    honey = Column(Integer)
    # user对应的user_count
    user_id = Column(Integer)


class UserAccount(BaseModel):
    __tablename__ = 'user_account'
    id = Column(Integer, primary_key=True)
    account = Column(String)
    password = Column(String)
    salt = Column(String)
    # status = Column(Integer)


class DaKa(BaseModel):
    __tablename__ = 'daka'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    update_time = Column(DateTime)
    last_time = Column(DateTime)
    days = Column(Integer)
    status = Column(Integer)

class HomeDataImg(BaseModel):
    __tablename__ = 'home_data_img'
    id = Column(Integer, primary_key=True)
    hot_data = Column(Text)
    hot_img = Column(Text)
    update_time = Column(DateTime)


class HomeNewData(BaseModel):
    __tablename__ = 'home_new_data'
    id = Column(Integer, primary_key=True)
    new_data = Column(Text)
    update_time = Column(Text)


class YouJi(BaseModel):
    __tablename__ = 'youji'
    id = Column(Integer, primary_key=True)
    content_head = Column(Text)
    content_text = Column(Text)
    content_detail = Column(Text)
    update_time = Column(DateTime)


class Destination(BaseModel):
    __tablename__ = 'destination'
    id = Column(Integer, primary_key=True)
    head_img_info = Column(Text)
    hot_poi_info = Column(Text)
    season_recommend = Column(Text)
    update_time = Column(DateTime)


class GongLve(BaseModel):
    __tablename__ = 'gonglve'
    id = Column(Integer, primary_key=True)
    nav_left = Column(Text)
    nav_right_img = Column(Text)
    content = Column(Text)
    update_time = Column(DateTime)
