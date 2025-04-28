from sqlalchemy.orm import Session
from app import models, schemas

def create_packet(db: Session, src_ip: str, dst_ip: str, protocol: str, size: int):
    db_packet = models.Packet(
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        size=size
    )
    db.add(db_packet)
    db.commit()
    db.refresh(db_packet)
    return db_packet

def get_packets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Packet).offset(skip).limit(limit).all()
