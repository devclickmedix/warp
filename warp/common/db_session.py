
from warp.runtime import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def setupSession():
    conn_str = config['db'].replace("postgres", "postgresql")
    # check if is there any option for storm
    conn_str = conn_str.split("?")[0]
    engine = create_engine(conn_str, 
        isolation_level=config.get("isolation_level", "READ COMMITTED"),
        echo=config.get("trace"))
    Session = sessionmaker(bind=engine)
    Base = declarative_base()
    return Session(), Base
