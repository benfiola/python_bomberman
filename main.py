import sys
from common import client_configuration
from client import Client

if __name__ == "__main__":
    code = 0
    client = Client(client_configuration)
    try:
        code = client.run()
    except KeyboardInterrupt as e:
        if client is not None:
            client.shut_down()
    sys.exit(code)


