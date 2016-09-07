import os
import sys
import gamemods
import cards


class Game(object):
    def __init__(self, num):
        self.num_players = num
        self.p_one = gamemods.Player('One', self)
        self.p_two = gamemods.Player('Two', self)
        self.p_three = gamemods.Player('Three', self)
        self.p_four = gamemods.Player('Four', self)
        self.p_five = gamemods.Player('Five', self)
        self.ship = gamemods.Ship()
        self.deck = gamemods.Deck()
        self.threat_deck = gamemods.Deck()
        self.phase = 1
        self.player_order = [self.p_one, self.p_two, self.p_three, self.p_four, self.p_five]
        self.playerlist = self.player_order[:self.num_players]
        self.threat_appearance = {}
        self.rockets_fired = []
        self.level_names = ['lower', 'upper']

    def test_game(self):
        for player in self.playerlist:
            self.deck.deal([player.hand], 12)
            for e, c in enumerate(player.hand.cards):
                player.card_slots[e] = c
            # print("Player %s Card Slots: %s" % (player.name, [str(x) for x in player.card_slots]))
        for turn, zone in enumerate(self.ship.zone_layout):
            self.threat_appearance[turn+1] = zone
            self.threat_deck.deal([zone.threats], 1)
            zone.threats.cards[-1].zone = zone

    def deal_new_phase(self):
        self.deck.deal([x.hand for x in self.playerlist], 6)

    def move_player(self, player, direction, turn):
        subreport = []
        current_zone = self.ship.zone_layout[player.location]
        if direction in ['RED', 'BLUE']:
            movement = 1 if direction == 'BLUE' else -1
            new_zone = player.location + movement
            if new_zone in range(3):
                subreport.append(" -- Player %s moves from %s Zone to %s Zone" % (
                    player.name, current_zone.color.capitalize(), self.ship.zone_layout[new_zone].color.capitalize()))
                player.location = new_zone
            else:
                subreport.append(" -- Player %s is in %s Zone. No movement possible."
                                 % (player.name, current_zone.color.capitalize()))
        elif direction == 'LIFT':
            if current_zone.lift_in_use or not current_zone.lift_is_working:
                subreport.append(" -- Lift in %s Zone is unavailable.  Player %s delayed."
                                 % (current_zone.color.capitalize(), player.name))
                player.delayed(turn)
            player.level = 0 if player.level else 1
            subreport.append(" -- Player %s moved to %s level, %s zone" % (
                player.name, current_zone.level_layout[player.level].name, current_zone.color))
        elif direction in ['00', '01', '02', '10', '11', '12']:
            new_level_name = self.level_names[int(direction[0])]
            new_zone = self.ship.zone_layout[int(direction[1])]
            subreport.append(" -- Player teleports to %s %s section" % (new_level_name, new_zone.color))
            player.location = int(direction[1])
            player.level = int(direction[0])
        return subreport

    def player_action(self, player, action, turn):
        subreport = []
        current_zone = self.ship.zone_layout[player.location]
        this_section = current_zone.level_layout[player.level]
        fire_cost = 1 if this_section.name == 'upper' or current_zone == 'white' else 0
        if action == 'A':
            if this_section.guns_fired:
                subreport.append(" -- Guns were already fired.  No result.")
            elif current_zone.lower.current_energy < fire_cost:
                subreport.append(" -- Not enough energy to fire guns!  No result.")
            else:
                current_zone.lower.current_energy -= fire_cost
                subreport.append(" -- %s %s Guns Fired, reactor energy remaining: %d" % (
                    current_zone.color.capitalize(), this_section.name, current_zone.lower.current_energy))
                this_section.guns_fired = 1
        elif action == 'B':
            if current_zone.color == 'white' and player.level == 0:
                fuel_caps = self.ship.fuel_capsules - 1
                if fuel_caps in range(3):
                    self.ship.fuel_capsules = fuel_caps
                    subreport.append(" -- Main Reactor energy to %d. %d fuel caps remaining"
                                     % (this_section.max_energy, fuel_caps))
                    this_section.current_energy = this_section.max_energy
                else:
                    subreport.append(" -- No fuel caps remaining.")
            else:
                draw_from = self.ship.white_zone.lower if player.level == 0 else current_zone.lower
                from_reactor = draw_from.current_energy
                energy_space = max(this_section.max_energy - this_section.current_energy, 0)
                this_thing = ["reactor", "Main"] if player.level == 0 else \
                    ["shields", current_zone.color.capitalize()]
                subreport.append(" -- %s zone %s: %d out of %d. %s Reactor %d" % (
                    current_zone.color.capitalize(), this_thing[0], this_section.current_energy,
                    this_section.max_energy, this_thing[1], from_reactor))
                refill = min(energy_space, from_reactor)
                subreport.append(" -- %d energy added to %s %s.  %s reactor: %d remaining" % (
                    refill, current_zone.color, this_thing[0], this_thing[1], from_reactor-refill))
                this_section.current_energy += refill
                draw_from.current_energy -= refill
        elif action == 'C':
            if 'computer' in this_section.c_action:
                subreport.append(" -- Main Computer Button Pressed")
                self.ship.main_computer = 1
            elif 'interceptors' in this_section.c_action:
                if self.ship.interceptors:
                    subreport.append(" -- Interceptors launched")
                    self.ship.interceptors = 0
                else:
                    subreport.append(" -- Interceptors already gone")
                    # Todo: finish interceptors - move player, get player back
            elif 'redbots' in this_section.c_action:
                subreport.append(" -- Red zone bots activated and following player")
                self.ship.red_bots = 0
                player.battlebots = 1
            elif 'bluebots' in this_section.c_action:
                subreport.append(" -- Blue zone bots activated and following player")
                self.ship.blue_bots = 0
                player.battlebots = 1
            elif 'rockets' in this_section.c_action:
                if turn in self.rockets_fired:
                    subreport.append(" -- Rocket were already fired this turn.  No effect.")
                elif self.ship.rockets_remaining:
                    self.rockets_fired.append(turn)
                    subreport.append(" -- Rockets fired.")
                    self.ship.rockets_remaining -= 1
                else:
                    subreport.append(" -- No rockets remain.  No effect.")
        elif action == 'bots':
            subreport.append(" -- Bots don't do anything yet.")
            # Todo: finish bots
        return subreport

    def reportout(self, report):
        # for player in self.playerlist:
        player = self.p_one
        for r in report:
            player.tellplayer(r)
            if 'GAMEOVER' in r:
                sys.exit(0)
        player.tellplayer("--------------------")
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
                # input("Press Enter to continue...")
        return report

    def threat_appears(self, turn):
        report = ["Turn %d: Threat Appearance Phase" % turn]
        if turn in self.threat_appearance.keys():
            this_zone = self.threat_appearance[turn]
            report.append("Threat appears!  Zone: "+this_zone.color)
            this_card = [c for c in this_zone.threats.cards if c.distance == 0][0]
            report.append(this_card.read_card())
            this_card.distance = len(this_zone.threat_track)
            this_card.track_section = 3
            report.append(this_zone.threat_track)
        else:
            report.append(" -- No Threat Appears This Turn")
        return report

    def play_cards(self, player, turn):
        this_card = player.card_slots[turn-1]
        report = ["Turn %d: Player %s Card Phase, Played --> %s" % (turn, player.name, this_card)]
        if this_card == 0:
            report.append(" -- Player %s didn't play anything" % player.name)
        elif this_card.state == 'm':
            report.extend(self.move_player(player, this_card.move, turn))
        elif this_card.state == 'a':
            report.extend(self.player_action(player, this_card.action, turn))
        else:
            print("Card State Error")
            sys.exit(0)
        return report

    def fire_guns(self, turn):
        report = ["Turn %d: Gun Firing Phase" % turn]
        white_guns = self.ship.white_zone.lower
        targets = {}
        zone_damage = {'red': 0, 'white': 0, 'blue': 0}
        for zone in self.ship.zone_layout:
            if len(zone.threats.cards) and zone.threats.cards[0].distance:
                targets[zone.color] = zone.threats.cards[0]
            else:
                zone.lower.guns_fired = 0
                zone.upper.guns_fired = 0
                continue
            if zone.color != 'white' and white_guns.guns_fired:
                if white_guns.gunrange < targets[zone.color].track_section:
                    report.append("(!) White lower section guns range too short!")
                else:
                    report.append("(!) White lower section guns fired: %d damage" % white_guns.gunpower)
                    zone_damage[zone.color] += white_guns.gunpower
            for level in zone.level_layout:
                if level.guns_fired:
                    # report.append("%s %s zone guns were fired" % (zone.color, level.name))
                    level.guns_fired = 0
                    if level.gunrange < targets[zone.color].track_section:
                        report.append("(!) %s %s section guns range too short!" % (
                            zone.color.capitalize(), level.name))
                    else:
                        report.append("(!) %s %s section guns fired: %d damage" % (
                            zone.color.capitalize(), level.name, level.gunpower))
                        zone_damage[zone.color] += level.gunpower
        if targets:
            if turn-1 in self.rockets_fired:
                closest_target = ['', 100]
                for color, t in targets.items():
                    if t.rocketable and t.distance < closest_target[1]:
                        closest_target = [color, t.distance]
                if closest_target[1] < 100:
                    report.append("(!) Rockets fired to %s zone threat" % closest_target[0])
                    zone_damage[closest_target[0]] += 3
                else:
                    report.append("(.) Rockets fired to nowhere.")
            if self.ship.interceptors == 0:  # 0 = interceptors are gone from the ship
                targets_distances = {y: x.track_section for y, x in targets.items()}
                # should be a dictionary of distance section for closest threat in each zone
                add_zones = [x for x, y in targets_distances.items() if y == 1]
                # should be a list of colors with a threat in the 1st distance section
                if len(add_zones) > 1:
                    add_damage = 3 if len(add_zones) == 1 else 1
                    for color in add_zones:
                        report.append("(!) Interceptors add %d damage to %s zone" % (add_damage, color))
                        zone_damage[color] += add_damage
                else:
                    report.append("(!) Threats out of range for interceptors.")
            for color, t in targets.items():
                if zone_damage[color] == 0:
                    continue
                report.append(" -- %s %s: Distance = %d, Section = %d, HP = %d, Shields = %d" % (
                    color.capitalize(), t.name, t.distance, t.track_section, t.hitpoints, t.shields))
                actual_damage = max(zone_damage[color] - t.shields, 0)
                report.append(" --(!) %s zone total damage = %d" % (color.capitalize(), zone_damage[color]))
                t.hitpoints -= actual_damage
                if t.hitpoints <= 0:
                    report.append(" -- -- Threat destroyed.")
                    del t.zone.threats.cards[0]
                else:
                    report.append(" -- -- Threat remaining HP = %d" % t.hitpoints)
        return report

    def threats_advance(self, turn):
        report = ["Turn %d: Threat Advancement Phase" % turn]
        for zone in self.ship.zone_layout:
            for threat in zone.threats.cards:
                if threat.distance == 0:
                    continue
                track_position = len(threat.zone.threat_track)-threat.distance
                report.append(" -- %s zone threat %s moves %d along threat track (New distance = %d)" % (
                    zone.color.capitalize(), threat.name, threat.speed, max(threat.distance-threat.speed, 0)))
                for spot in threat.zone.threat_track[track_position:track_position+threat.speed]:
                    if 'X' in spot:
                        report.extend(threat.x_action())
                    elif 'Y' in spot:
                        report.extend(threat.y_action())
                    elif 'Z' in spot:
                        report.extend(threat.z_action())
                    if '2' in spot:
                        report.append(" -- -- Enters 2nd distance section")
                        threat.track_section = 2
                    elif '1' in spot:
                        report.append(" -- -- Enters 1st distance section")
                        threat.track_section = 1
                threat.distance -= threat.speed
                if threat.distance <= 0:
                    report.append(" -- -- Threat %s removed from %s track" % (threat.name, zone.color))
                    zone.threats.cards.remove(threat)
        return report

    def playgame(self):
        os.system('cls')
        cards.randomly_populate(self.deck, 100)  # Temporarily removed for test deck
        self.deck.deal([x.hand for x in self.playerlist], 6)
        cards.definitely_populate(self.deck)  # Temporary test deck
        cards.generate_threat_tracks(self.ship)
        cards.generate_threat_deck(self.threat_deck)
        for player in self.playerlist:  # Temporarily removed for test cards
            player.playturn()
        # self.test_game()  # Temporary test to load player and threat cards
        turn = 0
        while turn < 12:
            report = []
            turn += 1
            # Temporarily removing main computer check for testing purposes
            # if turn in [3, 6, 10]:
            #     report.extend(self.computer_check(turn))
            # report = self.reportout(report)
            report.extend(self.threat_appears(turn))
            report = self.reportout(report)
            for player in self.playerlist:
                report.extend(self.play_cards(player, turn))
                report = self.reportout(report)
            report.extend(self.fire_guns(turn))
            report = self.reportout(report)
            report.extend(self.threats_advance(turn))
            report = self.reportout(report)
            input("Press Enter to Go to Next Turn > ")

newgame = Game(3)
newgame.playgame()
