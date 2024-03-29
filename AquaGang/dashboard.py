from PyQt6.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QGroupBox, QGridLayout, QVBoxLayout, QMainWindow, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6 import QtWidgets, uic, QtGui
import sys

from fishFrame import FishFrame


class Dashboard(QMainWindow):

    def __init__(self, allFish=None, allPondsNum=None):
        super().__init__()
        self.fished = allFish
        self.allPondsNum = allPondsNum
        # print(self.fished[0].getId())
        self.initUI()

    def initUI(self):

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()         # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.grid = QGridLayout()

        # temp = ["Fish ID: 123", "State: In Pond", "Status: alive", "Genesis: Sick-Salmon", "Crowd Threshold: 5/10", "Pheromone Level: 4/5", "Lifetime: 30/60"]
        # print(self.fished[0].getFishData().getGenesis())
        num = len(self.fished)
        j=0
        temp=0
        i=0
        label = QLabel("Pond Population : "+ str(len(self.fished)) + "/" + str(self.allPondsNum) + " (" + str(int((len(self.fished)/self.allPondsNum) * 100)) + "%)",self)
        font = label.font();
        font.setPointSize(30);
        font.setBold(True);
        label.setFont(font);
        for r in range(0,num): 
            # print("out", i, temp, j)
            while j < 2 and i < num:       
                # print("here", i, temp, j)
                info = [self.fished[i].getFishData().getId(), self.fished[i].getFishData().getState(), 
                self.fished[i].getFishData().getStatus(), self.fished[i].getFishData().getGenesis(), str(self.fished[i].getFishData().lifetime)]
                self.grid.addWidget(FishFrame(info, self.widget), temp, j)
                i+=1     
                j+=1
            j=0
            temp+=1
            
        self.vbox.addWidget(label)
        self.vbox.addLayout(self.grid)

        self.widget.setLayout(self.vbox)


        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(0, 290, 500, 700)
        self.setWindowTitle('Dashboard')
        self.show()

        return