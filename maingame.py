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
        self.threat_appearance = {}

    def deal_new_phase(self):
        self.deck.deal([x.hand for x in self.playerlist], 6)

    def reportout(self, report):
        for r in report:
            for player in self.playerlist:
                player.tellplayer(r)
        return []

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

    def threat_appears(self, turn):
        report = ["Turn %d: Threat Appearance Phase" % turn]
        if turn in self.threat_appearance.keys():
            this_zone = self.threat_appearance[turn]
            report.append("Threat appears!  Zone: "+this_zone.color)
            for c in this_zone.threats:
                if c.distance == 0:
                    this_card = c
                    break
            report.append(this_card.read_card())
            this_card.distance = len(this_zone.threat_track)
            report.append(this_zone.threat_track)
        else:
            report.append("No Threat Appears This Turn")
        return report

    def play_cards(self, turn):
        report = ["Turn %d: Player Card Phase" % turn]
        for player in self.playerlist:
            this_card = player.card_slots[turn-1]
            current_zone = self.ship.zone_layout[player.location]
            current_location = current_zone.level_layout[player.level]
            current_level = ['Lower', 'Upper']
            if this_card == 0:
                report.append(" -- Player %s didn't play anything" % player.name)
            elif this_card.state == 'm':
                report.append(" -- Player %s plays %s" % (player.name, this_card.move))
                if this_card.move in ['RED', 'BLUE']:
                    movement = 1 if this_card.move == 'BLUE' else -1
                    new_zone = self.ship.zone_layout.index(current_zone) + movement
                    if new_zone-1 in range(3):
                        report.append(" -- Player %s moves from %s Zone to %s Zone"
                                      % (player.name, current_zone.name.upper(),
                                         self.ship.zone_layout[new_zone].name.upper()))
                        player.location += movement
                    else:
                        report.append(" -- Player %s is in %s Zone. No movement possible."
                                      % (player.name, current_zone.name.upper()))
                else:
                    if current_zone.lift_in_use or not current_zone.lift_is_working:
                        report.append(" -- Lift in %s Zone is unavailable.  Player %s delayed."
                                      % (current_zone.name.upper(), player.name))
                        player.delayed(turn)
                    player.level = 0 if player.level else 1
                    report.append(" -- Player %s moved to %s Level, %s zone"
                                  % (player.name, current_level[player.level], current_zone.name))
            elif this_card.state == 'a':
                report.append(" -- Player %s plays %s" % (player.name, this_card.action))
                if this_card.action == 'A':
                    if current_location.guns_fired:
                        report.append(" -- Guns were already fired.  No result.")
                    else:
                        report.append(" -- %s Guns Fired" % current_level[player.level])
                        current_location.guns_fired = 1
                elif this_card.action == 'B' and current_zone.color == 'white':
                    fuel_caps = self.ship.fuel_capsules - 1
                    if fuel_caps in range(3):
                        self.ship.fuel_capsules = fuel_caps
                        report.append(" -- Main Reactor energy to %d. %d fuel caps remaining"
                                      % (current_location.max_energy, fuel_caps))
                        current_location.current_energy = current_location.max_energy
                    else:
                        report.append(" -- No fuel caps remaining.")
                elif this_card.action == 'B':
                    main_reactor = self.ship.white_zone.lower.current_energy
                    report.append(" -- %s zone reactor: %d out of %d. Main Reactor %d"
                                  % (current_zone.color.upper(), current_location.current_energy,
                                     current_location.max_energy, main_reactor))
                    reactor_space = max(current_location.max_energy - current_location.current_energy, 0)
                    refill = min(reactor_space, main_reactor)
                    report.append(" -- %d energy added to %s reactor from main.  Main reactor: %d remaining"
                                  % (refill, current_zone.color, main_reactor-refill))
                    current_location.current_energy += refill
                    self.ship.white_zone.lower.current_energy -= refill
                    # Todo: is this gonna work with hero cards?
                elif this_card.action == 'C':
                    report.append(" -- %s zone c-action (%s)")



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
            report = self.reportout(report)
            report.extend(self.threat_appears(turn))
            report = self.reportout(report)
            report.extend(self.play_cards(turn))

newgame = gameboard(1)
newgame.playgame()