import socket

HOST = '127.0.0.1'
PORT = 2000

identity = 'client2'
ClientSocket = socket.socket()
print('Waiting for connection')
try:
    ClientSocket.connect((HOST, PORT))
except socket.error as e:
    print(str(e))
while True:
    message = ClientSocket.recv(2048).decode('utf-8')
    if message == 'Declara-ti identitatea:':
        ClientSocket.send(identity.encode('utf-8'))
    else:
        print(message)
        message_to_send = input('Comanda: ')
        ClientSocket.send(message_to_send.encode('utf-8'))
