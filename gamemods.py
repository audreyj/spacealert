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
    def __init__(self, gun_strength, gun_range, maxenergy, name):
        self.name = name
        self.gunpower = gun_strength
        self.gunrange = gun_range
        self.max_energy = maxenergy
        self.current_energy = (maxenergy+(-maxenergy % 2))//2
        self.c_action = ''
        self.gun_spread = 1
        self.zone = ''
        self.guns_fired = 0


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
            self.upper = Section(5, 3, 3, 'upper')
            self.upper.zone = self
            self.upper.c_action = 'main computer'
            self.lower = Section(1, 2, 5, 'lower')
            self.lower.zone = self
            self.lower.c_action = 'spaceport'
            self.lower.gun_spread = 3
        elif color == 'red':
            self.upper = Section(4, 3, 2, 'upper')
            self.upper.zone = self
            self.upper.c_action = 'interceptors (range1, dmg1-3, spread1-3)'
            self.lower = Section(2, 2, 3, 'lower')
            self.lower.zone = self
            self.lower.c_action = 'redbots'
        elif color == 'blue':
            self.upper = Section(4, 3, 2, 'upper')
            self.upper.zone = self
            self.upper.c_action = 'bluebots'
            self.lower = Section(2, 2, 3, 'lower')
            self.lower.zone = self
            self.lower.c_action = 'rockets (range2, dmg3)'
        self.level_layout = [self.lower, self.upper]

    def fullshow(self):
        returnlist = ["|--------- " + self.color.upper() + " Zone Status ---------"]
        returnlist.append("| THREAT TRACK: " + str(self.threat_track))
        returnlist.append("| Upper Level Gun: Power = "+str(self.upper.gunpower) +
                          ", Range = "+str(self.upper.gunrange)+", Spread = "+str(self.upper.gun_spread))
        returnlist.append("| Upper Level Shield: Max = "+str(self.upper.max_energy) +
                          ", Current = "+str(self.upper.current_energy))
        if self.color == 'red':
            returnlist.append("| Interceptors are " + ("present" if self.ship.interceptors else "gone"))
        elif self.color == 'white':
            returnlist.append("| Main Computer " + ("activated" if self.ship.main_computer else "NOT activated"))
        elif self.color == 'blue':
            returnlist.append("| Blue Bots are " + ("present" if self.ship.blue_bots else "gone"))
        returnlist.append("|----- Lift Status: Lift is "+("Working" if self.lift_is_working else "BROKEN"))+"------"
        returnlist.append("|----- Lift Status: Lift is "+("IN USE" if self.lift_in_use else "available")+"--------")
        returnlist.append("| Lower Level Gun: Power = "+str(self.lower.gunpower) +
                          ", Range = "+str(self.lower.gunrange)+", Spread = "+str(self.lower.gun_spread))
        returnlist.append("| Lower Level Reactor: Max = "+str(self.lower.max_energy) +
                          ", Current = "+str(self.lower.current_energy))
        if self.color == 'red':
            returnlist.append("| Red Bots are " + ("present" if self.ship.red_bots else "gone"))
        elif self.color == 'blue':
            returnlist.append("| Rockets Remaining: " + str(self.ship.rockets_remaining))
        returnlist.append("|---------------------------------------------")
        returnlist.append("| Damage Taken: " + str(self.damage))
        returnlist.append("")
        return returnlist

    def refshow(self):
        returnlist = ["|---------- " + self.color.upper() + " Zone  --------------"]
        returnlist.append("| THREAT TRACK: " + str(self.threat_track))
        returnlist.append("| Upper Level Gun: Power = "+str(self.upper.gunpower) +
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

    def do_damage(self, amount):
        shields = self.upper.current_energy
        if shields >= amount:
            self.upper.current_energy -= amount
            report = "%s shields hold against %d damage.  Shields at %d energy." % (
                self.color.capitalize(), amount, self.upper.current_energy)
        else:
            result_damage = amount - self.upper.current_energy
            self.damage += result_damage
            if self.damage > self.max_hp:
                self.ship.explode(report)
            report = "%s shields %d -> 0.  %d damage taken, HP -> %d." % (
                self.color.capitalize(), self.upper.current_energy, result_damage, self.max_hp-self.damage)
            self.upper.current_energy = 0
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
        self.rockets_remaining = 3
        self.fuel_capsules = 3
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

    def explode(self, report):
        for thing in report:
            print(thing)
        print("Boom. Death.  Game Over.")
        sys.exit(0)


class Player(object):
    def __init__(self, p_name=''):
        self.location = 1
        self.level = 1
        self.name = p_name
        self.score = 0
        self.board = ''
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

    def get_from_player(self, prompt, validinputs):
        while 1:
            response = input(prompt).lower()
            if isinstance(validinputs[0], int):
                try:
                    response = int(response)
                except:
                    self.tellplayer("Enter a valid number")
                    continue
            if response in validinputs:
                break
            else:
                self.tellplayer("Not a valid choice.  Choose from: " + str(validinputs))
        return response

    def instr(self):
        self.tellplayer(" ---------- Player Commands: (use only one word, no trailing space) --------")
        self.tellplayer("|     SHIP: Show the layout of the ship for reference")
        self.tellplayer("|     WHAT: Show all the cards you've played (plus previous phases)")
        self.tellplayer("| TRANSFER: Transfer cards")
        self.tellplayer("|     PLAY: Play a card")
        self.tellplayer("|   PICKUP: Pick up a card")
        self.tellplayer("|    PHASE: Move to the next phase")
        self.tellplayer("|     DRAW: Draw new card to your hand")
        self.tellplayer("|   THREAT: Draw new threat card")
        self.tellplayer("|     SHOW: View threats")

    def show_history(self):
        for i, turn in enumerate(self.card_slots):
            self.tellplayer(str(i+1)+": "+str(turn))

    def show_ship(self):
        for thing in self.board.ship.show_ship_reference():
            self.tellplayer(thing)

    def show_threats(self):
        for zone in self.board.ship.zone_layout:
            self.tellplayer("|----- "+zone.color.upper()+" ZONE THREATS -------")
            for card in zone.threats.cards:
                self.tellplayer(card.read_card())

    def phaseup(self):
        self.board.phase += 1
        self.board.deal_new_phase()
        if self.board.phase == 2:
            self.slots_available = [4, 5, 6, 7]
        elif self.board.phase == 3:
            self.slots_available = [8, 9, 10, 11, 12]

    def drawcard(self):
        self.board.deck.deal([self.hand], 1)

    def threatcard(self):
        # threat_level = self.get_from_player(" '1' for Normal, '2' for Serious > ", [1, 2])
        turn_appearance = self.get_from_player(" Turn appearance > ", self.slots_available)
        zone_placement = self.get_from_player(" '1': red zone, '2': white zone, '3': blue zone > ", [1, 2, 3])
        the_zone = self.board.ship.zone_layout[zone_placement-1]
        self.board.threat_appearance[turn_appearance] = the_zone
        self.board.threat_deck.deal([the_zone.threats], 1)
        the_zone.threats.cards[-1].turn_appearance = turn_appearance
        the_zone.threats.cards[-1].zone = the_zone

    def playcard(self):
        cardnum = self.get_from_player(" Card to Play: ", range(1, len(self.hand.cards)+1)) - 1
        slotnum = self.get_from_player(" Slot to Play in: ", self.slots_available) - 1
        chosencard = self.hand.cards[cardnum]
        if self.card_slots[slotnum] != 0:
            self.pickup(slotnum+1)
        self.card_slots[slotnum] = chosencard
        del self.hand.cards[cardnum]
        self.card_slots[slotnum].state = self.get_from_player(
            " (M) for move side or (A) for action side: ", ['m', 'a'])

    def pickup(self, opt=0):
        if opt:
            slotnum = opt-1
        else:
            slotnum = self.get_from_player(" Which slot to pickup card > ", self.slots_available) - 1
        thecard = self.card_slots[slotnum]
        if thecard != 0:
            self.hand.add(thecard)
            self.card_slots[slotnum] = 0
            thecard.state = 0
        self.tellplayer("Picked up %s from slot %d" % (thecard, slotnum+1))

    def delayed(self, timeslot):
        # This will delay this player one turn from given timeslot
        self.card_slots.insert(timeslot-1, 0)
        try:
            nextzero = self.card_slots[timeslot:].index(0)
            del self.card_slots[timeslot+nextzero]
        except:
            del self.card_slots[-1]

    def playturn(self):
        while self.board.phase < 4:
            self.tellplayer("------ PHASE: "+str(self.board.phase) +
                            ", PLAYER "+self.name.upper()+", Slots Avaiable: " +
                            str(self.slots_available)+" -----")
            self.tellplayer(self.hand)

            userinput = self.get_from_player(" Take Action > ", list(self.actions.keys()))
            self.actions[userinput]()



