import sys, socket, threading
from PySide import QtCore , QtGui
from enum import Enum
import random

from server import ServerView_2


class FieldType(Enum):
    GRASS = 0
    CASTLE1 = 1
    CASTLE2 = 2
    FOREST = 3
    MOUNTAIN = 4
    LAKE = 5

class CommandType(Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"


class ServerController(QtGui.QWidget):
    """
    Der Spieleserver
    """
    errorsignal = QtCore.Signal((str,))
    msgsignal = QtCore.Signal()
    pCastle1 = QtGui.QPalette(QtCore.Qt.black)
    pCastle1.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)

    pCastle2 = QtGui.QPalette(QtCore.Qt.white)
    pCastle2.setColor(QtGui.QPalette.WindowText, QtCore.Qt.red)

    temp = QtGui.QPalette(QtCore.Qt.blue)
    print(temp.color(QtGui.QPalette.Base))
    print(temp.color(QtGui.QPalette.Text))

    pGrass = QtGui.QPalette(QtCore.Qt.green)
    pForest = QtGui.QPalette(QtCore.Qt.darkGreen)
    pLake = QtGui.QPalette(QtCore.Qt.darkBlue)
    pMountain = QtGui.QPalette(QtCore.Qt.darkGray)
    def __init__(self, parent=None):
        """
        Create a new controller with a MyView object
        using the MVC pattern

        :param parent:
        :return: None
        """
        super().__init__(parent)
        self.myForm = ServerView_2.Ui_Form()
        self.myForm.setupUi(self)

        self.rows = 10
        self.cols = 10

        self.prev_widget_pl1 = None
        self.prev_widget_pl2 = None

        self.myForm.horizontalSlider.setRange(5, (self.rows * self.cols) - 5)
        self.myForm.horizontalSlider_2.setRange(10, (self.rows * self.cols) - 5)
        self.myForm.horizontalSlider_3.setRange(2, (self.rows * self.cols)//5 - 5)

        self.m_amount = 5
        self.f_amount = 10
        self.l_amount = 2

        self.myForm.btnListen.clicked.connect(self.bind_and_listen)
        self.myForm.pushButton.clicked.connect(self.generate_field_size)
        self.myForm.horizontalSlider.valueChanged.connect(self.valueChangedM)
        self.myForm.horizontalSlider_2.valueChanged.connect(self.valueChangedF)
        self.myForm.horizontalSlider_3.valueChanged.connect(self.valueChangedL)
        self.myForm.btnShuffle.clicked.connect(self.setup_game)

        self.setup_game()
        self.shuffle = False
        self.listening = False

        self.errorsignal.connect(self.showError)
        self.msgsignal.connect(self.draw_map)

    def valueChangedM(self):
        available_fields = (self.rows * self.cols) - 5
        self.m_amount = self.myForm.horizontalSlider.value()
        self.myForm.horizontalSlider_2.setRange(10, available_fields - self.m_amount)
        self.myForm.horizontalSlider_3.setRange(2, available_fields//5 - self.m_amount)
        self.myForm.lineEdit_3.setText(str(self.m_amount))

    def valueChangedF(self):
        available_fields = (self.rows * self.cols) - 5
        available_fields - self.myForm.horizontalSlider.value()
        available_fields - self.myForm.horizontalSlider_3.value()
        self.f_amount = self.myForm.horizontalSlider_2.value()
        self.myForm.horizontalSlider.setRange(5, available_fields - self.f_amount)
        self.myForm.horizontalSlider_3.setRange(2, available_fields//5 - self.f_amount)
        self.myForm.lineEdit_4.setText(str(self.f_amount))

    def valueChangedL(self):
        available_fields = (self.rows * self.cols) - 5
        available_fields - self.myForm.horizontalSlider.value()
        available_fields - self.myForm.horizontalSlider_2.value()
        self.l_amount = self.myForm.horizontalSlider_3.value()
        self.myForm.horizontalSlider.setRange(5, available_fields - self.l_amount)
        self.myForm.horizontalSlider_2.setRange(10, available_fields - self.l_amount)
        self.myForm.lineEdit_5.setText(str(self.l_amount))

    def doSomething(self, event):
        print("haöö")
        print(self.sender())

    def setup_game(self):
        """
        Erzeugt ein neues Spiel und mischt die Felder durch.
        :return: None
        """
        if len(self.myForm.lineEdit.text()) > 0 and len(self.myForm.lineEdit_2.text()) > 0:
            try:
                self.rows = int(self.myForm.lineEdit.text())
                self.cols = int(self.myForm.lineEdit_2.text())
            except Exception:
                self.showError("Hoehe und Breite nur nummerisch bitte")
                self.rows = 10
                self.cols = 10
                self.myForm.lineEdit.setText(str(self.rows))
                self.myForm.lineEdit_2.setText(str(self.cols))

        else:
            self.rows = 10
            self.cols = 10

        self.label_layout = self.myForm.gridLayout

        for i in reversed(range(self.label_layout.count())):
            widget = self.label_layout.itemAt(i).widget()
            widget.setParent(None)

        # Alle Felder auf "Gras" Setze
        self.field = []
        for i in range(self.rows):
            self.field.append([])
            for j in range(self.cols):
                temp = QtGui.QLabel()
                self.label_layout.addWidget(temp,i,j)
                QtCore.QObject.connect(temp, QtCore.SIGNAL(("clicked()")), self.doSomething)
                self.field[i].append(FieldType.GRASS)

        # Burg und Startposition von Spieler 1 setzen
        x = random.randint(2,3)
        y = random.randint(2,3)
        self.field[x][y] = FieldType.CASTLE1
        self.player1 = (x,y)
        self.player1bomb = False
        # Burg und Startposition von Spieler 2 setzen
        x = random.randint(6,7)
        y = random.randint(6,7)
        self.field[x][y] = FieldType.CASTLE2
        self.player2 = (x,y)
        self.player2bomb = False

        # Zufällig 2-10 Teiche platzieren
        lakes = self.l_amount
        while lakes > 0:
            x = random.randint(0,self.rows-1)
            y = random.randint(0,self.cols-1)
            xr = (x+1)%self.rows
            xl = (x-1)%self.rows
            yu = (y+1)%self.cols
            yd = (y-1)%self.cols
            area = [self.field[xl][yu], self.field[x][yu], self.field[xr][yu], self.field[xl][y], self.field[x][y], self.field[xr][y], self.field[xl][yd],
                    self.field[x][yd], self.field[xr][yd]]
            # Es dürfen keine zwei Teiche nebeneinander sein
            if self.field[x][y] == FieldType.GRASS and not FieldType.LAKE in area:
                self.field[x][y] = FieldType.LAKE
                lakes -= 1

        # Zufällig 10 bis 20 Waldstücke erstellen
        forests = self.f_amount
        while forests > 0:
            x = random.randint(0,self.rows-1)
            y = random.randint(0,self.cols-1)
            if self.field[x][y] == FieldType.GRASS:
                self.field[x][y] = FieldType.FOREST
                forests -= 1

        # 3 bis 6 Berge erstellen
        mountains = self.m_amount
        while mountains > 0:
            x = random.randint(0, self.rows-1)
            y = random.randint(0, self.cols-1)
            if self.field[x][y] == FieldType.GRASS:
                self.field[x][y] = FieldType.MOUNTAIN
                mountains -= 1

        # Die Schriftrolle platzieren
        self.bomb = (-1,-1)
        while self.bomb[0]==-1:
            x = random.randint(0, self.rows-1)
            y = random.randint(0, self.cols-1)
            xr = (x+1)%self.rows
            xl = (x-1)%self.rows
            yu = (y+1)%self.cols
            yd = (y-1)%self.cols
            area = [self.field[xl][yu], self.field[x][yu], self.field[xr][yu], self.field[xl][y], self.field[x][y], self.field[xr][y], self.field[xl][yd],
                    self.field[x][yd], self.field[xr][yd]]
            # Die Schriftrolle darf nicht neben einer Burg sein
            if self.field[x][y] != FieldType.LAKE and not FieldType.CASTLE1 in area and not FieldType.CASTLE2 in area:
                self.bomb = (x,y)
        self.shuffle = False
        self.draw_map()

    def draw_map(self):
        """
        Zeichnet die Felder in die entsprechenden Widgets.
        :return: None
        """
        if hasattr(self,'bomblabel'):
            # Beschriftungen fuer Spieler bzw. Schriftrolle zuruecksetzen
            delattr(self, "bomblabel")
            delattr(self, "player1label")
            delattr(self, "player2label")


        for i in range(self.rows):
            for j in range(self.cols):
                # Jeweiliges Widget ermitteln
                widget_y = i
                widget_x = j
                widget = self.label_layout.itemAtPosition(i,j).widget()
                print(widget.text())
                #widget = getattr(self.myForm, "widget_"+str(widget_number))
                widget.setAutoFillBackground(True)

                # Hintergrundfarbe entsprechend setzen
                if self.field[i][j] == FieldType.GRASS:
                    widget.setPalette(self.pGrass)
                elif self.field[i][j] == FieldType.FOREST:
                    widget.setPalette(self.pForest)
                elif self.field[i][j] == FieldType.LAKE:
                    widget.setPalette(self.pLake)
                elif self.field[i][j] == FieldType.MOUNTAIN:
                    widget.setPalette(self.pMountain)
                elif self.field[i][j] == FieldType.CASTLE1:
                    widget.setPalette(self.pCastle1)
                elif self.field[i][j] == FieldType.CASTLE2:
                    widget.setPalette(self.pCastle2)

                # Schriftrolle bzw. Spieler in Widget ggf. schreiben
                temp_font = str(18)
                if self.cols >= 12 and self.rows >= 12:
                    temp_font = 18 - (self.cols - 10) + 3
                    if temp_font <= 5:
                        temp_font = 9

                if self.prev_widget_pl1 != None:
                    self.prev_widget_pl1.setText("")

                if self.prev_widget_pl2 != None:
                    self.prev_widget_pl2.setText("")

                if i == self.bomb[0] and j == self.bomb[1]:
                    self.bomblabel = QtGui.QLabel(widget)
                    widget.setText("<span style=\"font-size:%spt; font-weight:600; color:#cc0000;\">XX</span>"%temp_font)
                    self.bomblabel.show()
                if i == self.player1[0] and j == self.player1[1]:
                    self.player1label = QtGui.QLabel(widget)
                    self.prev_widget_pl1 = widget
                    widget.setPalette(self.temp)
                    if type(widget) == QtGui.QLabel:
                        widget.setText("P2")
                if i == self.player2[0] and j == self.player2[1]:
                    self.player2label = QtGui.QLabel(widget)
                    self.prev_widget_pl2 = widget
                    #self.player2label.setText("<span style=\"font-size:%spt; font-weight:600; color:#cccc00;\">P2</span>"%temp_font)
                    widget.setPalette(self.temp)
                    if type(widget) == QtGui.QLabel:
                        widget.setText("<span style=\"font-size:%spt; font-weight:600; color:#cccc00;\">P2</span>"%temp_font)

                #print(i,j,widget.text())


    def generate_field_size(self):
        if self.myForm.checkBox.isChecked():
            size = random.randint(10,100)
            self.rows = size
            self.cols = size
        else:
            self.rows = random.randint(10,100)
            self.cols = random.randint(10,100)
        self.myForm.lineEdit.setText(str(self.rows))
        self.myForm.lineEdit_2.setText(str(self.cols))

    def bind_and_listen(self):
        """
        Erzeugt einen neuen Thread, welcher auf eingehende
        Verbindungen wartet.
        :return: None
        """
        if not self.listening:
            try:
                self.port = int(self.myForm.linePort.text())
                self.listening = True
                self.myForm.btnListen.setText("Stop")
                if self.shuffle:
                    self.setup_game()
                self.myForm.btnShuffle.setDisabled(True)
                threading.Thread(target=self.__listen_for_clients).start()
            except ValueError:
                self.showError("Bitte geben Sie einen gültigen Port ein!")
        else:
            self.serversocket.close()
            if hasattr(self,"client1"):
                self.client1.close()
                self.shuffle = True
            if hasattr(self,"client2"):
                self.client2.close()
                self.shuffle = True
            self.myForm.listClients.clear()

    def __listen_for_clients(self):
        """
        Wartet auf eingehende Verbindungen und startet ggf. das Spiel.
        :return: None
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.serversocket:
                # Binding erstellen und auf localhost am angegebenen Port horchen
                self.serversocket.bind(('localhost', self.port))
                # Eingehende Verbindungen ab jetzt annehmen (mit maximal 5 pending connections)
                self.serversocket.listen(5)
                print("Auf client warten...")
                (self.client1, address) = self.serversocket.accept()
                with self.client1:
                    # Name von Spieler 1 eingeben und mit "OK" bestaetigen
                    name = self.client1.recv(1024).decode()
                    self.myForm.listClients.addItem(name)
                    self.client1.send("OK".encode())
                    (self.client2, address) = self.serversocket.accept()
                    with self.client2:
                        # Name von Spieler 2 eingeben und mit "OK" bestaetigen
                        name = self.client2.recv(1024).decode()
                        self.myForm.listClients.addItem(name)
                        self.client2.send("OK".encode())
                        self.game_loop()
                # Spiel zuende
                self.myForm.listClients.clear()
                self.myForm.btnListen.setText("Listen")
                self.myForm.btnShuffle.setDisabled(False)
                self.listening = False
                self.shuffle = True
        except Exception as e:
            self.myForm.btnListen.setText("Listen")
            self.listening = False
            self.myForm.btnShuffle.setDisabled(False)
            if e.errno != 10004:
                self.errorsignal.emit("Socket error: " + e.strerror)

    def field_message(self, position):
        """
        Erzeugt die Nachricht, welche alle sichtabren
        Felder des Spielers anzeigt.
        :param position: Position des jeweiligen Spielers
        :type position: (int, int)
        :return: Nachricht mit sichtbaren Felder
        :rtype: str
        """
        sight = 1
        if self.field[position[0]][position[1]] == FieldType.MOUNTAIN:
            sight = 3
        elif self.field[position[0]][position[1]] == FieldType.GRASS:
            sight = 2

        xu = (position[0] - sight) % self.rows
        xd = (position[0] + sight) % self.rows
        yl = (position[1] - sight) % self.cols
        yr = (position[1] + sight) % self.cols

        x = xu
        y = yl
        abort = False
        msg = ''
        while True:
            f = self.field[x][y]
            if f == FieldType.GRASS:
                msg += 'G'
            elif f == FieldType.LAKE:
                msg += 'L'
            elif f == FieldType.FOREST:
                msg += 'F'
            elif f == FieldType.MOUNTAIN:
                msg += 'M'
            elif f == FieldType.CASTLE1 or f == FieldType.CASTLE2:
                msg += 'C'

            if x == self.bomb[0] and y == self.bomb[1]:
                msg += 'B'
            else:
                msg += ' '

            if x == xd and y == yr:
                break
            else:
                if y == yr:
                    y = yl
                    x = (x + 1) % self.rows
                else:
                    y = (y + 1) % self.cols
        return msg

    def game_loop(self):
        """
        Bildet die Spielelogik ab und wickelt die Zuege ab.
        :return: None
        """
        msg = self.field_message(self.player1)
        self.client1.send(msg.encode())
        msg = self.field_message(self.player2)
        self.client2.send(msg.encode())
        skip1 = False
        skip2 = False
        while True:
            # ggf. Zug ueberspringen, falls Berg bestiegen wurde
            if not skip1:
                data = self.client1.recv(1024).decode()
                if data == CommandType.UP.value:
                    self.player1 = ((self.player1[0]-1) % self.rows, self.player1[1])
                elif data == CommandType.DOWN.value:
                    self.player1 = ((self.player1[0]+1) % self.rows, self.player1[1])
                elif data == CommandType.RIGHT.value:
                    self.player1 = (self.player1[0],(self.player1[1]+1) % self.cols)
                elif data == CommandType.LEFT.value:
                    self.player1 = (self.player1[0],(self.player1[1]-1) % self.cols)
                if self.field[self.player1[0]][self.player1[1]] == FieldType.MOUNTAIN:
                    skip1 = True
            else:
                skip1 = False
            if not skip2:
                data = self.client2.recv(1024).decode()
                if data == CommandType.UP.value:
                    self.player2 = ((self.player2[0]-1) % self.rows, self.player2[1])
                elif data == CommandType.DOWN.value:
                    self.player2 = ((self.player2[0]+1) % self.rows, self.player2[1])
                elif data == CommandType.RIGHT.value:
                    self.player2 = (self.player2[0],(self.player2[1]+1) % self.cols)
                elif data == CommandType.LEFT.value:
                    self.player2 = (self.player2[0],(self.player2[1]-1) % self.cols)
                if self.field[self.player2[0]][self.player2[1]] == FieldType.MOUNTAIN:
                    skip2 = True
            else:
                skip2 = False

            # Pruefen, ob Spieler 1 oder Spieler 2 gewonnen bzw. verloren haben
            check1= self.check_position(self.player1, 1)
            check2= self.check_position(self.player2, 2)

            if (check1 == 1 and check2 == 1) or (check1 == -1 and check2 == -1):
                # Unentschieden (beide gewonnen oder beide verloren)
                self.client1.send("Draw".encode())
                self.client2.send("Draw".encode())
                self.msgsignal.emit()
                return
            elif check1 == 1 or check2 == -1:
                # Spieler 1 hat gewonnen
                self.client1.send("You win".encode())
                self.client2.send("You lose".encode())
                self.msgsignal.emit()
                return
            elif check2 == 1 or check1 == -1:
                # Spieler 2 hat gewonnen
                self.client1.send("You lose".encode())
                self.client2.send("You win".encode())
                self.msgsignal.emit()
                return
            else:
                # Nachricht sichtbarer Felder schicken
                if not skip1:
                    msg = self.field_message(self.player1)
                    self.client1.send(msg.encode())
                if not skip2:
                    msg = self.field_message(self.player2)
                    self.client2.send(msg.encode())
                self.msgsignal.emit()

    def check_position(self,position, number):
        """
        Prueft die aktuelle Position und ermittelt, ob das
        Spiel gewonnen oder verloren wurde.
        :param position: Position des Spielers
        :type position: (int, int)
        :param number: Spielernummer (1 oder 2)
        :type number: int
        :return: -1 (verloren), 1 (gewonnen), 0 (weder noch)
        :rtype int
        """
        if self.field[position[0]][position[1]] == FieldType.LAKE:
            # In See gefallen
            return -1
        elif self.field[position[0]][position[1]] == FieldType.CASTLE2 and number==1 and self.player1bomb:
            # Gegnerische Basis mit Schriftrolle erreicht
            return 1
        elif self.field[position[0]][position[1]] == FieldType.CASTLE1 and number==2 and self.player2bomb:
            # Gegnerische Basis mit Schriftrolle erreicht
            return 1

        if position[0]==self.bomb[0] and position[1]==self.bomb[1]:
            if number == 1:
                self.player1bomb = True
                print("Player 1 got the scroll")
            else:
                self.player2bomb = True
                print("Player 2 got the scroll")

        return 0

    def showError(self, message):
        """
        Zeigt Fehlermeldungen an.
        :param message: Anzuzeigende Nachricht.
        :type message: str
        :return: None
        """
        msg = QtGui.QMessageBox()
        msg.setText(message)
        msg.setWindowTitle("Simple Chat Client")
        msg.setIcon(QtGui.QMessageBox.Critical)
        msg.exec_()

    def closeEvent(self, event):
        """
        Reagiert auf das Close-Event und beendet offene Verbindungen.
        :param event:
        :return: None
        """
        self.closing = True
        if hasattr(self,'serversocket'):
            self.serversocket.close()
            if hasattr(self,"client1"):
                self.client1.close()
            if hasattr(self,"client2"):
                self.client2.close()
        event.accept()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    c = ServerController()
    c.show()
    sys.exit(app.exec_())