from ..bot import config
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from urllib.parse import quote_plus
import os

connection_url = URL.create(
    username=os.getenv("database_username"),
    password=quote_plus(os.getenv("database_password")),
    host=os.getenv("database_host"),
    port=os.getenv("database_port"),
    database=config["database"]["database"],
)

drivername=config["database"]["sqlalchemy"]["connector"],

Base = declarative_base()

