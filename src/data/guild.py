from sqlalchemy import Column, BigInteger
from ..data import Base

class Guild(Base):
    __tablename__ = "guilds"

    Id = Column(BigInteger, primary_key=true)