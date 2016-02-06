import sys


class Hand(object):
    def __init__(self):
        self.cards = []

    def __str__(self):  # Return a string representing the hand
        reply = ""
        if self.cards:
            for i, card in enumerate(self.cards):
                reply += "(" + str(i + 1) + ") " + str(card) + "\n"
        else:
            reply = "<empty>"
        return reply

    def add(self, card):
        self.cards.append(card)

    def give(self, card, other_hand):
        self.cards.remove(card)
        other_hand.add(card)


class Deck(Hand):
    def shuffle(self):
        import random

        random.shuffle(self.cards)
        return "Shuffled the deck"

    def deal(self, hands, per_hand=5):
        for rounds in range(per_hand):
            for hand in hands:
                if self.cards:
                    top_card = self.cards[0]
                    self.give(top_card, hand)
                else:
                    return "Out of cards!"


class Section(object):
    def __init__(self, gun_strength, gun_range, maxenergy):
        self.gunpower = gun_strength
        self.gunrange = gun_range
        self.max_energy = maxenergy
        self.current_energy = (maxenergy+(-maxenergy % 2))//2
        self.c_action = ''
        self.gun_spread = 1
        self.fuel_capsules = 0
        self.zone = ''


class Zone(object):
    def __init__(self, color):
        self.max_hp = 6
        self.damage = 0
        self.lift_is_working = 1
        self.lift_in_use = 0
        self.ship = ''
        self.color = color
        self.threat_track = []
        self.threats = Hand()

        if color == 'white':
            self.upper = Section(5, 3, 3)
            self.upper.zone = self
            self.upper.c_action = 'main computer'

            self.lower = Section(1, 2, 5)
            self.lower.zone = self
            self.lower.c_action = 'spaceport'
            self.lower.fuel_capsules = 3
            self.lower.gun_spread = 3

        elif color == 'red':
            self.upper = Section(4, 3, 2)
            self.upper.zone = self
            self.upper.c_action = 'interceptors (range1, dmg1-3, spread1-3)'

            self.lower = Section(2, 2, 3)
            self.lower.zone = self
            self.lower.c_action = 'redbots'

        elif color == 'blue':
            self.upper = Section(4, 3, 2)
            self.upper.zone = self
            self.upper.c_action = 'bluebots'

            self.lower = Section(2, 2, 3)
            self.lower.zone = self
            self.lower.c_action = 'rockets (range2, dmg3)'

    def fullshow(self):
        returnlist = ["|--------- " + self.color.upper() + " Zone Status ---------"]
        returnlist.append("| THREAT TRACK: " + str(self.threat_track))
        returnlist.append("| Upper Level Gun: Power = "+str(self.upper.gunpower)+
                          ", Range = "+str(self.upper.gunrange)+", Spread = "+str(self.upper.gun_spread))
        returnlist.append("| Upper Level Shield: Max = "+str(self.upper.max_energy)+
                          ", Current = "+str(self.upper.current_energy))
        if self.color == 'red':
            returnlist.append("| Interceptors are " + ("present" if self.ship.interceptors else "gone"))
        elif self.color == 'white':
            returnlist.append("| Main Computer " + ("activated" if self.ship.main_computer else "NOT activated"))
        elif self.color == 'blue':
            returnlist.append("| Blue Bots are " + ("present" if self.ship.blue_bots else "gone"))
        returnlist.append("|----- Lift Status: Lift is "+("Working" if self.lift_is_working else "BROKEN"))+"------"
        returnlist.append("|----- Lift Status: Lift is "+("IN USE" if self.lift_in_use else "available")+"--------")
        returnlist.append("| Lower Level Gun: Power = "+str(self.lower.gunpower)+
                          ", Range = "+str(self.lower.gunrange)+", Spread = "+str(self.lower.gun_spread))
        returnlist.append("| Lower Level Reactor: Max = "+str(self.lower.max_energy)+
                          ", Current = "+str(self.lower.current_energy))
        if self.color == 'red':
            returnlist.append("| Red Bots are " + ("present" if self.ship.red_bots else "gone"))
        elif self.color == 'blue':
            returnlist.append("| Rockets Remaining: " + str(self.ship.rockets))
        returnlist.append("|---------------------------------------------")
        returnlist.append("| Damage Taken: " + str(self.damage))
        returnlist.append("")
        return returnlist

    def refshow(self):
        returnlist = ["|---------- " + self.color.upper() + " Zone  --------------"]
        returnlist.append("| THREAT TRACK: " + str(self.threat_track))
        returnlist.append("| Upper Level Gun: Power = "+str(self.upper.gunpower)+
                          ", Range = "+str(self.upper.gunrange)+", Spread = "+str(self.upper.gun_spread))
        returnlist.append("| Upper Level Shield: Max = "+str(self.upper.max_energy) +
                          ", Current = "+str(self.upper.current_energy))
        returnlist.append("| Upper Level C-Action: "+str(self.upper.c_action))
        returnlist.append("|---------------------------------------------")
        returnlist.append("| Lower Level Gun: Power = "+str(self.lower.gunpower)+", Range = " +
                          str(self.lower.gunrange)+", Spread = "+str(self.lower.gun_spread))
        returnlist.append("| Lower Level Reactor: Max = "+str(self.lower.max_energy) +
                          ", Current = "+str(self.lower.current_energy))
        returnlist.append("| Lower Level C-Action: "+str(self.lower.c_action))
        returnlist.append("|----------------------------------------------")
        return returnlist

    def Do_Damage(self, amount):
        shields = self.upper.current_energy
        if shields >= amount:
            self.upper.current_energy -= amount
            report = "Shields hold against %d damage.  Shields at %d energy." % (amount, self.upper.current_energy)
        else:
            result_damage = amount - self.upper.current_energy
            self.upper.current_energy = 0
            self.damage += result_damage
            if self.damage > self.max_hp:
                self.ship.explode()
            report = "Shields at %d.  %d damage taken to %s zone. %s zone HP = %d." % \
                     (self.upper.current_energy, result_damage, self.color, self.color, self.damage)
        return report


