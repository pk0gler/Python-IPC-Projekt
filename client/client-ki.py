import socket
from enum import Enum
import sys


class KI(object):
    def __init__(self, argv):
        if len(argv) != 4:
            raise ValueError("Please specify port as in >>python client-k1.py -p 5050 -s 10<<")
        # Set port globally
        if argv[0] == "-p":
            self.port = int(argv[1])
            if argv[2] == "-s":
                self.size = int(argv[3])
            else:
                raise ValueError("Please specify port as in >>python client-k1.py -p 5050 -s 10<<")
        else:
            raise ValueError("Please specify port as in >>python client-k1.py -p 5050 -s 10<<")
        # Initiate Connection
        self.connect()

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
            self.clientsocket = clientsocket
            try:
                # Verbindung herstellen (Gegenpart: accept() )
                clientsocket.connect(('localhost', self.port))
                msg = input("Name?")
                # Nachricht schicken
                clientsocket.send(msg.encode())
                # Antwort empfangen
                data = clientsocket.recv(1024).decode()
                if not data or not data == "OK":
                    # Schließen, falls Verbindung geschlossen wurde
                    clientsocket.close()
                else:
                    print("Verbunden ueber port " + str(self.port))
                    self.map_matr =[[0 for x in range(self.size)] for y in range(self.size)]
                    self.steps = 0
                    while True:
                        if self.rec_fields():
                            break
            except socket.error as serr:
                print("Socket error: " + serr.strerror)

    def rec_fields(self):
        data = self.clientsocket.recv(1024).decode()
        fields = None
        if not data:
            print("Connection closed")
            return True
        if self.steps != 0:
            self.steps += 1
        if len(data) == 50:
            print(data[0:10])
            print(data[10:20])
            print(data[20:30])
            print(data[30:40])
            print(data[40:50])
        elif len(data) == 18:
            ''''
            print(data[0:6])
            print(data[6:12])
            print(data[12:18])
            '''
            data = str(data).replace(" ", "")
            print(data)
            fields = [[0 for x in range(3)] for y in range(3)]
            for x in range(0,3):
                temp = data[x * 3: (x * 3) + 3]
                for y in range(0,3):
                    fields[x][y] = temp[y]
            for i in fields:
                print(i)
            self.add_to_map(fields)
        elif len(data) == 98:
            print(data[0:14])
            print(data[14:28])
            print(data[28:42])
            print(data[42:56])
            print(data[56:70])
            print(data[70:84])
            print(data[84:98])
        else:
            # Lose / Win
            print(data)
            return True
        return False

    def add_to_map(self, fields):
        field_size = len(fields)
        if self.steps == 0:
            for x in range(0,field_size):
                for y in range(0,field_size):
                    self.map_matr[x][y] = fields[x][y]
        else:
            print(self.steps)

        for i in self.map_matr:
            print(i)


class CommandType(Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"


if __name__ == '__main__':
    KI = KI(sys.argv[1:])
