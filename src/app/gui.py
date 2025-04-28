import requests
import dearpygui.dearpygui as dpg
import threading
import time

API_URL = "http://127.0.0.1:8000" ### Use standard localhost API url, should look to see if 8000 isn't open, check later (add to config???) ###


### Flag to indicate if the API URL is reachable, adding fallback ###
api_reachable = False


def check_api_status(url):
    """Check if the API is reachable."""
    try:
        response = requests.get(f"{url}/health")
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False
    

def set_api_url():
    """Set the API URL based on availability."""
    global API_URL, api_reachable
    if check_api_status(API_URL):
        print(f"API corriendo: {API_URL}")
        api_reachable = True
    else:
        print(f"API no es alacanzable: {API_URL}. Probando fallback.") ### Maybe use localhost as fallback? ###
        API_URL = "http://0.0.0.0:8000"
        if check_api_status(API_URL):
            print(f"API corriendo: {API_URL}")
            api_reachable = True
        else:
            print("API todavia no es alcanzable, verifique el servidor.")


set_api_url() ### Call function to set API URL ###


if api_reachable:
    stop_event = threading.Event() ### Init thread as false, like always open switch, close thread when event is set (flag = True) ###


    def fetch_data():
        while not stop_event.is_set():
            try:
                ### API GET requests, no need for filters ###
                packets = requests.get(f"{API_URL}/packets/latest/").json()
                tcp_udp = requests.get(f"{API_URL}/packets/protocols/").json() ### -> No need to split in two requests, one is fine, split the view ###
                top_sources = requests.get(f"{API_URL}/packets/top-sources/").json()
                top_destinations = requests.get(f"{API_URL}/packets/top-destinations/").json()

                '''
                Example function of log_text display:
                2025-04-27T12:00:00 - TCP - 192.168.1.1 -> 192.168.1.2
                2025-04-27T12:01:00 - UDP - 192.168.1.2 -> 192.168.1.3
                '''

                if 'packets' in packets:
                    if isinstance(packets['packets'], list):
                        log_text = "\n".join([f"{p['timestamp']} - {p['protocol']} - {p['src_ip']} -> {p['dst_ip']}" for p in packets['packets']])
                        dpg.set_value("packet_log", log_text)
                    else:
                        dpg.set_value("packet_log", "No packet data available") ### Could add a log file export if needed ###

                # TCP / UDP ###
                if 'tcp' in tcp_udp and 'udp' in tcp_udp:
                    tcp_traffic = tcp_udp.get("tcp", 0)
                    udp_traffic = tcp_udp.get("udp", 0)

                    total_traffic = tcp_traffic + udp_traffic ### API Filter Maybe?? ###
                    if total_traffic > 0: ### Bug fix, if 0, divide by 0 error ###
                        tcp_percentage = (tcp_traffic / total_traffic) * 100 ### Percentage (could default to math lib, not really needed though) ###
                        udp_percentage = (udp_traffic / total_traffic) * 100
                    else:
                        tcp_percentage = udp_percentage = 0

                    dpg.set_value("tcp_total", f"TCP Total: {tcp_traffic} packets")
                    dpg.set_value("tcp_bar", tcp_percentage / 100)  ### Progress bar ###

                    dpg.set_value("udp_total", f"UDP Total: {udp_traffic} packets")
                    dpg.set_value("udp_bar", udp_percentage / 100)  ### Progress bar ###

                    dpg.set_value("tcp_percentage", f"{tcp_percentage:.2f}%") ### Should round maybe? Decimal in percentage isn't 'proper' ###
                    dpg.set_value("udp_percentage", f"{udp_percentage:.2f}%")

                ### Top SRC IP, Retrieved from API, match dict to GUI ###
                if "top_sources" in top_sources:
                    dpg.set_value("top_sources", "\n".join(top_sources.get("top_sources", [])))

                ### Top DST IP, Retrieved from API, match dict to GUI ###
                if "top_destinations" in top_destinations:
                    dpg.set_value("top_destinations", "\n".join(top_destinations.get("top_destinations", [])))

            except Exception as e:
                print("Error fetching data:", e)
                current_log = dpg.get_value("error_log")
                new_error = f"Error: {e}\n"
                dpg.set_value("error_log", current_log + new_error)

            time.sleep(1)  ### Add auto 1s refresh, could implement Websocket if not, though data flow isn't that high ###


    '''
    Start the GUI, follow basic steps here, end of the GUI is at the end of main windows and child windows.
    Ref : https://dearpygui.readthedocs.io/en/latest/tutorials/first-steps.html
    '''

    dpg.create_context()

    with dpg.window(label="Packet Monitor", width=1200, height=800): ### Main window, if this stops all others stop, can't run windows in background 🤔🤔 ###
        with dpg.child_window(width=-1, height=-1): ### -> -1 occupies the max amount of space available  ###
            with dpg.group(horizontal=True):

                ### Left Side (Packet Log) ###
                with dpg.child_window(width=550, height=700):
                    dpg.add_spacer(height=10) ### Padding ###
                    dpg.add_text("Stream de Datos de Paquetes", bullet=True) ### Simulate WSS Stream with REST Async refresh ###
                    dpg.add_text("", tag="packet_log", wrap=530)

                ### Right Side (TCP/UDP Totals, Traffic, and Top IPs) ###
                with dpg.child_window(width=550, height=750):
                    dpg.add_spacer(height=10)

                    ### Total ###
                    dpg.add_text("Trafico Total -> TCP vs UDP", bullet=True)

                    ### TCP ###
                    dpg.add_text("", tag="tcp_total")
                    dpg.add_progress_bar(default_value=0.0, tag="tcp_bar", width=300)  ### I have no idea how to set color, maybe later (They changed the API, it used to be with add_theme_color, no longer accepts it. Ref: https://dearpygui.readthedocs.io/en/latest/reference/dearpygui.html#dearpygui.dearpygui.add_progress_bar ###
                    dpg.add_text("", tag="tcp_percentage")

                    dpg.add_spacer(height=20)

                    ### UDP ###
                    dpg.add_text("", tag="udp_total")
                    dpg.add_progress_bar(default_value=0.0, tag="udp_bar", width=300)
                    dpg.add_text("", tag="udp_percentage")

                    ### Top 5 SRC ###
                    dpg.add_spacer(height=20)
                    with dpg.group(horizontal=True):
                        with dpg.child_window(width=250, height=250):
                            dpg.add_text("Top 5 IP de ORIGEN (SRC)", bullet=True)
                            dpg.add_text("", tag="top_sources")

                        ### Top 5 DST -> One group as it's one API request ###
                        with dpg.child_window(width=250, height=250):
                            dpg.add_text("Top 5 IP de DESTINO (DST)", bullet=True)
                            dpg.add_text("", tag="top_destinations")

                    ### Add Error Log Section (below other sections) ### 
                    with dpg.group(horizontal=False):
                        with dpg.child_window(width=-1, height=200):
                            dpg.add_spacer(height=10)
                            dpg.add_text("Error Log", bullet=True)
                            dpg.add_text("", tag="error_log", wrap=530, color=(255, 0, 0))

    ### Start thread as background ###
    data_thread = threading.Thread(target=fetch_data, daemon=True) ### Daemon thread, closes when main thread closes ###
    data_thread.start()

'''
Gui cleanup, refer to docs here:
https://dearpygui.readthedocs.io/en/latest/tutorials/first-steps.html
'''

dpg.create_viewport(title="Detector de Paquetes (TCP_UDP)", width=1200, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

'''
CPU rendering example below, not used in the end
'''

# import tkinter as tk

# # Create the main window
# root = tk.Tk()
# root.title("Simple GUI")
# root.geometry("400x300")

# # Create a label and pack it
# label = tk.Label(root, text="This is a CPU-rendered GUI!")
# label.pack(pady=50)

# # Start the main event loop
# root.mainloop()
