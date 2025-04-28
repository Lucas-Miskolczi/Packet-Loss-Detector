import sys
import threading
import signal
from app.sniffer.sniffer import start_sniffing
import uvicorn
import platform
from scapy.all import get_if_list, get_if_addr
from scapy.arch.windows import get_windows_if_list


shutdown_flag = threading.Event()

### Function to run the sniffer to grab packets ###
def run_sniffer(interface, shutdown_flag):
    start_sniffing(interface, shutdown_flag)

### Force shutdown with CTRL + C to stop all processes ###
def stop_gracefully(signum, frame):
    print("\nShutting down gracefully...")
    shutdown_flag.set()

### Auto select the interface. This is especially necessary on Windows (in mac and linux it's much easier) ###
def select_interface():
    if platform.system() == "Windows":
        interfaces = get_windows_if_list()

        selected = None
        for iface in interfaces:
            iface_name = iface.get('name', '').lower()
            iface_desc = iface.get('description', '').lower()
            if (
                ("ethernet" in iface_name or "wi-fi" in iface_name)
                and not any(kw in iface_desc for kw in ["virtual", "vethernet", "hyper-v", "loopback", "tunnel", "pseudo"])
            ):
                selected = iface.get('name')
                print(f"Automatically selected: {selected}")
                return selected

        # If auto-select fails, print available interfaces and allow the user to choose
        if not selected:
            print("Available interfaces:")
            for idx, iface in enumerate(interfaces):
                iface_name = iface.get('name', 'Unknown')
                iface_desc = iface.get('description', 'No description')
                print(f"{idx}: {iface_name} ({iface_desc})")

            # Let the user select the interface
            try:
                choice = int(input("Enter the number of the interface to select: "))
                if 0 <= choice < len(interfaces):
                    selected = interfaces[choice].get('name')
                    print(f"Manually selected: {selected}")
                else:
                    print("Invalid choice, please try again.")
                    return select_interface()  # Recursively call if invalid choice
            except ValueError:
                print("Invalid input, please enter a number.")
                return select_interface()  # Recursively call if non-integer input

        return selected

    else:
        ### Linux y Mac. Linux -> suele ser eth0, wlan0 ; Mac -> en0, en1 ###
        interfaces = get_if_list()
        print("Available interfaces:", interfaces)
        if interfaces:
            return interfaces[0]
        else:
            print("No interfaces found.")
            sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_gracefully)

    # interface = "Ethernet"  ### -> Local Testing ###

    interface = select_interface()

    ### Only the sniffer runs in background ###
    sniffer_thread = threading.Thread(target=run_sniffer, args=(interface, shutdown_flag))
    sniffer_thread.start()

    ### Uvicorn needs to be main thread, not background ###
    #uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

    ### With this code, CTRL+C will kill the program, not just pause ###
    print("Waiting for sniffer to close...")
    sniffer_thread.join()

    print("Finished.")
    sys.exit(0)
