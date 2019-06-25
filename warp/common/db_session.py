
from warp.runtime import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def setupSession():
    conn_str = config['db'].replace("postgres", "postgresql")
    engine = create_engine(conn_str, 
        isolation_level=config.get("isolation_level", "READ COMMITTED")
        echo=config.get("trace"))
    Session = sessionmaker(bind=engine)
    return Session()
