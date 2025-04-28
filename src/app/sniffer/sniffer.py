from scapy.all import sniff
from app.utils.network_utils import extract_packet_info
from app.database import SessionLocal
from app import crud

def packet_callback(packet):
    info = extract_packet_info(packet)
    if info:
        db = SessionLocal()
        try:
            crud.create_packet(db, **info)
        finally:
            db.close()

def start_sniffing(interface: str, shutdown_flag):
    while not shutdown_flag.is_set():
        sniff(
            iface=interface,
            prn=packet_callback,
            store=False, ### No need store, have the DB ###
            timeout=1  ### Bug fix of infinite loop,  This sets a timeout (in seconds) for each sniff operation, so it doesn’t run indefinitely and allows the shutdown flag to be checked periodically. ###
        )
