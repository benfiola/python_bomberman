import sys
from common import client_configuration
from client import Client

if __name__ == "__main__":
    sys.exit(Client(client_configuration).run())


