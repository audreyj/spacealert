import random

class Card(object):
    def __init__(self):
        self.move = ''
        self.action = ''
        self.state = 0
        self.id = '<None>'

    def __str__(self):
        if self.state == 'm':
            reply = "[" + self.move + "] / " + self.action
        elif self.state == 'a':
            reply = self.move + " / [" + self.action + "]"
        else:
            reply = self.move + " / " + self.action
        return reply


def Randomly_Populate(deck, numcards):
    movetypes = ['RED', 'BLUE', 'LIFT']
    actiontypes = ['A', 'B', 'C', 'bots']
    for i in range(numcards):
        card = Card()
        card.move = random.choice(movetypes)
        card.action = random.choice(actiontypes)
        card.id = i
        deck.add(card)
    deck.shuffle()


def Generate_ThreatTracks(ship):
    tracks = [['', '3', '', '', 'X', '2', '', '', 'Y', '1', '', 'Z'],
              ['', '', '', '3', 'X', '', '', '2', 'Y', '', '', '1', '', '', 'Z'],
              ['', '', '3', 'X', '', '2Y', '', '', '', 'Y', '1', '', '', 'Z']]
    for zone in ship.zone_layout:
        zone.threat_track = random.choice(tracks)


def Generate_ThreatDeck(deck):
    cardlist = [Asteroid, StealthShip]
    for card in cardlist:
        deck.add(card())
    deck.shuffle()


class ThreatCard(object):
    def __init__(self):
        self.name = '<None>'
        self.card_text = '<None>'
        self.distance = 0
        self.targetable = 1
        self.rocketable = 1
        self.speed = 1
        self.hitpoints = 1
        self.shields = 0
        self.zone = ''

    def read_card(self):
        reply = "| "+self.name+": Speed = "+str(self.speed)+\
                ", HP = "+str(self.hitpoints)+"\n"+self.card_text
        return reply

    def x_action(self):
        pass

    def y_action(self):
        pass

    def z_action(self):
        pass

    def remove(self):
        self.distance = 0
        self.zone = ''

class Asteroid(ThreatCard):
    def __init__(self):
        ThreatCard.__init__(self)
        self.name = "Asteroid"
        self.card_text = "|  - X: speed+1.\n|  - Z: Does damage equal to remaining HP."
        self.hitpoints = 9
        self.shields = 0
        self.speed = 3

    def x_action(self):
        report = ["X: Asteroid's speed increases 1"]
        self.speed += 1
        return report

    def z_action(self):
        report = ["Z: Asteroid does %d damage" % self.hitpoints]
        report.append(self.zone.Do_Damage(self.hitpoints))
        return report


class StealthShip(ThreatCard):
    def __init__(self):
        ThreatCard.__init__(self)
        self.name = "Stealth Ship"
        self.card_text = "|  - X: Reveals itself.\n|  - Z: Does 3 damage to all zones."
        self.hitpoints = 4
        self.shields = 2
        self.speed = 3
        self.targetable = 0

    def x_action(self):
        report = ["X: Stealth Ship reveals itself and can now be targeted"]
        self.targetable = 1
        return report

    def z_action(self):
        report = ["Z: Stealth Ship does 3 damage to all zones."]
        for eachzone in self.zone.ship.zone_layout:
            report.append(eachzone.Do_Damage(3))
        return report