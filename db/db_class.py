from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, BINARY, Text
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from db.db_con import *
from sqlalchemy import Table

BaseModel = declarative_base()
engine = get_engine()


class User(BaseModel):
    __tablename__ = 'user'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
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
    img = Column(String(255))
    # 微博
    weibo = Column(String(20))
    # qq
    qq = Column(String(15))
    # 手机
    phone = Column(String(15))
    # 金币
    money = Column(Integer, server_default='0')
    # 蜂蜜
    honey = Column(Integer, server_default='0')
    # user对应的user_count
    user_id = Column(Integer)


class UserAccount(BaseModel):
    __tablename__ = 'user_account'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(50))
    password = Column(String(64))
    salt = Column(BINARY(64))
    # status = Column(Integer)


class DaKa(BaseModel):
    __tablename__ = 'daka'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    update_time = Column(DateTime)
    last_time = Column(DateTime)
    days = Column(Integer)


class HomeDataImg(BaseModel):
    __tablename__ = 'home_data_img'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    hot_data = Column(Text)
    hot_img = Column(Text)
    update_time = Column(DateTime, nullable=False, server_default=func.now())


class HomeNewData(BaseModel):
    __tablename__ = 'home_new_data'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    new_data = Column(Text)
    update_time = Column(DateTime, nullable=False, server_default=func.now())


class YouJi(BaseModel):
    __tablename__ = 'youji'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_head = Column(Text)
    content_text = Column(Text)
    content_detail = Column(Text)
    update_time = Column(DateTime, nullable=False, server_default=func.now())


class Destination(BaseModel):
    __tablename__ = 'destination'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_img_info = Column(Text)
    hot_poi_info = Column(Text)
    season_recommend = Column(Text)
    update_time = Column(DateTime, nullable=False, server_default=func.now())


class GongLve(BaseModel):
    __tablename__ = 'gonglve'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    nav_left = Column(Text)
    nav_right_img = Column(Text)
    content = Column(Text)
    update_time = Column(DateTime, nullable=False, server_default=func.now())

class WriteGongLve(BaseModel):
    __tablename__ = 'write_gonglve'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_character_set': 'utf8mb4',
        'mysql_collate': 'utf8mb4_bin',
        'mysql_auto_increment': '1',
        'mysql_row_format': 'Compact'
    }
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    title = Column(String(50))
    content = Column(Text)
    update_time = Column(DateTime, nullable=False, server_default=func.now())
if __name__ == '__main__':
    # 删除所有的表,有需要使用
    # BaseModel.metadata.drop_all(engine)
    # 数据库没有的表会创建，有的不会删除
    BaseModel.metadata.create_all(engine)
