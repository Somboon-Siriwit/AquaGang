import enum
from re import S
# from turtle import update
from PondData import PondData
from Fish import Fish
# from run import Dashboard
from dashboard import Dashboard
from pondDashboard import PondDashboard
from random import randint
from FishData import FishData

import random
import pygame
import pygame_menu
import sys
from PyQt6.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt6.QtCore import Qt, QSize
from PyQt6 import QtWidgets, uic, QtGui
import threading
from Client import Client
from FishStore import FishStore
from vivisystem.client import VivisystemClient
from vivisystem.models import VivisystemPond, VivisystemFish, EventType


#sadsa
class Pond:

    def __init__(self, fishStore: FishStore, vivi_client: VivisystemClient, name="Aqua-Gang"):
        self.name = name
        self.fishes = []
        self.moving_sprites = pygame.sprite.Group()
        self.plankton = pygame.image.load("/Users/jirapad/Documents/GitHub/AquaGang/AquaGang/assets/images/sprites/plankton.png")
        self.birdImage = pygame.image.load("/Users/jirapad/Documents/GitHub/AquaGang/AquaGang/assets/images/sprites/crab.png")
        self.plankton = pygame.transform.scale(self.plankton, (128,128))
        self.birdImage = pygame.transform.scale(self.birdImage, (128, 128))
        self.msg = ""
        self.pondData = PondData(self.name)
        self.network = None
        self.sharkTime = 0
        self.displayShark = False
        self.fishStore: FishStore = fishStore
        self.vivi_client = vivi_client
        

    def getPondData(self):
        return self.pondData

    def getPopulation(self):
        return len(self.fishes)
    
    def randomBird(self):
        dead = randint(0, len(self.fishes)-1)
        return self.fishes[dead]

    def randomShark(self):
        dead = randint(0, len(self.fishes)-1)
        return self.fishes[dead]

    # def sharkAttack(self, screen, fish):
    #     screen.blit(self.plankton, (fish.getFishx(), fish.getFishy())) 
    #     self.removeFish(fish)
    #     fish.die()
           

    def spawnFish(self, parentFish = None):
        tempFish = Fish(100, 100, self.name, parentFish.getId())
        self.fishes.append(tempFish)
        self.moving_sprites.add(tempFish)
        
    def pheromoneCloud(self ):
        pheromone = randint(2, 20)
        for f in self.fishes:
            f.increasePheromone(pheromone)
        
            if f.isPregnant(): ## check that pheromone >= pheromone threshold
                newFish = Fish(50, randint(50, 650), f.getGenesis(), f.getId())
                print("CHILD FISH")
                self.addFish( newFish)
                # self.pondData.addFish( newFish.fishData)
                
                f.resetPheromone()

    def migrateFish(self, fishIndex, destination):
        # destination = random.choice(self.network.other_ponds.keys())
        print("---------------------------FISH SHOULD BE REMOVED BY MIGRATE-------------------------")

        temp = self.fishes[fishIndex]
        # self.fishes.pop(fishIndex)
        # self.moving_sprites.remove(temp)
        # self.pondData.migrateFish(temp.getId())
        # self.network.pond = self.pondData
        self.removeFish(temp)
        self.network.migrate_fish(temp.fishData, destination )

    #---------------implement---------------#``

    def addFish(self, newFishData): #from another pond
        self.fishes.append(newFishData)
        self.pondData.addFish(newFishData.fishData)
        self.moving_sprites.add(newFishData)
        self.network.pond = self.pondData

    
    def removeFish(self, fish):
        self.fishes.remove(fish)
        print("---------------------------FISH SHOULD BE REMOVED-------------------------")
        for f in self.pondData.fishes:
            if f.id == fish.getId():
                print("---------------------------REMOVE FISH FROM POND DATA-------------------------")
                self.pondData.fishes.remove(f)
                break
        self.network.pond = self.pondData
        self.moving_sprites.remove(fish)

    def update(self, injectPheromone = False):
        for ind, f in enumerate( self.fishes): #checkout all the fish in the pond
            f.updateLifeTime() # decrease life time by 1 sec
            if f.fishData.status == "dead":
                self.removeFish(f)
                continue
            self.pondData.setFish(f.fishData)
            
            if len(self.network.other_ponds.keys()) > 0:
                # print( f.getId(), f.in_pond_sec)
                if f.getGenesis() != self.name and f.in_pond_sec >= 5 and not f.gaveBirth:
                    newFish = Fish(50,randint(50, 650),f.fishData.genesis, f.fishData.id)
                    newFish.giveBirth() ## not allow baby fish to breed
                    print("ADD FISH MIGRATED IN POND FOR 5 SECS")
                    self.addFish( newFish )
                    f.giveBirth()
            
                    # self.pondData.addFish( newFish.fishData )
                if f.getGenesis() == self.name and f.in_pond_sec <= 15:
                    if random.getrandbits(1):
                        # print('OTHER POND >>> ',self.network.other_ponds.keys())
                        dest = random.choice(list(self.network.other_ponds.keys()))
                        self.migrateFish( ind, dest )
                        # self.network.migrate_fish(f, dest)
                        # self.pondData.migrateFish(f.getId())
                        parent = None
                        if f.fishData.parentId:
                            parent = f.fishData.parentId
                        for ind2, f2 in enumerate(self.fishes):
                            if parent and f2.fishData.parentId == parent or f2.fishData.parentId == f.getId():
                                self.migrateFish( ind2, dest)
                                # self.network.migrate_fish( f2, dest)
                                # self.pondData.migrateFish(f2.getId())
                                break
                        continue
                elif f.getGenesis() == self.name and f.in_pond_sec >= 15:
                    dest = random.choice(list(self.network.other_ponds.keys()))
                    self.migrateFish( ind, dest )
                    # self.network.migrate_fish(f, dest)
                    # self.pondData.migrateFish(f.getId())
                    parent = None
                    if f.fishData.parentId:
                        parent = f.fishData.parentId
                    for ind2, f2 in enumerate(self.fishes):
                        if parent and f2.fishData.parentId == parent or f2.fishData.parentId == f.getId():
                            self.migrateFish( ind2, dest)
                            # self.network.migrate_fish( f2, dest)
                            # self.pondData.migrateFish(f2.getId())
                            break
                    continue
                else :
                    dest = random.choice(list(self.network.other_ponds.keys()))
                    if self.getPopulation() > f.getCrowdThresh():
                        
                        self.migrateFish( ind, dest )
                        # self.network.migrate_fish(f, dest )
                        # self.pondData.migrateFish( f.fishData.id )
                    continue
            
        if ( injectPheromone ):
            self.pheromoneCloud()
        # print("Client send :",self.pondData)
        self.network.pond = self.pondData

    def run(self):
        # General setup
        direction = 1
        speed_x = 3
        # speed_y = 4
        random.seed(123)
        
        self.network = Client(self.pondData)
        # self.msg = self.network.get_msg()
        msg_handler = threading.Thread(target=self.network.get_msg)
        msg_handler.start()
        send_handler = threading.Thread(target=self.network.send_pond)
        send_handler.start()
        lifetime_handler = threading.Thread(target=self.network.handle_lifetime)
        lifetime_handler.start()

        pygame.init()
        screen = pygame.display.set_mode((1280, 720))

        bg = pygame.image.load("/Users/jirapad/Documents/GitHub/AquaGang/AquaGang/assets/images/background/bg3.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        pygame.display.set_caption("AquaGang Project")
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        pregnant_time = pygame.time.get_ticks()
        update_time = pygame.time.get_ticks()
        self.addFish(Fish(10,100))

        # self.addFish(Fish(10,140, genesis="peem"))
        # self.addFish(Fish(100,200, genesis="dang"))

        app = QApplication(sys.argv)
        other_pond_list = []

        running = True
        while running:

            if len(self.fishes) > 15:
                while(len(self.fishes)>16):
                    kill = randint(0, len(self.fishes) - 1)
                    self.removeFish(self.fishes[kill])
                # self.fishes[kill].die()

            # print(self.network.get_msg())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.network.disconnect()
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        # print(self.fishes[0].getId())
                        allPondsNum = len(self.fishes)
                        for p in self.network.other_ponds.values():
                            allPondsNum += p.getPopulation()
                        d = Dashboard(self.fishes, allPondsNum)
                        pond_handler = threading.Thread(target=app.exec)
                        pond_handler.start()
                    elif event.key == pygame.K_LEFT:
                        for pondName in list(self.network.other_ponds.keys()):
                            other_pond_list.append(self.network.other_ponds.get(pondName))
                        pd = PondDashboard(other_pond_list)
                        pond_handler = threading.Thread(target=app.exec)
                        pond_handler.start()
                        
            other_pond_list = []

            # print("POND:"+self.msg.__str__())
            # print("pond: ", self.pondData)
            # self.msg = self.network.send_pond()
           # print(self.msg.data)
            if len(self.network.messageQ) > 0:
                self.msg = self.network.messageQ.pop()
                if (self.msg.action == "MIGRATE"):
                    newFish = Fish(50, randint(50, 650), self.msg.data['fish'].genesis, self.msg.data['fish'].parentId)
                    print("ADD MIGRATED FISH")
                    self.addFish(newFish)

                    # self.pondData.addFish(newFish.fishData)
                    # self.network.pond = self.pondData
                    
            screen.fill((0, 0, 0))
            screen.blit(bg,[0,0])

            
            for fish in self.moving_sprites:
                fish.move(speed_x)
                screen.blit(fish.image, fish.rect)
      
            
            time_since_enter = pygame.time.get_ticks() - start_time
            time_since_new_birth = pygame.time.get_ticks() - pregnant_time
            time_since_update = pygame.time.get_ticks() - update_time
            if (time_since_update > 1000):
                self.update()
                # print(self.fishes)
                update_time = pygame.time.get_ticks()

            if (time_since_new_birth > 5000):
                self.pheromoneCloud()
                pregnant_time = pygame.time.get_ticks()

            #shark every 15 seconds
            if time_since_enter > 7000:
                if len(self.fishes) > 4 and len(self.fishes)% 2 == 0:
                    deadFishbyPlankton = self.randomShark()
                    screen.blit(self.plankton, (deadFishbyPlankton.getFishx()+30, deadFishbyPlankton.getFishy()))
                    pygame.display.flip()
                    pygame.event.pump()
                    pygame.time.delay(1000)
                    self.removeFish(deadFishbyPlankton)
                    deadFishbyPlankton.die()
                    start_time = pygame.time.get_ticks()
                elif len(self.fishes) > 4 and len(self.fishes)% 2 != 0:
                    deadFishbyBird = self.randomBird()
                    screen.blit(self.birdImage, (deadFishbyBird.getFishx()+30, deadFishbyBird.getFishy()))
                    pygame.display.flip()
                    pygame.event.pump()
                    pygame.time.delay(1000)
                    self.removeFish(deadFishbyBird)
                    deadFishbyBird.die()
                    start_time = pygame.time.get_ticks()
            # print(len(self.fishes))

            # if time_since_last_data_send > 2000:
            #     pass
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        