class Ship(object):
    def __init__(self):
        self.red_zone = Zone('red')
        self.red_zone.ship = self
        self.white_zone = Zone('white')
        self.white_zone.ship = self
        self.blue_zone = Zone('blue')
        self.blue_zone.ship = self
        self.red_bots = 1
        self.blue_bots = 1
        self.rockets = 3
        self.main_computer = 0
        self.interceptors = 1
        self.zone_layout = [self.red_zone, self.white_zone, self.blue_zone]

    def show_ship_reference(self):
        returnlist = []
        for zone in self.zone_layout:
            returnlist.extend(zone.refshow())
        return returnlist

    def show_ship_status(self):
        returnlist = []
        for zone in self.zone_layout:
            returnlist.extend(zone.fullshow())
        return returnlist

    def explode(self):
        print("Boom. Death.  Game Over.")
        sys.exit(0)


class Player(object):
    def __init__(self, pname=''):
        self.location = ''
        self.name = pname
        self.score = 0
        self.handlimit = 5
        self.gameboard = ''
        self.battlebots = 0
        self.hand = Hand()
        self.card_slots = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.slots_available = [1, 2, 3]
        self.actions = {"what": self.show_history, "draw": self.drawcard, "threat": self.threatcard,
                        # "transfer": self.transfercard,
                        "phase": self.phaseup, "play": self.playcard, "show": self.show_threats,
                        "pickup": self.pickup, "help": self.instr, "ship": self.show_ship}

    def tellplayer(self, what):
        print(what)

    def get_from_player(self, prompt=''):
        reponse = input(prompt).lower()
        return reponse

    def instr(self, opt=''):
        self.tellplayer("---------- Player Screen: ---------")
        self.tellplayer("|   Slots Open: This shows the numbered slots that are open for you to play on")
        self.tellplayer("|   Your Cards: This shows you a list of the playable cards in your hand")
        self.tellplayer("---------- Player Options: --------")
        self.tellplayer("|         SHIP: Shows the layout of the ship for reference")
        self.tellplayer("|         WHAT: Shows all the cards you've played (plus previous phases)")
        self.tellplayer("| TRANSFER X Y: Transfers card number X to player number Y")
        self.tellplayer("|     PLAY X Y: Plays card X in time slot Y")
        self.tellplayer("|     PICKUP X: Picks up card in time slot X")
        self.tellplayer("|        PHASE: Move to the next phase")
        self.tellplayer("|         DRAW: Draw new card to your hand")
        self.tellplayer("|       THREAT: Draw new threat card")
        self.tellplayer("|         SHOW: View threats")

    def show_history(self, opt=''):
        for i, turn in enumerate(self.card_slots):
            self.tellplayer(str(i+1)+": "+str(turn))

    def show_ship(self, opt=''):
        for thing in self.gameboard.ship.show_ship_reference():
            self.tellplayer(thing)

    def show_threats(self, opt=''):
        for zone in self.gameboard.ship.zone_layout:
            self.tellplayer("|----- "+zone.color.upper()+" ZONE THREATS -------")
            for card in zone.threats.cards:
                self.tellplayer(card.read_card())

    def phaseup(self, opt=''):
        self.gameboard.phase += 1
        self.gameboard.deal_new_phase()
        if self.gameboard.phase == 2:
            self.slots_available = [4, 5, 6, 7]
        elif self.gameboard.phase == 3:
            self.slots_available = [8, 9, 10, 11, 12]

    def drawcard(self, clickcost=1):
        self.gameboard.deck.deal([self.hand], 1)

    def threatcard(self, opt=''):
        # threat_level = self.get_from_player(" '1' for Normal, '2' for Serious > ")
        zone_placement = self.get_from_player(" 'R' for red zone, 'W' for white zone, 'B' for blue zone > ")
        if zone_placement == 'r':
            self.gameboard.threat_deck.deal([self.gameboard.ship.red_zone.threats], 1)
        elif zone_placement == 'w':
            self.gameboard.threat_deck.deal([self.gameboard.ship.white_zone.threats], 1)
        elif zone_placement == 'b':
            self.gameboard.threat_deck.deal([self.gameboard.ship.blue_zone.threats], 1)
        else:
            self.tellplayer("Bah, stop messing around. quit out")
            return False

    def playcard(self, firstopt='', secondopt=''):
        try:
            cardnum = int(firstopt) - 1
            slotnum = int(secondopt) - 1
        except:
            self.tellplayer("Use numbers to choose cards and slots")
            return False
        if cardnum in range(len(self.hand.cards)):
            chosencard = self.hand.cards[cardnum]
        else:
            self.tellplayer("Pick a card from your hand")
            return False
        if slotnum+1 in self.slots_available:
            if self.card_slots[slotnum] != 0:
                self.pickup(slotnum+1)
            self.card_slots[slotnum] = chosencard
            del self.hand.cards[cardnum]
        else:
            self.tellplayer("Pick an available slot to play in")
            return False
        newinput = self.get_from_player(" (M) for move side or (A) for action side: ")
        if newinput == 'm':
            self.card_slots[slotnum].state = 'm'
        elif newinput == 'a':
            self.card_slots[slotnum].state = 'a'
        else:
            self.tellplayer("Bah, stop messing around. quit out.")
            return False

    def pickup(self, opt=''):
        try:
            slotnum = int(opt) - 1
        except:
            self.tellplayer("Use numbers to choose slot")
            return False
        if slotnum+1 in self.slots_available:
            thecard = self.card_slots[slotnum]
            if thecard != 0:
                self.hand.add(thecard)
                self.card_slots[slotnum] = 0
                thecard.state = 0
            self.tellplayer("Picked up %s from slot %d" % (thecard, slotnum))
        else:
            self.tellplayer("You can't take anything from that slot")
            return False

    def delayed(self, timeslot):
        self.card_slots.insert(timeslot-1, 0)
        try:
            nextzero = self.card_slots[timeslot:].index(0)
            del self.card_slots[timeslot+nextzero]
        except:
            del self.card_slots[-1]

    def playturn(self):
        while self.gameboard.phase < 4:
            self.tellplayer("------ PHASE: "+str(self.gameboard.phase)+", PLAYER "+self.name.upper()+" -----")
            self.tellplayer("------ "+str(self.slots_available)+" ---------")
            self.tellplayer(self.hand)

            userinput = self.get_from_player(" Take Action > ")
            wordlist = userinput.split()
            if wordlist[0] in self.actions:
                do = self.actions[wordlist[0]]
                # try:
                do(*wordlist[1:])
            # except:
            #	self.tellplayer("Not understanding your nouns")
            else:
                self.tellplayer("action not in list: ")
                self.tellplayer(self.actions.keys())


