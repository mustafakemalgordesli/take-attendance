import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv('DATABASE_URL')

engine = create_engine(DB_URL, isolation_level = "REPEATABLE READ")

Session = sessionmaker(bind=engine)

session = Session()

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    role = Column(String)

# Create the table in the database
Base.metadata.create_all(engine)