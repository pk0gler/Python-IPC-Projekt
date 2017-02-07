import socket
import time

import sys

from client.implementation import *

class Node(object):
    def __init__(self, x, y, val):
        self.coor = (x, y)
        self.value = val
        self.calc_weight()
        self.visited = False
        self.get_new = 0
        if self.value != "L":
            self.passable = True
        else:
            self.passable = False

    def __repr__(self):
        return "x" + str(self.coor[0]) + ",y" + str(self.coor[1]) + ":" + self.value + " "

    def __repr_only_val__(self):
        return str(self.value + " ")

    def __lt__(self, other):
        return self.coor.__lt__(other.coor)

    def calc_weight(self):
        if self.value == "M":
            self.weight = 2
        elif self.value == "L":
            self.weight = 100
        else:
            self.weight = 1


def create_commands(path, start):
    prevx = start[0]
    prevy = start[1]
    commands = []
    for i in path:
        print(i, prevx, ",", prevy)
        if prevx != i[0]:
            if (i[0] - 1) % size_x == prevx:
                commands.append("right")
            else:
                commands.append("left")
        else:
            if (i[1] - 1) % size_y == prevy:
                commands.append("down")
            else:
                commands.append("up")
        prevx = i[0]
        prevy = i[1]
    return commands


def calc_possible_new_fields(val, coor, map):
    my_range = 0
    if "G" in val:
        my_range = 5
    elif "M" in val:
        my_range = 7
    elif "L" in val:
        my_range = 0
    else:
        my_range = 3

    fields_in_range = []

    for y in range(coor[1] - (my_range // 2), coor[1] + (my_range // 2 + 1)):
        for x in range(coor[0] - (my_range // 2), coor[0] + (my_range // 2 + 1)):
            coor_temp = (x % size_x, y % size_y)
            if coor_temp != coor:
                fields_in_range.append(coor_temp)

    # calculate whether those field are new fields or not
    for i in fields_in_range:
        for y in range(size_y):
            for x in range(size_x):
                temp = map[y][x]
                if type(temp) == Node:
                    if temp.coor == i:
                        for ii in range(len(fields_in_range)):
                            if fields_in_range[ii] == temp.coor:
                                fields_in_range[ii] = 0
                else:
                    pass

    fields_in_range = [x for x in fields_in_range if x != 0]

    return len(fields_in_range)


def reverse_command(prev_command):
    if prev_command == "up":
        return "down"
    elif prev_command == "down":
        return "up"
    elif prev_command == "left":
        return "right"
    elif prev_command == "right":
        return "left"


def main(argv):
    """ init-Method

            Method acts as the Constructor initiates all variables

            @:param argv: Arguments passed by the User
    """
    global ip, port, size_x, size_y
    global timeout
    timeout = 0.02
    if len(argv) == 0:
        raise ValueError("Please specify port as in >>python client-k1.py -p 5050 -s 10<<")
    # Set port globally
    try:
        ip = argv[1]
        port = int(argv[3])
        size_x = int(argv[5])
        size_y = int(argv[7])

    except Exception as e:
        raise ValueError("Invalid Arguments")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
        try:
            clientsocket.connect((ip, port))
            name = "test"
            clientsocket.send(name.encode())
            data = clientsocket.recv(1024).decode()
            if not data or not data == "OK":
                clientsocket.close()
            else:
                print("Connected as " + name)
                # define necessary variables
                prev_command = None
                map = [[0 for x in range(size_x)] for y in range(size_y)]
                prev_x = 0
                prev_y = 0
                steps = 0
                graph = GridWithWeights(size_x, size_y)
                have_bomb = False
                while True:
                    data = clientsocket.recv(1024).decode()
                    if "You" in data:
                        print("Steps needed: ", steps)
                        sys.exit(0)
                    print("received data: " + data)
                    print()
                    # Correct bomb in string
                    temp = ""
                    if "B" in data:
                        for i in data:
                            if i == "B":
                                temp += "B "
                            else:
                                temp += i
                        data = temp.split(" ")
                    else:
                        data = data.split(" ")
                    del data[-1]
                    print("Corrected data and splited: ", data)

                    # bring in correct 2 dimensional form
                    if len(data) % 3 == 0:
                        # it is forest or start point
                        temp_size = 3

                    elif len(data) % 5 == 0:
                        temp_size = 5

                    elif len(data) % 7 == 0:
                        temp_size = 7

                    else:
                        # Lose / Win
                        print(data)
                    fields = [[0 for x in range(temp_size)] for y in range(temp_size)]
                    for y in range(temp_size):
                        temp = data[y * temp_size: (y * temp_size) + temp_size]
                        for x in range(0, temp_size):
                            print(x, "stelle")
                            print(temp_size)
                            val = temp[x]
                            fields[y][x] = Node(x, y, val)

                    print()
                    print("Received Fields")
                    for i in fields:
                        print(i.__repr__())

                    # save received fields into map
                    if steps == 0:
                        pass
                    # for x in range(len(fields)):
                    #         for y in range(len(fields)):
                    #             temp_node = fields[x][y]
                    #             temp_node.coor = (x-1,y-1)
                    #             map[x-1][y-1] = temp_node

                    else:
                        if prev_command == "up":
                            prev_y -= 1
                        elif prev_command == "down":
                            prev_y += 1
                        elif prev_command == "left":
                            prev_x -= 1
                        elif prev_command == "right":
                            prev_x += 1

                    prev_x = prev_x % size_x
                    prev_y = prev_y % size_y

                    # in der map speichern
                    for y in range(0, len(fields)):
                        for x in range(0, len(fields)):
                            node_temp = fields[y][x]
                            node_temp.coor = ((x - len(fields) // 2 + prev_x) % size_x, (y - len(fields) // 2 + prev_y) % size_y)
                            if "C" in node_temp.value and node_temp.coor != (0,0):
                                node_temp.value = "EC"
                                print("enemy castle found")
                            map[(y - len(fields) // 2 + prev_y) % size_x][(x - len(fields) // 2 + prev_x) % size_y] = node_temp

                    map[prev_y][prev_x].visited = True

                    # graph fuer a* neu beurteilen
                    for y in range(size_y):
                        for x in range(size_x):
                            node = map[y][x]
                            if type(node) == Node:
                                if not node.passable:
                                    graph.walls.append(node.coor)
                                graph.weights[node.coor] = node.weight

                    print()
                    print("new map is:")
                    for i in map:
                        print(i)

                    bomb_node = None

                    # map felder bewerten
                    queue = PriorityQueue()
                    for y in range(size_y):
                        for x in range(size_x):
                            node = map[y][x]
                            if type(node) == Node:
                                if "B" in node.value and have_bomb == False:
                                    print("bombe gefunden in die queue rein")
                                    queue.put(node, -1000000000)
                                    bomb_node = node.coor
                                elif "EC" in node.value and have_bomb == True:
                                    print("Gehe zu EC")
                                    queue.put(node, -1000000000)
                                else:
                                    poss_fields = calc_possible_new_fields(node.value, node.coor, map)
                                    way_to_field = heuristic(node.coor, (prev_x, prev_y))
                                    queue.put(node, (poss_fields * -1) + way_to_field)
                                    print(poss_fields, "for field:", node)
                                    print("way to field:", way_to_field)
                                    print()


                    next_node = queue.get()
                    start = (prev_x, prev_y)
                    goal = next_node.coor

                    if start == bomb_node:
                        print("im on bomb")
                        print("Ich habe ", steps, " Schritte gebrauchbt")
                        bomb_node = start

                        have_bomb = True

                        queue = PriorityQueue()
                        for y in range(size_y):
                            for x in range(size_x):
                                node = map[y][x]
                                if type(node) == Node:
                                    if "B" in node.value and have_bomb == False:
                                        print("bombe gefunden in die queue rein")
                                        queue.put(node, -1000000000)
                                        bomb_node = node.coor
                                    elif "EC" in node.value and have_bomb == True:
                                        print("Gehe zu EC")
                                        queue.put(node, -1000000000)
                                    else:
                                        poss_fields = calc_possible_new_fields(node.value, node.coor, map)
                                        way_to_field = heuristic(node.coor, (prev_x, prev_y))
                                        queue.put(node, poss_fields * -1)
                                        print(poss_fields, "for field:", node)
                                        print("way to field:", way_to_field)
                                        print()

                        next_node = queue.get()
                        start = (prev_x, prev_y)
                        goal = next_node.coor

                    # zum naechsten node gehen
                    came_from, cost_so_far = a_star_search(graph, start, goal)
                    draw_grid(graph, width=3, point_to=came_from, start=start, goal=goal)
                    print()
                    draw_grid(graph, width=3, number=cost_so_far, start=start, goal=(x, y))
                    print()
                    path = reconstruct_path(came_from, start=start, goal=goal)[2:]
                    draw_grid(graph, width=3, path=path)
                    commands = create_commands(path, start)
                    print(commands)
                    print("want to go to field:" , next_node)
                    print("iam on field", start)


                    clientsocket.send(commands[0].encode())
                    prev_command = commands[0]
                    #clientsocket.send(eing.encode())
                    #prev_command = eing
                    time.sleep(timeout)
                    steps += 1

        except socket.error as serr:
            print("Socket error: " + serr.strerror)

if __name__ == "__main__":
    main(sys.argv[1:])
