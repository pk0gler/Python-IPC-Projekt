"""
The KI Class generates autoamated algorithms to find the perfect
way to play the IPC-Game.
Obviously it will always defeat a human being.
"""
import socket
import sys
from enum import Enum

from client.implementation import *


class KI(object):
    """

    """

    def __init__(self, argv):
        """ init-Method

        Method acts as the Constructor initiates all variables

        @:param argv: Arguments passed by the User
        """
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
        self.graph = GridWithWeights(self.size, self.size)
        self.map_matr = [[0 for x in range(self.size)] for y in range(self.size)]
        self.steps = 0
        # Initiate Connection
        self.connect()

    def connect(self):
        """ Connect Method

        TO connect Client with Server on specified Port

        :return:
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
            self.clientsocket = clientsocket
            try:
                # Verbindung herstellen (Gegenpart: accept() )
                clientsocket.connect(('localhost', self.port))
                msg = "kogler"
                # Nachricht schicken
                clientsocket.send(msg.encode())
                # Antwort empfangen
                data = clientsocket.recv(1024).decode()
                if not data or not data == "OK":
                    # Schließen, falls Verbindung geschlossen wurde
                    clientsocket.close()
                else:
                    print("Verbunden ueber port " + str(self.port))
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

        data = self.seperate_bomb(data)

        if len(data) % 3 == 0:
            # it is forest or start point
            temp_size = 3
            self.type = FieldType(FieldType.FOREST)

        elif len(data) % 5 == 0:
            temp_size = 5
            self.type = FieldType(FieldType.GRAS)

        elif len(data) % 7 == 0:
            temp_size = 7
            self.type = FieldType(FieldType.MOUNTAIN)

        else:
            # Lose / Win
            print(data)
            return True

        fields = [[0 for x in range(temp_size)] for y in range(temp_size)]
        for x in range(0, temp_size):
            temp = data[x * temp_size: (x * temp_size) + temp_size]
            for y in range(0, temp_size):
                fields[x][y] = temp[y]

        self.add_to_map(fields)
        return False

    def seperate_bomb(self, data):
        if "B" in data:
            data = data.replace("B", "B ")
            data = data.split(" ")
            return data[:len(data) - 1]
        else:
            data = data.split(" ")
            return data[:len(data) - 1]

    def add_to_map(self, fields):
        for i in fields:
            print(i)
        print("--")
        field_size = len(fields)
        if self.steps == 0:
            self.prev_x = 0
            self.prev_y = 0

            for x in range(0, field_size):
                for y in range(0, field_size):
                    self.map_matr[x - 1][y - 1] = fields[x][y]
                    self.graph.weights.update(
                        {((x - 1) % self.size, (y - 1) % self.size): self.type.get_weight(fields[x][y])})

        else:
            if self.command == CommandType.UP.value.encode():
                self.prev_y -= 1
                self.prev_x = self.prev_x

            if self.command == CommandType.DOWN.value.encode():
                self.prev_y += 1
                self.prev_x = self.prev_x

            if self.command == CommandType.LEFT.value.encode():
                self.prev_y = self.prev_y
                self.prev_x -= 1

            if self.command == CommandType.RIGHT.value.encode():
                self.prev_y = self.prev_y
                self.prev_x += 1

        for x in range(0, field_size):
            for y in range(0, field_size):
                self.map_matr[x - field_size // 2 + self.prev_y][y - field_size // 2 + self.prev_x] = fields[x][y]
                self.graph.weights.update({((x - field_size // 2 + self.prev_y) % self.size,
                                            (y - field_size // 2 + self.prev_x) % self.size): self.type.get_weight(
                    fields[x][y])})

        for i in self.map_matr:
            print(i)

        print("-")

        print(self.graph.weights)

        for i in range(self.size):
            for j in range(self.size):
                if self.map_matr[i][j] == "L":
                    self.graph.walls.append((j, i))
                    print(j, i, "asd")

        print("-")

        print(self.graph.walls)

        self.make_choice()

    def make_choice(self):
        command = input("wo?")
        # if "B" in self.map_matr:
        #     print("bombe")
        #     command = CommandType.DOWN.value.encode()
        # else:
        #     command = CommandType.DOWN.value.encode()
        self.react(command.encode())

    def react(self, command):
        # print(command)
        self.clientsocket.send(command)
        a_star = input("a*?")
        if a_star == "j":
            x = int(input("wohin: x"))
            y = int(input("wohin: y"))
            came_from, cost_so_far = a_star_search(self.graph, (self.prev_x, self.prev_y), (x, y))

            draw_grid(self.graph, width=3, point_to=came_from, start=(self.prev_x, self.prev_y), goal=(x, y))
            print()
            draw_grid(self.graph, width=3, number=cost_so_far, start=(self.prev_x, self.prev_y), goal=(x, y))
            print()
            draw_grid(self.graph, width=3,
                      path=reconstruct_path(came_from, start=(self.prev_x, self.prev_y), goal=(x, y)))
            self.create_commandos(reconstruct_path(came_from, start=(self.prev_x, self.prev_y), goal=(x, y))[2:])

        self.steps += 1
        self.command = command

    def create_commandos(self, path):
        prevx = self.prev_x
        prevy = self.prev_y
        print(prevx, prevy)
        commands = []
        for i in path:
            actx = i[0]
            acty = i[1]
            if prevx != actx:
                if actx > prevx:
                    commands.append("right")
                else:
                    commands.append("left")
            elif prevy != acty:
                if acty > prevy:
                    commands.append("down")
                else:
                    commands.append("up")

        print(commands)


class CommandType(Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"


class FieldType(Enum):
    CENTER = {'short': 'C', 'sight': 3}
    FOREST = {'short': 'F', 'sight': 3}
    GRAS = {'short': 'G', 'sight': 5}
    MOUNTAIN = {'short': 'M', 'sight': 7}
    LAKE = {'short': 'L', 'sight': 0}

    def get_weight(self, type):
        if type == "C":
            return 1
        elif type == "F":
            return 2
        elif type == "G":
            return 1
        elif type == "M":
            return 2
        elif type == "L":
            return 0


if __name__ == '__main__':
    KI = KI(sys.argv[1:])
