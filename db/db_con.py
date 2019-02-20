from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setting import db_user, db_password


# 得到数据库引擎
def get_engine():
    engine = create_engine('mysql+pymysql://' + db_user + ':' + db_password + '@localhost:3306/test?charset=utf8mb4',
                           echo=True,
                           encoding='utf-8', convert_unicode=True, pool_size=5, pool_timeout=30, pool_recycle=-1,
                           max_overflow=3)
    return engine


# 获得session
def get_con():
    try:
        engine = get_engine()
        # 创建DBSession类型:
        session = sessionmaker(bind=engine)
        return session()
    except Exception as e:
        print(e)
