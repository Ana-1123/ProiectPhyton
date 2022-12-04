import socket
import select

identities = []
clients = []


def process_data(sock, message):
            print(message)
            sock.send('Mesaj primit'.encode('utf-8'))


if __name__ == "__main__":

    CONNECTION_LIST = []
    RECV_BUFFER = 2048
    HOST = '127.0.0.1'
    PORT = 2000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    CONNECTION_LIST.append(server_socket)

    print("Game server started on port " + str(PORT))

    while True:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

        for r_sock in read_sockets:
            # conectare noua la server
            if r_sock == server_socket:
                sock_conn, address = server_socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                sock_conn.send('Declara-ti identitatea:'.encode('utf-8'))
                identity = sock_conn.recv(1024).decode('utf-8')
                print(identity)
                identities.append(identity)
                clients.append(sock_conn)
                sock_conn.send('Connected to server! For details write Details.'.encode('utf-8'))
                CONNECTION_LIST.append(sock_conn)
            # mesaj de la clienti
            else:
                try:
                    data = r_sock.recv(RECV_BUFFER)
                    if data:
                        process_data(r_sock, data)
                except socket.error as e:
                    print(str(e))
