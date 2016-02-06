import os
import sys
import gamemods
import cards


class gameboard(object):
    def __init__(self, num):
        self.num_players = num
        self.playerone = gamemods.Player('One')
        self.playerone.gameboard = self
        self.playertwo = gamemods.Player('Two')
        self.playertwo.gameboard = self
        self.playerthree = gamemods.Player('Three')
        self.playerthree.gameboard = self
        self.playerfour = gamemods.Player('Four')
        self.playerfour.gameboard = self
        self.playerfive = gamemods.Player('Five')
        self.playerfive.gamebaord = self
        self.ship = gamemods.Ship()
        self.deck = gamemods.Deck()
        self.threat_deck = gamemods.Deck()
        self.phase = 1
        self.player_order = [self.playerone, self.playertwo, self.playerthree, self.playerfour, self.playerfive]
        self.playerlist = self.player_order[:self.num_players]

    def deal_new_phase(self):
        self.deck.deal([x.hand for x in self.playerlist], 6)

    def computer_check(self, current_turn):
        report = ["Turn %d: Checking Main Computer Terminal" % current_turn]
        if self.ship.main_computer:
            report.append("Main Computer On.")
            self.ship.main_computer = 0
        else:
            report.append("Main Computer Off.  All players delayed.")
            for player in self.playerlist:
                player.delayed(current_turn)
        return report

    def playgame(self):
        os.system('cls')
        cards.Randomly_Populate(self.deck, 100)
        self.deck.deal([x.hand for x in self.playerlist], 5)
        cards.Generate_ThreatTracks(self.ship)
        cards.Generate_ThreatDeck(self.threat_deck)
        for player in self.playerlist:
            player.playturn()
        turn = 0
        while turn < 12:
            report = []
            turn += 1
            if turn in [3, 6, 10]:
                report.extend(self.computer_check(turn))

newgame = gameboard(1)
newgame.playgame()