from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

'''
CREATE TABLE packets (
    id SERIAL PRIMARY KEY,
    src_ip VARCHAR(15),
    dst_ip VARCHAR(15),
    protocol VARCHAR(10),
    size INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);
'''

Base = declarative_base()

class Packet(Base):
    __tablename__ = "packets"

    id = Column(Integer, primary_key=True, index=True)
    src_ip = Column(String(15))
    dst_ip = Column(String(15))
    protocol = Column(String(10))
    size = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=func.now())
