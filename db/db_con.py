from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 获得session
def get_con():
    try:
        engine = create_engine('mysql+pymysql://root@localhost:3306/test?charset=utf8mb4', echo=True,
                               encoding='utf-8', convert_unicode=True, pool_size=5, pool_timeout=30, pool_recycle=-1,
                               max_overflow=3)
        # 创建DBSession类型:
        session = sessionmaker(bind=engine)
        return session()
    except Exception as e:
        print(e)
