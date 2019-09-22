import pygame
import random

class Player(object):
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.coins = 0
        currentAction = None
        self.uninterrupted = True
        
        
        self.status = "notMyTurn"
    
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        try:
            return self.name==other.name
        except:
            return False
    #List of character-specific actions that the players can take:
    def assassinate(self, otherPlayer):
        #spend 3 coins
        #target otherPlayer
        #assassin's action
        currentAction = "tryAssassinate"
        self.coins -= 3
        isLegal = "False"
        for card in self.cards:
            if card.type == "Assassin":
                isLegal = "True"
        msg = "tryAssassinate " + otherPlayer + " " + str(isLegal)+"\n"
        return msg
        
        
        """
        pygame.time.delay(5000)
        if uninterrupted == True:
            currentAction = None
            msg = "assassinate "+self.name+" "+otherPlayer+"\n"
            return msg
        """
     
     
    # #swapDraw and swapPutBack are to be called in sequence    
    # def swapDraw(self, game):
    #     #draw two cards from deck
    #     #choose two cards to put back in deck
    #     #ambassador's action
    #     currentAction = "try-swapDraw"
    #     uninterrupted = True
    #     pygame.time.delay(5000)
    #     
    #     if uninterrupted == True:
    #         cardDrawn1 = random.choice(game.deck)
    #         self.cards.append(cardDrawn1) #deck is a list of strings
    #         game.deck.remove(cardDrawn1)
    #         cardDrawn2 = random.choice(game.deck)
    #         self.cards.append(cardDrawn2)
    #         game.deck.remove(cardDrawn2)
    #     
    #     msg = "swap "+self.name+" "+self.cards[2]+" "+self.cards[3]+"\n"
    #     return msg
    #     
    #     
    # def swapPutBack(self, game):
    #     currentAction = None
    #     firstPutBack = input("Choose nth card to put back (starting from 0)")
    #     game.deck.append(self.cards.pop(firstPutBack))
    #     secondPutBack = input("Choose nth card to put back")
    #     game.deck.append(self.cards.pop(secondPutBack))
    
        
    def steal(self, otherPlayer):
        #target otherPlayer
        #take two coins from otherPlayer
        #captain's action
        isLegal = False
        for card in self.cards:
            if card.type=="Captain":
                isLegal = True
        msg = "trySteal " + otherPlayer + " " + str(isLegal) + "\n"
        return msg
        
    def take3Coins(self):
        #duke's action
        isLegal = False
        for card in self.cards:
            if card.type == "Duke":
                isLegal = True
        msg = "tryTake3coins " + str(isLegal) + "\n"
        return msg
        
    #List of actions that everyone can take
        
    def take1Coin(self):
        currentAction = "take1coin"
        self.coins += 1
        msg = "tryTake1Coin" + "\n"
        return msg
        
    def take2Coins(self):
        pass
        
    def launchCoup(self, otherPlayer):
        #target otherPlayer
        #spend 10 coins
        #kill a character from otherPlayer
        #cannot be challenged or blocked
        self.coins -= 10
        msg = "launchCoup" + otherPlayer + "\n"
        return msg

    #reactions
    
    #in these cases, action is the message received
    def challenge(self, isLegal):
        if isLegal == "True":
            return ("challenge fail\n", "fail")
        elif isLegal == "False":
            return ("challenge success\n", "success")
    def allow(self):
        return ("allow 2 ass\n")
        
    def block(self, action):
        pass
    
            
        