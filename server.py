import socket
import select

identities = []
clients = []
details_client1 = 'Jocul \"Spanzuratoare\"\nRolul pe care il aveti este de a trimite un cuvant cu o mica definitie,' \
                  ' la cerere. Structura ce trebuie respectata este urmatoarea: scrieti cuvantul, doua puncte-:, ' \
                  'un spatiu si definitia. De exemplu "ninsoare: Precipitație atmosferică sub formă de fulgi ' \
                  'compuși din cristale de gheață"'
details_client2 = 'Jocul \"Spanzuratoare\"\nRolul pe care il aveti este de ghici un cuvant. Vi se va oferi definitia ' \
                  'acestuia. Veti trimite cate o litera si vi se va spune daca aceasta face face parte din cuvant ' \
                  'sau nu, veti putea vizualiza si numarul de litere pe care il are cuvantul si literile ghicite ' \
                  'corespunzator asezate. In cazul in care v-ati dat seama ce cuvant este, scrieti: Cuvantul intreg:' \
                  ' cuvantul\nComenzi: Start game, Reset game, Details '
word = []
definition = ''
wordscheme = []
startgame = 0
lives = 0


def wordschemechange(letter):
    global word, wordscheme, lives
    gasit = 0
    for i in range(0, len(word)):
        if word[i] == letter:
            wordscheme[i] = letter
            gasit = 1
    if gasit == 0:
        lives -= 1
    if wordscheme.count('_') == 0:
        return 1
    return 0


def gameinit(givenword, givendefinition):
    global word, wordscheme, definition
    wordscheme = ['_' for x in givenword]
    word = [x for x in givenword]
    definition = givendefinition


def process_data(sock, message):
    global word, definition, wordscheme, startgame, lives
    position = clients.index(sock)
    identity = identities[position]
    if identity == 'client2':
        if message.decode('utf-8') == 'Start game' or message.decode('utf-8') == 'Reset game':
            startgame = 1
            positiontosend = identities.index('client1')
            clients[positiontosend].send('Trimite cuvant si definitie'.encode('utf-8'))
        elif message.decode('utf-8') == 'Details':
            sock.send(details_client2.encode('utf-8'))
        elif 'Cuvantul intreg:' in message.decode('utf-8'):
            if startgame == 1:
                decodedmessage = message.decode('utf-8')
                extractguess = decodedmessage.split(': ')
                wordguess = extractguess[1]
                if wordguess == ''.join(word):
                    sock.send('Felicitari ati ghicit cuvantul!'.encode('utf-8'))
                    startgame = 0
                else:
                    scheme = ''.join(wordscheme)
                    lives -= 1
                    if lives >= 1:
                        message_to_send = 'Cuvantul nu este corect\n' + scheme + str(lives)
                    else:
                        message_to_send = 'Cuvantul nu este corect. Ati pierdut jocul!'
                    sock.send(message_to_send.encode('utf-8'))
            else:
                sock.send('Mai intai incepeti un nou joc. Comanda: Start game'.encode('utf-8'))
        else:
            if startgame == 1:
                if len(message.decode('utf-8')) > 1:
                    sock.send('Trimiteti o singura litera'.encode('utf-8'))
                else:
                    if wordschemechange(message.decode('utf-8')) == 1:
                        sock.send('Felicitari ati ghicit cuvantul!'.encode('utf-8'))
                        startgame = 0
                    else:
                        if lives >= 1:
                            message_to_send = ''.join(wordscheme)
                            message_to_send = message_to_send + str(lives)
                        else:
                            message_to_send = 'Ati pierdut jocul!'
                        sock.send(message_to_send.encode('utf-8'))
            else:
                sock.send('Mai intai incepeti un nou joc. Comanda: Start game'.encode('utf-8'))
    else:
        if message.decode('utf-8') != 'Pregatit':
            if message.decode('utf-8') == 'Details':
                sock.send(details_client1.encode('utf-8'))
            else:
                decodedmessage = message.decode('utf-8')
                wordanddef = decodedmessage.split(':')
                extractword = wordanddef[0]
                extractdefinition = wordanddef[1]
                positiontosend = identities.index('client2')
                startgame = 1
                if len(extractword) < 9:
                    lives = len(extractword)
                else:
                    lives = len(extractword) - 2
                gameinit(extractword, extractdefinition)
                message_to_send = extractdefinition + ' ' + ''.join(wordscheme) + str(lives)
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
