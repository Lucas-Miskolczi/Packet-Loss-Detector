from scapy.layers.inet import IP, TCP, UDP

def extract_packet_info(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        size = len(packet)

        if TCP in packet:
            protocol = 'TCP'
        elif UDP in packet:
            protocol = 'UDP'
        else:
            protocol = str(packet[IP].proto)  # Fallback to protocol number

        return {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": protocol,
            "size": size
        }
    return None
