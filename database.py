from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL="sqlite:///./contactbook.db"

engine=create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False})

sessionlocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

base=declarative_base()
