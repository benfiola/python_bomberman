import sys
from common import ClientConfiguration, HostConfiguration, get_logger
from client import Client
from client.custom_events import *
from host import Host
import threading

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Running test")

    c_config1 = ClientConfiguration(socket_data=('localhost', 20002))
    c_config2 = ClientConfiguration(socket_data=('localhost', 20003))
    h_config = HostConfiguration(socket_data=('localhost', 20001))

    client = Client(c_config1)

    client_thread = threading.Thread(name="Client", target=client.run)
    client_thread.start()
    client.push_custom_event(CreateHost(h_config))
    client.push_custom_event(ConnectToHost(h_config))
    client.push_custom_event(DisconnectFromHost())
    client.push_custom_event(CreateHost(h_config))
    client.push_custom_event(ConnectToHost(h_config))
    client.push_custom_event(DisconnectFromHost())