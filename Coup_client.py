import pygame
import random

from pygamegame import PygameGame
from player import *
from card import *

# CITATION: Sockets starter code from Kyle
# https://kdchin.gitbooks.io/sockets-module-manual/
# Modified for use with Pygame

import socket
import threading
from queue import Queue

HOST = "192.168.1.12" # put host IP address here if playing on multiple computers
PORT = 50005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

# Game code starts here

class Game(PygameGame):

    def init(self):
        self.fontSmall = pygame.font.Font('resources/font.ttf', 18)
        self.fontMedium = pygame.font.Font('resources/font.ttf', 28)
        self.fontBig = pygame.font.Font('resources/font.ttf', 48)
        self.fontGiant = pygame.font.Font('resources/font.ttf', 64)
        self.me = None
        self.cardNames = [ ]
        tempSet = [ [ 'Ambassador', 'Assassin', 'Captain', 'Contessa', 'Duke' ] for i in range(3) ]
        self.deck = tempSet[0] + tempSet[1] + tempSet[2]
        self.waiting = True
        self.players = [ ]
        self.playerNames = [ ]
        self.shuffling = 0
        self.player1Text = self.fontSmall.render('Player 1', True, (255,255,255))
        self.player2Text = self.fontSmall.render('Player 2', True, (255,255,255))
        self.player3Text = self.fontSmall.render('Player 3', True, (255,255,255))
        self.player4Text = self.fontSmall.render('Player 4', True, (255,255,255))
        self.player1_rect = self.player1Text.get_rect(center=(2000,2000))
        self.player2_rect = self.player2Text.get_rect(center=(2000,2000))
        self.player3_rect = self.player3Text.get_rect(center=(2000,2000))
        self.player4_rect = self.player4Text.get_rect(center=(2000,2000))
        self.coins1 = self.fontSmall.render('Coins', True, (255,255,255))
        self.coins2 = self.fontSmall.render('Coins', True, (255,255,255))
        self.coins3 = self.fontSmall.render('Coins', True, (255,255,255))
        self.coins4 = self.fontSmall.render('Coins', True, (255,255,255))
        self.myCoins = self.fontMedium.render('Coins', True, (255,255,255))
        self.coins1_rect = self.coins1.get_rect(center=(2000,2000))
        self.coins2_rect = self.coins2.get_rect(center=(2000,2000))
        self.coins3_rect = self.coins3.get_rect(center=(2000,2000))
        self.coins4_rect = self.coins4.get_rect(center=(2000,2000))
        self.myCoins_rect = self.myCoins.get_rect(center=(2000,2000))
        
        ###
        
        self.isLegal = None
        self.command = None
        self.initator = None
        self.challenger = None
        self.target = None
        ###
        self.turnCounter = 0
        self.numAllows = 0
        #self.players[0].status = "myTurn"
        
    ###
    def getTurn(self):
        self.turnCounter = self.turnCounter%4
        for i in range(len(self.players)):
            if i == self.turnCounter:
                self.players[i].status = "myTurn"
            else:
                self.players[i].status = "notMyTurn"
    

    def mousePressed(self, x, y):
        pass

    def mouseReleased(self, x, y):
        pass

    def mouseMotion(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass

    def keyPressed(self, keyCode, modifier):
        if self.me.status == "myTurn":
            if keyCode == pygame.K_a:
                self.me.status = "assassinating"
            elif keyCode == pygame.K_c:
                self.me.status = "launchingCoup"
            elif keyCode == pygame.K_s:
                self.me.status = "stealing"
            elif keyCode == pygame.K_m:
                msg = self.me.take1Coin()
                self.server.send(msg.encode())
            #elif keyCode == pygame.K_d:
            #    msg = "tryTake2Coins\n"
            #    self.server.send(msg.encode())
            elif keyCode == pygame.K_t:
                msg = self.me.take3Coins()
                self.server.send(msg.encode())
            

        elif self.me.status == "assassinating":
            if keyCode == pygame.K_1:
                msg = self.me.assassinate("1")
            elif keyCode == pygame.K_2:
                msg = self.me.assassinate("2")
            elif keyCode == pygame.K_3:
                msg = self.me.assassinate("3")
            elif keyCode == pygame.K_4:
                msg = self.me.assassinate("4")
            
            tempMsg = msg.split(" ")
            self.isLegal = tempMsg[-1]
            self.command = tempMsg[0]
            self.initiator = self.me.name
            self.target = tempMsg[1]
            self.server.send(msg.encode())
            print(self.me.status)
            
        elif self.me.status == "launchingCoup":
            if keyCode ==  pygame.K_1:
                msg = self.me.launchCoup("1")
            elif keyCode ==  pygame.K_2:
                msg = self.me.launchCoup("2")
            elif keyCode ==  pygame.K_3:
                msg = self.me.launchCoup("3")
            elif keyCode ==  pygame.K_4:
                msg = self.me.launchCoup("4")
            self.server.send(msg.encode())
        
        elif self.me.status == "stealing":
            if keyCode == pygame.K_1:
                msg = self.me.steal("1")
            elif keyCode == pygame.K_2:
                msg = self.me.steal("2")
            elif keyCode == pygame.K_3:
                msg = self.me.steal("3")
            elif keyCode == pygame.K_4:
                msg = self.me.steal("4")
                
            
            tempMsg = msg.split(" ")
            self.isLegal = tempMsg[-1]
            self.command = tempMsg[0]
            self.initiator = self.me.name
            self.target = tempMsg[1]
            self.server.send(msg.encode())
            
        elif self.me.status == "responding":
            if keyCode == pygame.K_y:
                result = self.me.challenge(self.isLegal)
                msg = result[0]
                self.challenger = self.me.name
                print(result[0], result[1])
                if (result[1]=="fail"):
                    print(self.command)
                    if (self.command == "tryAssassinate"):
                        #print(command, "7.1")
                        for player in self.players:
                            print(self.players)
                            print(player, player.name, self.target, self.challenger, self.initiator)
                            print(player.name==self.target)
                            if (player.name == self.target):
                                print("alibaba1")
                                player.cards.pop()
                            if (player.name == self.challenger):
                                print("alibaba2")
                                player.cards.pop()
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    elif (self.command == "trySteal"):
                        #print(command, "7.2")
                        for player in self.players:
                            # print(self.players)
                            # print(player, player.name, self.target, self.challenger, self.initiator)
                            # print(player.name==self.target)
                            if (player.name == self.target):
                                # print("alibaba1")
                                player.coins -= 2
                            if (player.name == self.initiator):
                                # print("alibaba2")
                                player.coins += 2
                            if (player.name == self.challenger):
                                # print("alibaba3")
                                player.cards.pop()
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    elif (self.command == "tryTake3Coins"):
                        #print(command, "7.3")
                        for player in self.players:
                            if (player.name == self.initiator):
                                player.coins += 3
                            if (player.name == self.challenger):
                                player.cards.pop()
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                elif (result[1]=="success"):
                    if self.command == "tryAssassinate":
                        #print(command, "8.1")
                        for player in self.players:
                            #print(self.players)
                            #print(player, player.name, self.target, self.challenger, self.initiator)
                            #print(player.name==self.target)
                            if (player.name == self.initiator):
                                #print("alibaba3")
                                player.cards.pop()
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    elif (self.command == "trySteal"):
                        #print(command, "8.2")
                        for player in self.players:
                            #print(self.players)
                            #print(player, player.name, self.target, self.challenger, self.initiator)
                            #print(player.name==self.target)
                            if (player.name == self.initiator):
                                #print("alibaba3")
                                player.cards.pop()
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    elif (self.command == "tryTake3Coins"):
                        #print(command, "8.3")
                        for player in self.players:
                            if (player.name == self.initiator):
                                player.cards.pop()
                            msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                ###
                self.turnCounter += 1
                self.getTurn()
                self.server.send(msg.encode())
            ### Allow code
            elif keyCode == pygame.K_n:
                print("slap")
                msg = self.me.allow()
                print("slap2")
                self.server.send(msg.encode())
                print("slap3")
                self.numAllows += 1
                
                if self.numAllows == 3:
                    #print(command, "7.0")
                    #print(self.command)
                    if (self.command == "tryAssassinate"):
                        #print(command, "7.1")
                        for player in self.players:
                            #print(self.players)
                            #print(player, player.name, self.target, self.challenger, self.initiator)
                            #print(player.name==self.target)
                            if (player.name == self.target):
                                print("alibaba1")
                                player.cards.pop()
                            
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    elif (self.command == "trySteal"):
                        #print(command, "7.2")
                        for player in self.players:
                            # print(self.players)
                            # print(player, player.name, self.target, self.challenger, self.initiator)
                            # print(player.name==self.target)
                            if player.name == self.target:
                                # print("alibaba1")
                                player.coins -= 2
                            if player.name == self.initiator:
                                # print("alibaba2")
                                player.coins += 2
                            
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    elif (self.command == "tryTake3Coins"):
                        #print(command, "7.3")
                        for player in self.players:
                            if (player.name == self.initiator):
                                player.coins += 3
                            
                            #msg = " ".join(player.cards)
                            #self.server.send(msg.encode())
                            print(player, player.cards)
                    
                    self.numAllows = 0
                    self.turnCounter += 1
                    self.getTurn()

    def keyReleased(self, keyCode, modifier):
        pass

    def timerFired(self, dt):
        if self.waiting and len(self.players) >= 4:
            msg = "FULL SERVER\n"
            self.server.send(msg.encode())

        while (self.serverMsg.qsize() > 0):
            msg = self.serverMsg.get(False)
            try:
                print("fanny")
                msg = msg.split()
                command = msg[0]
                print(command, command == "challenge")
                print(msg[-1], len(msg[-1]), "100000000000000000000000")

                print(command, 0)
                if (command == "shuffle"):
                    index = int(msg[2])
                    if self.players[index].name == self.me.name:
                        if index == 0:
                            self.shuffling += 1
                            if self.shuffling == 2:
                                return
                            elif self.shuffling == 3:
                                self.shuffling = 0
                                return
                        card = random.choice(self.deck)
                        self.deck.remove(card)
                        self.cardNames.append(card)
                        self.me.cards.append(Card(card))
                        msg = 'taken ' + str(index) + ' ' + card + '\n'
                        self.server.send(msg.encode())
                        if index == 3 and len(self.me.cards) <= 1:
                            index = 0
                        else:
                            index += 1
                        msg = 'shuffle ' + str(index) + '\n'
                        self.server.send(msg.encode())
                
                elif (command == 'taken'):
                    print(command, 1)
                    playerIndex = int(msg[2])
                    card = msg[3]
                    self.deck.remove(card)
                    self.players[playerIndex].cards.append(Card(card, True))
                
                elif (command == "FULL") and self.waiting:
                    print(command, 2)
                    pygame.time.delay(1000)
                    self.players.sort()
                    self.playerNames = sorted(self.players)
                    for i in range(len(self.players)):
                        self.players[i] = Player(self.players[i])
                        if self.players[i].name == self.me:
                            self.me = self.players[i]
                    msg = 'shuffle ' + '0' + '\n'
                    self.server.send(msg.encode())
                    self.waiting = False
                    self.getTurn() #RAYMOND'S GENIUS FUCKING IDEA
                
                elif (command == "myIDis"):
                    print(command, 3)
                    myPID = msg[1]
                    self.players.append(myPID)
                    self.me = myPID
                    
                
                elif (command == "newPlayer"):
                    print(command, 4)
                    newPID = msg[1]
                    self.players.append(newPID)
                
                
                    
                elif (command in ["tryAssassinate", "trySteal"]):
                    print(command, 5)
                    self.isLegal = msg[-1]
                    print(self.isLegal, len(self.isLegal), "ass whack my fanny hole")
                    self.command = command
                    self.initiator = msg[1]
                    self.target = msg[2]
                    if (command == "tryAssassinate"):
                        for player in self.players:
                            if (player.name == self.initiator):
                                player.coins -= 3
                    self.me.status = "responding"
                    print(self.isLegal, self.command, self.initiator, self.target, self.me.status)
                    # for player in self.players:
                    #     if player.name == self.initiator:
                    #         player.coins -= 3
                
                elif (command == "tryTake3Coins"):
                    print(command, 6)
                    self.isLegal = msg[-1]
                    self.command = command
                    self.initator = msg[1]
                    self.me.status = "responding"
                    
                
                elif msg[0] == "challenge":
                    print(command, 7)
                    self.challenger = msg[1]
                    print(msg[2])
                    if msg[2] == "fail":
                        print(command, "7.0")
                        print(self.command)
                        if (self.command == "tryAssassinate"):
                            print(command, "7.1")
                            for player in self.players:
                                print(self.players)
                                print(player, player.name, self.target, self.challenger, self.initiator)
                                print(player.name==self.target)
                                if (player.name == self.target):
                                    print("alibaba1")
                                    player.cards.pop()
                                if (player.name == self.challenger):
                                    print("alibaba2")
                                    player.cards.pop()
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                        elif (self.command == "trySteal"):
                            print(command, "7.2")
                            for player in self.players:
                                # print(self.players)
                                # print(player, player.name, self.target, self.challenger, self.initiator)
                                # print(player.name==self.target)
                                if player.name == self.target:
                                    # print("alibaba1")
                                    player.coins -= 2
                                if player.name == self.initiator:
                                    # print("alibaba2")
                                    player.coins += 2
                                if player.name == self.challenger:
                                    # print("alibaba3")
                                    player.cards.pop()
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                        elif (self.command == "tryTake3Coins"):
                            print(command, "7.3")
                            for player in self.players:
                                if (player.name == self.initiator):
                                    player.coins += 3
                                if (player.name == self.challenger):
                                    player.cards.pop()
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                    
                    elif msg[2] == "success":
                        print(command, 8)
                        print(self.command)
                        if self.command == "tryAssassinate":
                            print(command, "8.1")
                            for player in self.players:
                                #print(self.players)
                                #print(player, player.name, self.target, self.challenger, self.initiator)
                                #print(player.name==self.target)
                                if (player.name == self.initiator):
                                    #print("alibaba3")
                                    player.cards.pop()
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                        elif self.command == "trySteal":
                            print(command, "8.2")
                            for player in self.players:
                                #print(self.players)
                                #print(player, player.name, self.target, self.challenger, self.initiator)
                                #print(player.name==self.target)
                                if player.name == self.initiator:
                                    #print("alibaba3")
                                    player.cards.pop()
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                        elif self.command == "tryTake3Coins":
                            print(command, "8.3")
                            for player in self.players:
                                if player.name == self.initiator:
                                    player.cards.pop()
                                msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                    
                    ###
                    #for turn counter
                    self.turnCounter += 1
                    self.numAllows = 0 #to reinitialize it before next turn
                    self.getTurn()
                
                ###
                elif (msg[0] == "allow"):
                    print("ass")
                    self.numAllows += 1
                    if self.numAllows == 3:#should 3-self.dead (for full game)
                        #print(command, "7.0")
                        #print(self.command)
                        if (self.command == "tryAssassinate"):
                            #print(command, "7.1")
                            for player in self.players:
                                #print(self.players)
                                #print(player, player.name, self.target, self.challenger, self.initiator)
                                #print(player.name==self.target)
                                if (player.name == self.target):
                                    print("alibaba1")
                                    player.cards.pop()
                                
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                        elif (self.command == "trySteal"):
                            print(command, "7.2")
                            for player in self.players:
                                # print(self.players)
                                # print(player, player.name, self.target, self.challenger, self.initiator)
                                # print(player.name==self.target)
                                if player.name == self.target:
                                    # print("alibaba1")
                                    player.coins -= 2
                                if player.name == self.initiator:
                                    # print("alibaba2")
                                    player.coins += 2
                                
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                        elif (self.command == "tryTake3Coins"):
                            print(command, "7.3")
                            for player in self.players:
                                if (player.name == self.initiator):
                                    player.coins += 3
                                
                                #msg = " ".join(player.cards)
                                #self.server.send(msg.encode())
                                print(player, player.cards)
                            
                        
                        self.turnCounter += 1
                        self.numAllows = 0
                        self.getTurn()
                        
                
            except:
                # print("failed")
                self.serverMsg.task_done()

    def redrawAll(self, screen):
        if self.waiting:
            waiting = self.fontBig.render('waiting for players...', True, (255,255,255))
            waiting_rect = waiting.get_rect(center=(self.width // 2, self.height // 2))
            screen.blit(waiting, waiting_rect)
        else:
            otherPlayer = 0
            for i in range(len(self.players)):
                if self.players[i].name != self.me.name:
                    self.playerNum1Text = self.fontSmall.render(str(i+1), True, (255,255,255))
                    otherPlayer += 1
                    shift = -75
                    if otherPlayer == 1:
                        cx, cy = 0, self.height // 2
                        angle = 90
                        for card in self.players[i].cards:
                            card.draw(screen, cx, cy + shift, 0.2, angle)
                            shift *= -1
                        if i == 0:
                            self.player1_rect = self.player1Text.get_rect(center=(75, 190))
                            self.coins1_rect = self.coins1.get_rect(center=(75, 530))
                        elif i == 1:
                            self.player2_rect = self.player2Text.get_rect(center=(75, 190))
                            self.coins2_rect = self.coins2.get_rect(center=(75, 530))
                    elif otherPlayer == 2:
                        cx, cy = self.width // 2, 0
                        angle = 0
                        for card in self.players[i].cards:
                            card.draw(screen, cx + shift, cy, 0.2, angle)
                            shift *= -1
                        if i == 1:
                            self.player2_rect = self.player2Text.get_rect(center=(410, 52))
                            self.coins2_rect = self.coins2.get_rect(center=(870, 52))
                        elif i == 2:
                            self.player3_rect = self.player3Text.get_rect(center=(410, 52))
                            self.coins3_rect = self.coins3.get_rect(center=(870, 52))
                    elif otherPlayer == 3:
                        cx, cy = self.width, self.height // 2
                        angle = 90
                        for card in self.players[i].cards:
                            card.draw(screen, cx, cy + shift, 0.2, angle)
                            shift *= -1
                        if i == 2:
                            self.player3_rect = self.player3Text.get_rect(center=(1205, 190))
                            self.coins3_rect = self.coins3.get_rect(center=(1205, 530))
                        elif i == 3:
                            self.player4_rect = self.player4Text.get_rect(center=(1205, 190))
                            self.coins4_rect = self.coins4.get_rect(center=(1205, 530))
                else:
                    cx, cy = self.width // 2, self.height
                    shift = -125
                    angle = 0
                    for card in self.me.cards:
                            card.draw(screen, cx + shift, cy, 0.4, angle)
                            shift *= -1
            screen.blit(self.player1Text, self.player1_rect)
            screen.blit(self.player2Text, self.player2_rect)
            screen.blit(self.player3Text, self.player3_rect)
            screen.blit(self.player4Text, self.player4_rect)
            self.coins1 = self.fontSmall.render('Coins: ' + str(self.players[0].coins), True, (255,255,255))
            self.coins2 = self.fontSmall.render('Coins: ' + str(self.players[1].coins), True, (255,255,255))
            self.coins3 = self.fontSmall.render('Coins: ' + str(self.players[2].coins), True, (255,255,255))
            self.coins4 = self.fontSmall.render('Coins: ' + str(self.players[3].coins), True, (255,255,255))
            self.myCoins = self.fontMedium.render('Coins: ' + str(self.me.coins), True, (255,255,255))
            self.myCoins_rect = self.myCoins.get_rect(center=(1000,625))
            screen.blit(self.coins1, self.coins1_rect)
            screen.blit(self.coins2, self.coins2_rect)
            screen.blit(self.coins3, self.coins3_rect)
            screen.blit(self.coins4, self.coins4_rect)
            screen.blit(self.myCoins, self.myCoins_rect)
            coup = self.fontGiant.render('COUP', True, (255,255,255))
            coup_rect = coup.get_rect(center=(self.width//2, self.height//2))
            screen.blit(coup, coup_rect)


def main():
    serverMsg = Queue(100)
    threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
    game = Game(serverMsg, server)
    game.run()

if __name__ == '__main__':
    main()