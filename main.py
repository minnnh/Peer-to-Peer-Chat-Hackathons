import sys
import socketserver

from server import P2PServer
from client import Client

if __name__ == '__main__':
    try:
        host_name = sys.argv[1]
        if host_name == 'server':
            HOST, PORT = "127.0.0.1", 65432
            with socketserver.ThreadingTCPServer((HOST,PORT), P2PServer) as server:
                server.serve_forever()

        elif host_name == 'client1':
            client1 = Client("127.0.0.1", 60410, "127.0.0.1", 65432)
            client1.update_clients_from_server()
            client1.listen()
            client1.close_all_socket()

        elif host_name == 'client2':
            client2 = Client("127.0.0.1", 60420, "127.0.0.1", 65432)
            client2.update_clients_from_server()
            client2.connect_to_first_client()
            client2.close_all_socket()

        else:
            print('Wrong args input')
    except Exception as e:
        print('Wrong input args,', e)