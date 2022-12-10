import socket
import select

identities = []
clients = []

details_game = 'Jocul \"Spanzuratoare\"\nCuvântul ce trebuie ghicit este reprezentat de un șir de linii, fiecare' \
               'linie reprezentând o literă a cuvântului. Daca trimiteti o litera ce se află în cuvânt aceasta va' \
               'apărea pe toate pozitile corespunzatoare, in caz contrat numarul de vieti/greseli va scadea cu 1. In' \
               'cazul in  care v-ati dat seama ce cuvant este, scrieti: Cuvantul intreg: cuvantul\n' \
               'Comenzi: Start game, Reset game, Details, Cuvantul intreg '

word = []
definition = ''
word_scheme = []
start_game = 0
lives = 0


# modificam schema si numarul de vieti in functie de prezenta sau nu a literei in cuvant
def word_scheme_change(letter):
    global word, word_scheme, lives
    gasit = 0
    for i in range(0, len(word)):
        if word[i] == letter:
            word_scheme[i] = letter
            gasit = 1
    if gasit == 0:
        lives -= 1
    if word_scheme.count('_') == 0:
        return 1
    return 0


def game_init(given_word, given_definition):
    global word, word_scheme, definition
    word_scheme = ['_' for x in given_word]
    word = [x for x in given_word]
    definition = given_definition


# apelarea functiilor, modificarea variabilelor in functie de mesajul primit
def process_data(sock, message):
    global word, definition, word_scheme, start_game, lives
    position = clients.index(sock)
    identity = identities[position]
    if identity == 'client2':
        if message.decode('utf-8') == 'Start game' or message.decode('utf-8') == 'Reset game':
            start_game = 1
            positiontosend = identities.index('client1')
            clients[positiontosend].send('Trimite un cuvant si definitia sa'.encode('utf-8'))
        elif message.decode('utf-8') == 'Details':
            sock.send(details_game.encode('utf-8'))
        elif 'Cuvantul intreg:' in message.decode('utf-8'):
            if start_game == 1:
                decodedmessage = message.decode('utf-8')
                extractguess = decodedmessage.split(': ')
                wordguess = extractguess[1]
                if wordguess == ''.join(word):
                    sock.send('Felicitari ati ghicit cuvantul!'.encode('utf-8'))
                    start_game = 0
                else:
                    scheme = ''.join(word_scheme)
                    lives -= 1
                    if lives >= 1:
                        message_to_send = 'Cuvantul nu este corect\n' + scheme + str(lives)
                    else:
                        message_to_send = 'Cuvantul nu este corect. Ati pierdut jocul!'
                        start_game = 0
                    sock.send(message_to_send.encode('utf-8'))
            else:
                sock.send('Mai intai incepeti un nou joc. Comanda: Start game'.encode('utf-8'))
        else:
            if start_game == 1:
                if len(message.decode('utf-8')) > 1:
                    sock.send('Trimiteti o singura litera'.encode('utf-8'))
                else:
                    if word_scheme_change(message.decode('utf-8')) == 1:
                        sock.send('Felicitari ati ghicit cuvantul!'.encode('utf-8'))
                        start_game = 0
                    else:
                        if lives >= 1:
                            message_to_send = ''.join(word_scheme)
                            message_to_send = message_to_send + str(lives)
                        else:
                            message_to_send = 'Ati pierdut jocul!'
                            start_game = 0
                        sock.send(message_to_send.encode('utf-8'))
            else:
                sock.send('Mai intai incepeti un nou joc. Comanda: Start game'.encode('utf-8'))
    else:
        if message.decode('utf-8') != 'Pregatit':
            if message.decode('utf-8').count(':') != 1:
                sock.send("Respectati formatul- cuvant: definitie\nTrimite un cuvant si definitia sa".encode('utf-8'))
            else:
                decodedmessage = message.decode('utf-8')
                wordanddef = decodedmessage.split(':')
                extractword = wordanddef[0]
                extractdefinition = wordanddef[1]
                positiontosend = identities.index('client2')
                start_game = 1
                if len(extractword) < 9:
                    lives = len(extractword)
                else:
                    lives = len(extractword) - 2
                game_init(extractword, extractdefinition)
                message_to_send = extractdefinition + ' ' + ''.join(word_scheme) + str(lives)
                clients[positiontosend].send(message_to_send.encode('utf-8'))


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
    end = 0
    while True:
        try:
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
                    data = r_sock.recv(RECV_BUFFER)
                    if data:
                        if data.decode('utf-8') != 'End game':
                            process_data(r_sock, data)
                        else:
                            position_end = clients.index(r_sock)
                            identity_end = identities[position_end]
                            if identity_end == 'client1':
                                position_to_send = identities.index('client2')
                                clients[position_to_send].send('End game'.encode('utf-8'))
                            else:
                                position_to_send = identities.index('client1')
                                clients[position_to_send].send('End game'.encode('utf-8'))
                            end = 1
                            break
            if end == 1:
                server_socket.close()
                break
        except KeyboardInterrupt:
            print("Game end")
            end = 1
