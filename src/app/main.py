from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import crud, schemas, database
from sqlalchemy import func
from app.models import Packet

'''
Could integrate Alembic for migrations, small tool doesn't require it
'''

app = FastAPI()

database.init_db() ### From database.py , if tables aren't created create them ###

def get_db():
    db = database.SessionLocal() ### Create a new session for each request ###
    try:
        yield db ### Dependency injection for FastAPI ###
    finally:
        db.close() ### Close the session ###


### Health endpoint to check if the API is up and running ###
@app.get("/health")
def health_check():
    return {"status": "OK", "message": "API is running"}


'''
Get Latest packets, terminal view

SELECT *
FROM packets
ORDER BY timestamp DESC
LIMIT 45;

'''
@app.get("/packets/latest/")
def get_latest_packets(limit: int = 45, db: Session = Depends(get_db)): ### Increase limit to display more packets ###
    return {"packets": db.query(Packet).order_by(Packet.timestamp.desc()).limit(limit).all()}

'''
Locate TCP and UDP

SELECT COUNT(*)
FROM packets
WHERE protocol = 'TCP';

SELECT COUNT(*)
FROM packets
WHERE protocol = 'UDP';

'''
@app.get("/packets/protocols/")
def get_protocol_counts(db: Session = Depends(get_db)):
    tcp_count = db.query(Packet).filter(Packet.protocol == "TCP").count()
    udp_count = db.query(Packet).filter(Packet.protocol == "UDP").count()
    return {"tcp": tcp_count, "udp": udp_count}

'''
Top 5 SRC

SELECT src_ip, COUNT(src_ip) AS count
FROM packets
GROUP BY src_ip
ORDER BY count DESC
LIMIT 5;

'''
@app.get("/packets/top-sources/")
def get_top_sources(db: Session = Depends(get_db)):
    top_sources = (
        db.query(Packet.src_ip, func.count(Packet.src_ip).label("count"))
        .group_by(Packet.src_ip)
        .order_by(func.count(Packet.src_ip).desc())
        .limit(5)
        .all()
    )
    return {"top_sources": [f"{ip} ({count} packets)" for ip, count in top_sources]}

'''
Top 5 DST

SELECT dst_ip, COUNT(dst_ip) AS count
FROM packets
GROUP BY dst_ip
ORDER BY count DESC
LIMIT 5;

'''
@app.get("/packets/top-destinations/")
def get_top_destinations(db: Session = Depends(get_db)):
    top_destinations = (
        db.query(Packet.dst_ip, func.count(Packet.dst_ip).label("count"))
        .group_by(Packet.dst_ip)
        .order_by(func.count(Packet.dst_ip).desc())
        .limit(5)
        .all()
    )
    return {"top_destinations": [f"{ip} ({count} packets)" for ip, count in top_destinations]}



### Full unrestricted request, deprecated ###
# @app.get("/packets/", response_model=list[schemas.PacketRead])
# def read_packets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     packets = crud.get_packets(db, skip=skip, limit=limit)
#     return packets