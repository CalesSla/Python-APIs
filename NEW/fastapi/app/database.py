from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()


SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{os.getenv("dbpassword")}@localhost/fastapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)