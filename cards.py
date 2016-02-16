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


def Definitely_Populate(deck):
    move_red = Card()
    move_red.move = 'RED'
    move_red.state = 'm'
    move_blue = Card()
    move_blue.move = 'BLUE'
    move_blue.state = 'm'
    move_lift = Card()
    move_lift.move = 'LIFT'
    move_lift.state = 'm'
    action_a = Card()
    action_a.action = 'A'
    action_a.state = 'a'
    action_b = Card()
    action_b.action = 'B'
    action_b.state = 'a'
    action_c = Card()
    action_c.action = 'C'
    action_c.state = 'a'

    Player_Ones_Cards = [move_red, action_a, action_b, move_lift, action_b, action_c,
                         action_a, move_lift, action_a, action_a, action_a, action_a]
    Player_Twos_Cards = [action_c, action_b, move_lift, action_b, action_b, action_a,
                         action_b, action_c, move_lift, action_b, action_a, action_a]
    Player_Threes_Cards = [move_blue, action_b, move_lift, action_c, action_b, action_c,
                           action_a, move_lift, action_a, action_a, action_a, action_a]

    for card in Player_Ones_Cards+Player_Twos_Cards+Player_Threes_Cards:
        deck.add(card)


def Generate_ThreatTracks(ship):
    tracks = [['', '', '', '', '2X', '', '', '', '1Y', '', '', 'Z'],
              ['', '', '', '2', 'X', '', '', '1', 'Y', '', '', '', '', '', 'Z'],
              ['', '', '2', 'X', '', 'Y', '', '', '1', 'Y', '', '', '', 'Z']]
    for zone in ship.zone_layout:
        zone.threat_track = random.choice(tracks)


def Generate_ThreatDeck(deck):
    cardlist = [Asteroid, StealthShip, StealthShip]
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
        self.track_section = 0
        self.zone = ''

    def read_card(self):
        reply = "| "+self.name+": Speed = "+str(self.speed)+", HP = "+str(self.hitpoints) + \
                ", Shields = "+str(self.shields)+"\n"+self.card_text
        return reply

    def x_action(self):
        return [" -- -- No X Action"]

    def y_action(self):
        return [" -- -- No Y Action"]

    def z_action(self):
        return [" -- -- No Z Action"]

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
        self.speed = 2

    def x_action(self):
        report = [" -- -- X: Asteroid's speed increases 1"]
        self.speed += 1
        return report

    def z_action(self):
        report = [" -- -- Z: Asteroid does %d damage" % self.hitpoints]
        report.append(self.zone.do_damage(self.hitpoints))
        return report


class StealthShip(ThreatCard):
    def __init__(self):
        ThreatCard.__init__(self)
        self.name = "Stealth Ship"
        self.card_text = "|  - X: Reveals itself.\n|  - Z: Does 3 damage to all zones."
        self.hitpoints = 4
        self.shields = 2
        self.speed = 2
        self.targetable = 0

    def x_action(self):
        report = [" -- -- X: Stealth Ship reveals itself and can now be targeted"]
        self.targetable = 1
        return report

    def z_action(self):
        report = [" -- -- Z: Stealth Ship does 3 damage to all zones."]
        for eachzone in self.zone.ship.zone_layout:
            report.append(eachzone.do_damage(3))
        return report