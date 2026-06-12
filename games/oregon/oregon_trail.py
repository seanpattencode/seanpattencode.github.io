#!/usr/bin/env python3
"""
OREGON TRAIL
Original programming by Bill Heinemann - 1971
Python version - 2025

This program simulates a trip over the Oregon Trail from
Independence, Missouri to Oregon City, Oregon in 1847.

Includes integrated automated player and comprehensive test suite.
"""

import random
import time
import sys
import os
import json
import argparse
import io
import contextlib
from typing import Optional, Tuple, List, Dict, Any


# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class OregonTrail:
    """Main game class for Oregon Trail"""

    # Constants
    TOTAL_MILES = 2040
    SOUTH_PASS = 950
    BLUE_MOUNTAINS = 1700

    # Dates for turns (turn_number -> date string)
    DATES = {
        0: "MARCH 29",
        1: "APRIL 12",
        2: "APRIL 26",
        3: "MAY 10",
        4: "MAY 24",
        5: "JUNE 7",
        6: "JUNE 21",
        7: "JULY 5",
        8: "JULY 19",
        9: "AUGUST 2",
        10: "AUGUST 16",
        11: "AUGUST 31",
        12: "SEPTEMBER 13",
        13: "SEPTEMBER 27",
        14: "OCTOBER 11",
        15: "OCTOBER 25",
        16: "NOVEMBER 8",
        17: "NOVEMBER 22",
        18: "DECEMBER 6",
        19: "DECEMBER 20",
    }

    # Event probabilities (cumulative percentages)
    EVENT_DATA = [6, 11, 13, 15, 17, 22, 32, 35, 37, 42, 44, 54, 64, 69, 95]

    def __init__(self, seed: Optional[int] = None, auto_player=None):
        """Initialize game state

        Args:
            seed: Random seed for deterministic gameplay
            auto_player: AutoPlayer instance for programmatic play
        """
        if seed is not None:
            random.seed(seed)

        self.seed = seed
        self.auto_player = auto_player

        self.oxen_cost = 0  # A
        self.bullets = 0  # B
        self.clothing = 0  # C
        self.food = 0  # F
        self.misc_supplies = 0  # M1
        self.cash = 0  # T
        self.mileage = 0  # M
        self.mileage_prev = 0  # M2

        self.turn_number = 0  # D3
        self.shooting_skill = 0  # D9
        self.eating_choice = 0  # E

        # Flags
        self.injury_flag = False  # K8
        self.serious_illness_flag = False  # S4
        self.south_pass_cleared = False  # F1
        self.blue_mountains_cleared = False  # F2
        self.blizzard_flag = False  # L1
        self.fort_option_flag = True  # X1 (-1 means fort available)
        self.mileage_display_flag = False  # M9

        # Shooting words
        self.shooting_words = ["BANG", "BLAM", "POW", "WHAM"]

        # Replay recording
        self.replay_log = []
        self.decision_number = 0

    def print_instructions(self):
        """Display game instructions"""
        print()
        print()
        print("THIS PROGRAM SIMULATES A TRIP OVER THE OREGON TRAIL FROM")
        print("INDEPENDENCES, MISSOURI TO OREGON CITY, OREGON IN 1847.")
        print("YOUR FAMILY OF FIVE WILL COVER THE 2040 MILE OREGON TRAIL")
        print("IN 5-6 MONTHS --- IF YOU MAKE IT ALIVE.")
        print()
        print("YOU HAD SAVED $900 TO SPEND FOR THE TRIP, AND YOU'VE JUST")
        print("   PAID $200 FOR A WAGON.")
        print("YOU WILL NEED TO SPEND THE REST OF YOUR MONEY ON THE")
        print("   FOLLOWING ITEMS:")
        print()
        print("     OXEN - YOU CAN SPEND $200-$300 ON YOUR TEAM")
        print("            THE MORE YOU SPEND, THE FASTER YOU'LL GO")
        print("               BECAUSE YOU'LL HAVE BETTER ANIMALS")
        print()
        print("     FOOD - THE MORE YOU HAVE, THE LESS CHANCE THERE")
        print("               IS OF GETTING SICK")
        print()
        print("     AMMUNITION - $1 BUYS A BELT OF 50 BULLETS")
        print("            YOU WILL NEED BULLETS FOR ATTACKS BY ANIMALS")
        print("               AND BANDITS, AND FOR HUNTING FOOD")
        print()
        print("     CLOTHING - THIS IS ESPECIALLY IMPORTANT FOR THE COLD")
        print("               WEATHER YOU WILL ENCOUNTER WHEN CROSSING")
        print("               THE MOUNTAINS")
        print()
        print("     MISCELLANEOUS SUPPLIES - THIS INCLUDES MEDICINE AND")
        print("              OTHER THINGS YOU WILL NEED FOR SICKNESS")
        print("              AND EMERGENCY REPAIRS")
        print()
        print()
        print("YOU CAN SPEND ALL YOUR MONEY BEFORE YOU START YOUR TRIP -")
        print("OR YOU CAN SAVE SOME OF YOUR CASH TO SPEND AT FORTS ALONG")
        print("THE WAY WHEN YOU RUN LOW. HOWEVER, ITEMS COST MORE AT")
        print("THE FORTS. YOU CAN ALSO GO HUNTING ALONG THE WAY TO GET")
        print("MORE FOOD.")
        print("WHENEVER YOU HAVE TO USE YOUR TRUSTY RIFLE ALONG THE WAY,")
        print("YOU WILL BE TOLD TO TYPE IN THAT WORD (ONE THAT SOUNDS LIKE A")
        print("GUN SHOT). THE FASTER YOU TYPE IN THAT WORD AND HIT THE")
        print('"RETURN" KEY, THE BETTER LUCK YOU\'LL HAVE WITH YOUR GUN.')
        print()
        print("AT EACH TURN, ALL ITEMS ARE SHOWN IN DOLLAR AMOUNTS")
        print("EXCEPT BULLETS")
        print("WHEN ASKED TO ENTER MONEY AMOUNTS, DON'T USE A \"$\".")
        print()
        print("GOOD LUCK!!!")

    def get_input(self, prompt: str, valid_range: Optional[tuple] = None) -> float:
        """Get numeric input from user with validation"""
        while True:
            try:
                if self.auto_player:
                    response = self.auto_player.get_decision(self, 'numeric')
                    self.replay_log.append(('numeric', response))
                    print(f"{prompt}{response}")
                else:
                    response = input(prompt)

                value = float(response)
                if valid_range:
                    min_val, max_val = valid_range
                    if value < min_val or value > max_val:
                        if min_val == max_val:
                            print("IMPOSSIBLE")
                        elif value < min_val:
                            print("NOT ENOUGH")
                        else:
                            print("TOO MUCH")
                        continue
                return value
            except ValueError:
                print("PLEASE ENTER A NUMBER")

    def get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input from user"""
        while True:
            if self.auto_player:
                response = self.auto_player.get_decision(self, 'yes_no')
                self.replay_log.append(('yes_no', response))
                print(f"{prompt}{response}")
            else:
                response = input(prompt).strip().upper()

            response = response.strip().upper()
            if response in ["YES", "NO"]:
                return response == "YES"
            print("PLEASE ANSWER YES OR NO")

    def initial_purchases(self):
        """Handle initial resource purchases - now pre-filled with balanced defaults"""
        print()
        print()
        print("YOUR WAGON HAS BEEN STOCKED WITH SUPPLIES:")
        print()

        # Pre-filled balanced strategy values (reduced to give starting cash)
        self.oxen_cost = 250
        self.food = 150
        ammo_dollars = 75
        self.clothing = 75
        self.misc_supplies = 50

        self.bullets = 50 * ammo_dollars
        self.cash = 700 - (self.oxen_cost + self.food + ammo_dollars + self.clothing + self.misc_supplies)

        print(f"  OXEN TEAM: ${self.oxen_cost}")
        print(f"  FOOD: ${int(self.food)}")
        print(f"  AMMUNITION: ${ammo_dollars} ({int(self.bullets)} BULLETS)")
        print(f"  CLOTHING: ${int(self.clothing)}")
        print(f"  MISCELLANEOUS SUPPLIES: ${int(self.misc_supplies)}")
        print()
        print(f"CASH ON HAND: ${self.cash}")
        print()
        print("MONDAY MARCH 29 1847")
        print()

    def print_status(self):
        """Display current game status"""
        # Ensure non-negative values
        self.food = max(0, self.food)
        self.bullets = max(0, self.bullets)
        self.clothing = max(0, self.clothing)
        self.misc_supplies = max(0, self.misc_supplies)

        # Convert to integers for display
        self.food = int(self.food)
        self.bullets = int(self.bullets)
        self.clothing = int(self.clothing)
        self.misc_supplies = int(self.misc_supplies)
        self.cash = int(self.cash)
        self.mileage = int(self.mileage)

        # Check for medical bills
        if self.serious_illness_flag or self.injury_flag:
            self.cash -= 20
            if self.cash < 0:
                return self.die("YOU CAN'T AFFORD A DOCTOR")
            print("DOCTOR'S BILL IS $20")
            self.serious_illness_flag = False
            self.injury_flag = False

        # Display mileage
        if self.mileage_display_flag:
            print("TOTAL MILEAGE IS 950")
            self.mileage_display_flag = False
        else:
            print(f"TOTAL MILEAGE IS {self.mileage}")

        # Display resources
        print(f"{'FOOD':<15}{'BULLETS':<15}{'CLOTHING':<15}{'MISC. SUPP.':<15}{'CASH':<15}")
        print(f"{self.food:<15}{self.bullets:<15}{self.clothing:<15}{self.misc_supplies:<15}{self.cash:<15}")

    def turn_choice(self) -> int:
        """Get player's choice for the turn"""
        if self.food < 13:
            print("YOU'D BETTER DO SOME HUNTING OR BUY FOOD SOON!!!!")

        if self.fort_option_flag:
            print("DO YOU WANT TO (1) STOP AT THE NEXT FORT, (2) HUNT, ", end="")
            print("OR (3) CONTINUE")
            choice = int(self.get_input("", (1, 3)))
            return choice
        else:
            print("DO YOU WANT TO (1) HUNT, OR (2) CONTINUE")
            choice = int(self.get_input("", (1, 2)))
            if choice == 1:
                # Check if enough bullets
                if self.bullets <= 39:
                    print("TOUGH---YOU NEED MORE BULLETS TO GO HUNTING")
                    return self.turn_choice()
                return 2  # Hunt (maps to choice 2 in main logic)
            else:
                return 3  # Continue (maps to choice 3 in main logic)

    def stop_at_fort(self):
        """Handle stopping at a fort for supplies"""
        print("ENTER WHAT YOU WISH TO SPEND ON THE FOLLOWING")

        # Food
        print("FOOD", end="")
        food_cost = self.get_purchase_amount()
        self.food += (2/3) * food_cost

        # Ammunition
        print("AMMUNITION", end="")
        ammo_cost = self.get_purchase_amount()
        self.bullets = int(self.bullets + (2/3) * ammo_cost * 50)

        # Clothing
        print("CLOTHING", end="")
        clothing_cost = self.get_purchase_amount()
        self.clothing += (2/3) * clothing_cost

        # Miscellaneous
        print("MISCELLANEOUS SUPPLIES", end="")
        misc_cost = self.get_purchase_amount()
        self.misc_supplies += (2/3) * misc_cost

        self.mileage -= 45

    def get_purchase_amount(self) -> float:
        """Get purchase amount and validate against cash"""
        purchase = self.get_input("? ", (0, float('inf')))
        if purchase < 0:
            return 0

        self.cash -= purchase
        if self.cash < 0:
            print("YOU DON'T HAVE THAT MUCH--KEEP YOUR SPENDING DOWN")
            print("YOU MISS YOUR CHANCE TO SPEND ON THAT ITEM")
            self.cash += purchase
            return 0
        return purchase

    def shoot(self) -> int:
        """Shooting mini-game - returns reaction time score"""
        word_index = random.randint(0, 3)
        shooting_word = self.shooting_words[word_index]

        print(f"TYPE {shooting_word}")

        if self.auto_player:
            response, reaction_time = self.auto_player.get_shooting_response(shooting_word)
            self.replay_log.append(('shoot', (shooting_word, response, reaction_time)))
            print(response)
        else:
            start_time = time.time()
            response = input().strip().upper()
            end_time = time.time()
            reaction_time = int((end_time - start_time) * 1000)  # milliseconds

        # Adjust for shooting skill (1=best, 5=worst)
        reaction_score = (reaction_time / 100) - (self.shooting_skill - 1)

        print()

        # Penalty for wrong word
        if response != shooting_word:
            reaction_score = 9

        return max(0, int(reaction_score))

    def hunt(self):
        """Go hunting for food"""
        if self.bullets <= 39:
            print("TOUGH---YOU NEED MORE BULLETS TO GO HUNTING")
            return

        self.mileage -= 45
        reaction_score = self.shoot()

        if reaction_score <= 1:
            print("RIGHT BETWEEN THE EYES---YOU GOT A BIG ONE!!!!")
            print("FULL BELLIES TONIGHT!")
            self.food += 52 + random.random() * 6
            self.bullets -= 10 + int(random.random() * 4)
        elif 100 * random.random() < 13 * reaction_score:
            print("YOU MISSED---AND YOUR DINNER GOT AWAY.....")
        else:
            print("NICE SHOT--RIGHT ON TARGET--GOOD EATIN' TONIGHT!!")
            self.food += 48 - 2 * reaction_score
            self.bullets -= 10 + 3 * reaction_score

    def choose_eating(self):
        """Choose how well to eat"""
        if self.food < 13:
            return self.die("YOU RAN OUT OF FOOD AND STARVED TO DEATH")

        print("DO YOU WANT TO EAT (1) POORLY (2) MODERATELY")
        print("OR (3) WELL", end="")

        while True:
            self.eating_choice = int(self.get_input("? ", (1, 3)))
            food_consumed = 8 + 5 * self.eating_choice

            if self.food >= food_consumed:
                self.food -= food_consumed
                break
            else:
                print("YOU CAN'T EAT THAT WELL")

        # Calculate mileage for this turn
        self.mileage += 200 + (self.oxen_cost - 220) / 3 + 10 * random.random()

    def random_event(self):
        """Generate and handle random events"""
        r1 = 100 * random.random()

        event_index = 0
        for i, threshold in enumerate(self.EVENT_DATA):
            if r1 <= threshold:
                event_index = i
                break
        else:
            event_index = 15  # Helpful Indians

        if event_index == 0:
            print("WAGON BREAKS DOWN--LOSE TIME AND SUPPLIES FIXING IT")
            self.mileage -= 15 + 5 * random.random()
            self.misc_supplies -= 8
        elif event_index == 1:
            print("OX INJURES LEG---SLOWS YOU DOWN REST OF TRIP")
            self.mileage -= 25
            self.oxen_cost -= 20
        elif event_index == 2:
            print("BAD LUCK---YOUR DAUGHTER BROKE HER ARM")
            print("YOU HAD TO STOP AND USE SUPPLIES TO MAKE A SLING")
            self.mileage -= 5 + 4 * random.random()
            self.misc_supplies -= 2 + 3 * random.random()
        elif event_index == 3:
            print("OX WANDERS OFF---SPEND TIME LOOKING FOR IT")
            self.mileage -= 17
        elif event_index == 4:
            print("YOUR SON GETS LOST---SPEND HALF THE DAY LOOKING FOR HIM")
            self.mileage -= 10
        elif event_index == 5:
            print("UNSAFE WATER--LOSE TIME LOOKING FOR CLEAN SPRING")
            self.mileage -= 10 * random.random() + 2
        elif event_index == 6:
            if self.mileage <= 950:
                print("HEAVY RAINS---TIME AND SUPPLIES LOST")
                self.food -= 10
                self.bullets -= 500
                self.misc_supplies -= 15
                self.mileage -= 10 * random.random() + 5
            else:
                return self.cold_weather()
        elif event_index == 7:
            print("BANDITS ATTACK")
            reaction_score = self.shoot()
            self.bullets -= 20 * reaction_score

            if self.bullets < 0:
                print("YOU RAN OUT OF BULLETS---THEY GET LOTS OF CASH")
                self.cash = self.cash / 3
            elif reaction_score <= 1:
                print("QUICKEST DRAW OUTSIDE OF DODGE CITY!!!")
                print("YOU GOT 'EM!")
            else:
                print("YOU GOT SHOT IN THE LEG AND THEY TOOK ONE OF YOUR OXEN")
                self.injury_flag = True
                print("BETTER HAVE A DOC LOOK AT YOUR WOUND")
                self.misc_supplies -= 5
                self.oxen_cost -= 20
        elif event_index == 8:
            print("THERE WAS A FIRE IN YOUR WAGON--FOOD AND SUPPLIES DAMAGE!")
            self.food -= 40
            self.bullets -= 400
            self.misc_supplies -= random.random() * 8 + 3
            self.mileage -= 15
        elif event_index == 9:
            print("LOSE YOUR WAY IN HEAVY FOG---TIME IS LOST")
            self.mileage -= 10 + 5 * random.random()
        elif event_index == 10:
            print("YOU KILLED A POISONOUS SNAKE AFTER IT BIT YOU")
            self.bullets -= 10
            self.misc_supplies -= 5
            if self.misc_supplies < 0:
                return self.die("YOU DIE OF SNAKEBITE SINCE YOU HAVE NO MEDICINE")
        elif event_index == 11:
            print("WAGON GETS SWAMPED FORDING RIVER--LOSE FOOD AND CLOTHES")
            self.food -= 30
            self.clothing -= 20
            self.mileage -= 20 + 20 * random.random()
        elif event_index == 12:
            print("WILD ANIMALS ATTACK!")
            reaction_score = self.shoot()

            if self.bullets <= 39:
                print("YOU WERE TOO LOW ON BULLETS--")
                print("THE WOLVES OVERPOWERED YOU")
                self.injury_flag = True
                return self.check_illness()

            if reaction_score <= 2:
                print("NICE SHOOTIN' PARDNER---THEY DIDN'T GET MUCH")
            else:
                print("SLOW ON THE DRAW---THEY GOT AT YOUR FOOD AND CLOTHES")

            self.bullets -= 20 * reaction_score
            self.clothing -= reaction_score * 4
            self.food -= reaction_score * 8
        elif event_index == 13:
            print("HAIL STORM---SUPPLIES DAMAGED")
            self.mileage -= 5 + random.random() * 10
            self.bullets -= 200
            self.misc_supplies -= 4 + random.random() * 3
        elif event_index == 14:
            # Illness based on eating choice
            if self.eating_choice == 1:
                return self.check_illness()
            elif self.eating_choice == 3:
                if random.random() < 0.5:
                    return self.check_illness()
            else:  # eating_choice == 2
                if random.random() <= 0.25:
                    return self.check_illness()
        else:  # event_index == 15
            print("HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD")
            self.food += 14

    def cold_weather(self):
        """Handle cold weather event"""
        print("COLD WEATHER---BRRRRRRR!--YOU ", end="")

        insufficient_clothing = False
        if self.clothing < 22 + 4 * random.random():
            print("DON'T ", end="")
            insufficient_clothing = True

        print("HAVE ENOUGH CLOTHING TO KEEP YOU WARM")

        if insufficient_clothing:
            return self.check_illness()

    def mountains(self):
        """Handle mountain passage"""
        if self.mileage <= 950:
            return

        # Random mountain events
        if random.random() * 10 > 9 - ((self.mileage/100 - 15)**2 + 72) / ((self.mileage/100 - 15)**2 + 12):
            print("RUGGED MOUNTAINS")

            if random.random() <= 0.1:
                print("YOU GOT LOST---LOSE VALUABLE TIME TRYING TO FIND TRAIL!")
                self.mileage -= 60
            elif random.random() <= 0.11:
                print("WAGON DAMAGED!---LOSE TIME AND SUPPLIES")
                self.misc_supplies -= 5
                self.bullets -= 200
                self.mileage -= 20 + 30 * random.random()
            else:
                print("THE GOING GETS SLOW")
                self.mileage -= 45 + random.random() / 0.02

        # South Pass - check first
        if not self.south_pass_cleared:
            self.south_pass_cleared = True
            if random.random() >= 0.8:
                print("YOU MADE IT SAFELY THROUGH SOUTH PASS--NO SNOW")
            else:
                self.check_blizzard()

        # Blue Mountains
        if self.mileage >= 1700 and not self.blue_mountains_cleared:
            self.blue_mountains_cleared = True
            if random.random() >= 0.7:
                pass  # No special message, just clear the flag
            else:
                self.check_blizzard()

        # Check if mountain events pushed us back below South Pass
        if self.mileage <= 950:
            self.mileage_display_flag = True

    def check_blizzard(self):
        """Check for blizzard in mountains"""
        print("BLIZZARD IN MOUNTAIN PASS--TIME AND SUPPLIES LOST")
        self.blizzard_flag = True
        self.food -= 25
        self.misc_supplies -= 10
        self.bullets -= 300
        self.mileage -= 30 + 40 * random.random()

        if self.clothing < 18 + 2 * random.random():
            return self.check_illness()

    def check_illness(self):
        """Check for illness"""
        if 100 * random.random() < 10 + 35 * (self.eating_choice - 1):
            # No illness
            return

        if 100 * random.random() < 100 - (40 / (4 ** (self.eating_choice - 1))):
            # Mild or bad illness
            illness_type = random.random()
            if illness_type < 0.5:
                print("MILD ILLNESS---MEDICINE USED")
                self.mileage -= 5
                self.misc_supplies -= 2
            else:
                print("BAD ILLNESS---MEDICINE USED")
                self.mileage -= 5
                self.misc_supplies -= 2
        else:
            # Serious illness
            print("SERIOUS ILLNESS---")
            print("YOU MUST STOP FOR MEDICAL ATTENTION")
            self.misc_supplies -= 10
            self.serious_illness_flag = True

        if self.misc_supplies < 0:
            return self.die("YOU RAN OUT OF MEDICAL SUPPLIES", "PNEUMONIA")

        if self.blizzard_flag:
            self.blizzard_flag = False

    def die(self, cause: str, death_type: Optional[str] = None):
        """Handle player death"""
        print(cause)

        if death_type:
            print(f"YOU DIED OF {death_type}")
        elif self.injury_flag:
            print("YOU DIED OF INJURIES")

        print()
        print("DUE TO YOUR UNFORTUNATE SITUATION, THERE ARE A FEW")
        print("FORMALITIES WE MUST GO THROUGH")
        print()

        self.get_yes_no("WOULD YOU LIKE A MINISTER? ")

        self.get_yes_no("WOULD YOU LIKE A FANCY FUNERAL? ")

        next_of_kin = self.get_yes_no("WOULD YOU LIKE US TO INFORM YOUR NEXT OF KIN? ")

        if not next_of_kin:
            print("BUT YOUR AUNT SADIE IN ST. LOUIS IS REALLY WORRIED ABOUT YOU")
            print()
        else:
            print("THAT WILL BE $4*50 FOR THE TELEGRAPH CHARGE.")
            print()

        print("WE THANK YOU FOR THIS INFORMATION AND WE ARE SORRY YOU")
        print("DIDN'T MAKE IT TO THE GREAT TERRITORY OF OREGON")
        print("BETTER LUCK NEXT TIME")
        print()
        print()
        print(" " * 30 + "SINCERELY")
        print()
        print(" " * 17 + "THE OREGON CITY CHAMBER OF COMMERCE")

        return True  # Game over

    def victory(self):
        """Handle winning the game"""
        # Calculate final day
        mileage_diff = self.mileage - self.mileage_prev
        if mileage_diff == 0:
            fraction = 1.0
        else:
            fraction = (self.TOTAL_MILES - self.mileage_prev) / mileage_diff
        self.food += (1 - fraction) * (8 + 5 * self.eating_choice)

        print()
        print("YOU FINALLY ARRIVED AT OREGON CITY")
        print("AFTER 2040 LONG MILES---HOORAY!!!!!")
        print("A REAL PIONEER!")
        print()

        # Calculate arrival date
        days_fraction = int(fraction * 14)
        total_days = self.turn_number * 14 + days_fraction

        # Calculate day of week
        day_of_week = (days_fraction + 1) % 7
        day_names = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        print(day_names[day_of_week], end=" ")

        # Calculate month and day
        if total_days <= 124:
            month = "JULY"
            day = total_days - 93
        elif total_days <= 155:
            month = "AUGUST"
            day = total_days - 124
        elif total_days <= 185:
            month = "SEPTEMBER"
            day = total_days - 155
        elif total_days <= 216:
            month = "OCTOBER"
            day = total_days - 185
        elif total_days <= 246:
            month = "NOVEMBER"
            day = total_days - 216
        else:
            month = "DECEMBER"
            day = total_days - 246

        print(f"{month} {day} 1847")
        print()

        # Display final resources
        print(f"{'FOOD':<15}{'BULLETS':<15}{'CLOTHING':<15}{'MISC. SUPP.':<15}{'CASH':<15}")
        final_food = max(0, int(self.food))
        final_bullets = max(0, int(self.bullets))
        final_clothing = max(0, int(self.clothing))
        final_misc = max(1, int(self.misc_supplies))
        final_cash = max(0, int(self.cash))
        print(f"{final_food:<15}{final_bullets:<15}{final_clothing:<15}{final_misc:<15}{final_cash:<15}")
        print()

        print(" " * 11 + "PRESIDENT JAMES K. POLK SENDS YOU HIS")
        print(" " * 17 + "HEARTIEST CONGRATULATIONS")
        print()
        print(" " * 11 + "AND WISHES YOU A PROSPEROUS LIFE AHEAD")
        print()
        print(" " * 22 + "AT YOUR NEW HOME")

        return True  # Game over

    def play_turn(self) -> bool:
        """Play one turn of the game. Returns True if game is over."""
        # Check if won
        if self.mileage >= self.TOTAL_MILES:
            return self.victory()

        # Check if took too long
        if self.turn_number >= 20:
            print("YOU HAVE BEEN ON THE TRAIL TOO LONG ------")
            print("YOUR FAMILY DIES IN THE FIRST BLIZZARD OF WINTER")
            return True

        # Display date
        print()
        print(f"MONDAY {self.DATES[self.turn_number]} 1847")
        print()

        # Display status
        result = self.print_status()
        if result:
            return True

        # Get player choice
        choice = self.turn_choice()

        # Execute choice
        if choice == 1:
            self.stop_at_fort()
        elif choice == 2:
            self.hunt()
        # choice 3 is continue (do nothing)

        # Eating
        result = self.choose_eating()
        if result:
            return True

        # Random events
        result = self.random_event()
        if result:
            return True

        # Mountains
        result = self.mountains()
        if result:
            return True

        # Advance to next turn
        self.mileage_prev = self.mileage
        self.turn_number += 1

        # Toggle fort option
        self.fort_option_flag = not self.fort_option_flag

        return False

    def play(self):
        """Main game loop"""
        # Set default shooting skill (2 = good shot)
        if self.auto_player:
            self.shooting_skill = self.auto_player.params['shooting_skill']
        else:
            self.shooting_skill = 2  # Default to "good shot"

        # Initial purchases
        self.initial_purchases()

        # Main game loop
        while True:
            game_over = self.play_turn()
            if game_over:
                break


# ============================================================================
# AUTOMATED PLAYER
# ============================================================================

class AutoPlayer:
    """Automated player that makes decisions programmatically"""

    def __init__(self, strategy: str = "balanced"):
        """
        Initialize auto player with a strategy

        Args:
            strategy: "balanced", "aggressive", "conservative", or "custom"
        """
        self.strategy = strategy
        self.decision_count = 0
        self.decisions = []

        # Strategy parameters
        if strategy == "balanced":
            self.params = {
                'oxen': 250,
                'food': 200,
                'ammo': 100,
                'clothing': 100,
                'misc': 50,
                'eating_preference': 2,  # Moderate
                'hunt_threshold': 80,  # Hunt when food < 80
                'fort_threshold': 30,  # Stop at fort when supplies < 30
                'shooting_skill': 2,  # Good shot
                'shoot_reaction_ms': 150,  # Fast but realistic
            }
        elif strategy == "aggressive":
            self.params = {
                'oxen': 300,  # Fast travel
                'food': 100,  # Less food, more hunting
                'ammo': 150,  # More bullets
                'clothing': 50,
                'misc': 100,
                'eating_preference': 1,  # Eat poorly
                'hunt_threshold': 50,
                'fort_threshold': 20,
                'shooting_skill': 1,  # Ace marksman
                'shoot_reaction_ms': 100,
            }
        elif strategy == "conservative":
            self.params = {
                'oxen': 200,  # Slower but cheaper
                'food': 250,  # More food
                'ammo': 50,
                'clothing': 150,  # More clothing
                'misc': 50,
                'eating_preference': 3,  # Eat well
                'hunt_threshold': 100,
                'fort_threshold': 50,
                'shooting_skill': 3,  # Fair
                'shoot_reaction_ms': 200,
            }
        else:
            # Default balanced
            self.params = {
                'oxen': 250,
                'food': 200,
                'ammo': 100,
                'clothing': 100,
                'misc': 50,
                'eating_preference': 2,
                'hunt_threshold': 80,
                'fort_threshold': 30,
                'shooting_skill': 2,
                'shoot_reaction_ms': 150,
            }

    def get_decision(self, game_state, decision_type: str) -> str:
        """
        Make a decision based on game state and decision type

        Args:
            game_state: The OregonTrail game instance
            decision_type: Type of decision needed

        Returns:
            Decision as string
        """
        self.decision_count += 1
        decision = None

        if decision_type == 'yes_no':
            # Handle yes/no questions (death questions, etc)
            decision = "NO"

        elif decision_type == 'numeric':
            # During gameplay - determine context
            decision = self._make_gameplay_decision(game_state)

        self.decisions.append((decision_type, decision, {
            'turn': game_state.turn_number,
            'mileage': game_state.mileage,
            'food': game_state.food,
            'bullets': game_state.bullets,
        }))

        return decision

    def _make_gameplay_decision(self, game_state) -> str:
        """Make decisions during gameplay"""
        # Check what kind of decision is needed
        if game_state.food < 13:
            # Low food warning was shown
            if hasattr(game_state, 'fort_option_flag') and game_state.fort_option_flag:
                # Can stop at fort, hunt, or continue
                if game_state.food < 20 and game_state.cash > 50:
                    return "1"  # Stop at fort
                elif game_state.bullets > 40:
                    return "2"  # Hunt
                else:
                    return "3"  # Continue
            else:
                # Can only hunt or continue
                if game_state.bullets > 40:
                    return "1"  # Hunt
                else:
                    return "2"  # Continue
        else:
            # Normal turn decision
            if hasattr(game_state, 'fort_option_flag') and game_state.fort_option_flag:
                # Fort, hunt, or continue
                if game_state.food < self.params['hunt_threshold'] and game_state.bullets > 40:
                    return "2"  # Hunt
                elif (game_state.food < self.params['fort_threshold'] or
                      game_state.clothing < self.params['fort_threshold'] or
                      game_state.misc_supplies < self.params['fort_threshold']) and game_state.cash > 100:
                    return "1"  # Stop at fort
                else:
                    return "3"  # Continue
            else:
                # Hunt or continue
                if game_state.food < self.params['hunt_threshold'] and game_state.bullets > 40:
                    return "1"  # Hunt
                else:
                    return "2"  # Continue

        # Check if this is an eating choice
        if hasattr(game_state, 'eating_choice'):
            # Adjust eating based on food supply
            if game_state.food > 100:
                return str(self.params['eating_preference'])
            elif game_state.food > 50:
                return "2"  # Moderate
            else:
                return "1"  # Poorly

        # Default to continue
        return "3"

    def get_shooting_response(self, word: str) -> Tuple[str, int]:
        """
        Simulate shooting response

        Args:
            word: The word to type

        Returns:
            Tuple of (response_word, reaction_time_ms)
        """
        # Simulate reaction time with some variance
        base_time = self.params['shoot_reaction_ms']
        variance = random.randint(-30, 50)
        reaction_time = max(50, base_time + variance)

        # 95% chance of typing correctly
        if random.random() < 0.95:
            return (word, reaction_time)
        else:
            # Occasionally make a mistake
            wrong_words = ["BANG", "BLAM", "POW", "WHAM"]
            if word in wrong_words:
                wrong_words.remove(word)
            return (random.choice(wrong_words), reaction_time)


# ============================================================================
# REPLAY SYSTEM
# ============================================================================

class ReplaySystem:
    """System for saving and loading game replays"""

    @staticmethod
    def save_replay(game_state, filename: str):
        """Save a replay to file"""
        replay_data = {
            'version': '1.4',
            'seed': game_state.seed,
            'strategy': game_state.auto_player.strategy if game_state.auto_player else None,
            'decisions': game_state.replay_log,
            'final_state': {
                'won': game_state.mileage >= game_state.TOTAL_MILES,
                'turn_number': game_state.turn_number,
                'mileage': game_state.mileage,
                'food': game_state.food,
                'bullets': game_state.bullets,
                'clothing': game_state.clothing,
                'misc_supplies': game_state.misc_supplies,
                'cash': game_state.cash,
            }
        }

        with open(filename, 'w') as f:
            json.dump(replay_data, f, indent=2)

        return replay_data

    @staticmethod
    def load_replay(filename: str) -> Dict:
        """Load a replay from file"""
        with open(filename, 'r') as f:
            return json.load(f)

    @staticmethod
    def print_replay_summary(replay_data: Dict):
        """Print a summary of a replay"""
        print("\n" + "="*60)
        print("REPLAY SUMMARY")
        print("="*60)
        print(f"Seed: {replay_data['seed']}")
        print(f"Strategy: {replay_data['strategy']}")
        print(f"Total Decisions: {len(replay_data['decisions'])}")
        print(f"\nFinal State:")
        final = replay_data['final_state']
        print(f"  Won: {final['won']}")
        print(f"  Turn: {final['turn_number']}")
        print(f"  Mileage: {final['mileage']}/{2040}")
        print(f"  Food: {final['food']}")
        print(f"  Bullets: {final['bullets']}")
        print(f"  Clothing: {final['clothing']}")
        print(f"  Misc Supplies: {final['misc_supplies']}")
        print(f"  Cash: {final['cash']}")
        print("="*60)


# ============================================================================
# AUTOMATED PLAYTHROUGH FUNCTIONS
# ============================================================================

def play_automated_game(seed: int = 42, strategy: str = "balanced", verbose: bool = True):
    """
    Play an automated game with the specified seed and strategy

    Args:
        seed: Random seed for deterministic gameplay
        strategy: AI strategy to use
        verbose: Whether to show game output

    Returns:
        Tuple of (won, replay_data)
    """
    # Create auto player and game
    auto_player = AutoPlayer(strategy=strategy)
    game = OregonTrail(seed=seed, auto_player=auto_player)

    # Capture or show output based on verbose flag
    if verbose:
        game.play()
    else:
        # Suppress output
        with contextlib.redirect_stdout(io.StringIO()):
            game.play()

    # Save replay
    replay_file = f"replay_seed{seed}_{strategy}.json"
    replay_data = ReplaySystem.save_replay(game, replay_file)

    won = game.mileage >= game.TOTAL_MILES

    if verbose:
        print(f"\n{'='*60}")
        print(f"GAME SUMMARY")
        print(f"{'='*60}")
        print(f"Seed: {seed}")
        print(f"Strategy: {strategy}")
        print(f"Won: {won}")
        print(f"Turn: {game.turn_number}")
        print(f"Mileage: {game.mileage}/{game.TOTAL_MILES}")
        print(f"Food: {game.food}")
        print(f"Bullets: {game.bullets}")
        print(f"Cash: {game.cash}")
        print(f"Replay saved: {replay_file}")
        print(f"{'='*60}")

    return won, replay_data


def play_multiple_games(seed: int = 1, num_games: int = 5, strategy: str = "balanced", verbose: bool = False):
    """
    Play multiple automated games with consecutive seeds

    Args:
        seed: Starting random seed
        num_games: Number of games to play
        strategy: AI strategy to use
        verbose: Whether to show individual game outputs

    Returns:
        Dictionary with statistics
    """
    wins = 0
    total_mileage = 0
    total_turns = 0
    games_data = []

    print(f"\nPlaying {num_games} games starting from seed {seed}...")
    print(f"Strategy: {strategy}")
    print("="*60)

    for i in range(num_games):
        current_seed = seed + i
        if not verbose:
            print(f"Game {i+1}/{num_games} (seed {current_seed})...", end=" ")

        won, replay_data = play_automated_game(current_seed, strategy, verbose)

        if won:
            wins += 1
            if not verbose:
                print("WON")
        else:
            if not verbose:
                print("LOST")

        final = replay_data['final_state']
        total_mileage += final['mileage']
        total_turns += final['turn_number']
        games_data.append(replay_data)

    # Print summary
    print("\n" + "="*60)
    print("MULTI-GAME SUMMARY")
    print("="*60)
    print(f"Games Played: {num_games}")
    print(f"Games Won: {wins} ({wins/num_games*100:.1f}%)")
    print(f"Games Lost: {num_games - wins}")
    print(f"Average Mileage: {total_mileage/num_games:.1f}")
    print(f"Average Turns: {total_turns/num_games:.1f}")
    print("="*60)

    return {
        'num_games': num_games,
        'wins': wins,
        'losses': num_games - wins,
        'win_rate': wins / num_games,
        'avg_mileage': total_mileage / num_games,
        'avg_turns': total_turns / num_games,
        'games': games_data
    }


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_manual_game_syntax():
    """Test that manual game starts without errors"""
    print("Test 1: Manual game syntax check...")
    # Since game is in same file, just check if we can instantiate it
    try:
        game = OregonTrail(seed=1, auto_player=AutoPlayer())
        print("  ✓ PASSED: No syntax errors")
    except Exception as e:
        raise AssertionError(f"Syntax error: {e}")


def test_no_riders():
    """Test that riders have been completely removed"""
    print("\nTest 2: Verify riders removed...")

    # Check that riders_attack method doesn't exist in the code
    import inspect
    methods = [method for method in dir(OregonTrail) if not method.startswith('_')]
    assert "riders_attack" not in methods, "riders_attack() method still exists"

    # Check source code
    source = inspect.getsource(OregonTrail)
    assert "FRIENDLY RIDERS" not in source, "Friendly rider messages still in code"
    assert "LOOK HOSTILE" not in source, "Hostile rider messages still in code"
    assert "RIDERS AHEAD" not in source, "Rider messages still in code"

    print("  ✓ PASSED: All rider code removed")


def test_winning_game():
    """Test a game that wins"""
    print("\nTest 3: Winning game playthrough...")

    won, replay_data = play_automated_game(seed=200, strategy="aggressive", verbose=False)

    assert won, "Game should win with seed 200"
    assert replay_data['final_state']['won'], "Final state should show won=True"
    print("  ✓ PASSED: Game wins and saves replay")


def test_losing_game():
    """Test a game that loses"""
    print("\nTest 4: Losing game playthrough...")

    won, replay_data = play_automated_game(seed=31, strategy="balanced", verbose=False)

    assert not won, "Game should lose with seed 31"
    assert not replay_data['final_state']['won'], "Final state should show won=False"
    print("  ✓ PASSED: Game loses gracefully and saves replay")


def test_replay_file_format():
    """Test that replay file is valid JSON"""
    print("\nTest 5: Replay file format...")

    replay_file = "replay_seed200_aggressive.json"
    assert os.path.exists(replay_file), f"Replay file {replay_file} not found"

    with open(replay_file, 'r') as f:
        data = json.load(f)

    assert "seed" in data, "Replay missing seed"
    assert "strategy" in data, "Replay missing strategy"
    assert "decisions" in data, "Replay missing decisions"
    assert "final_state" in data, "Replay missing final_state"
    assert data["seed"] == 200, "Seed should be 200"
    assert data["strategy"] == "aggressive", "Strategy should be aggressive"
    assert len(data["decisions"]) > 0, "Should have decisions recorded"
    print("  ✓ PASSED: Replay file format valid")


def test_determinism():
    """Test that replays are deterministic"""
    print("\nTest 6: Determinism verification...")

    # Load original replay
    replay_file = "replay_seed200_aggressive.json"
    original_replay = ReplaySystem.load_replay(replay_file)

    # Re-run with same seed and strategy
    seed = original_replay['seed']
    strategy = original_replay['strategy']

    auto_player = AutoPlayer(strategy=strategy)
    game = OregonTrail(seed=seed, auto_player=auto_player)

    # Suppress output
    with contextlib.redirect_stdout(io.StringIO()):
        game.play()

    # Compare final states
    original_final = original_replay['final_state']

    assert game.mileage == original_final['mileage'], f"Mileage mismatch: {game.mileage} vs {original_final['mileage']}"
    assert game.turn_number == original_final['turn_number'], f"Turn mismatch: {game.turn_number} vs {original_final['turn_number']}"
    assert abs(game.food - original_final['food']) < 0.01, f"Food mismatch: {game.food} vs {original_final['food']}"
    assert game.bullets == original_final['bullets'], f"Bullets mismatch: {game.bullets} vs {original_final['bullets']}"

    print("  ✓ PASSED: Replay is deterministic (100%)")


def test_multiple_games():
    """Test multiple game statistics"""
    print("\nTest 7: Multiple games statistics...")

    stats = play_multiple_games(seed=1, num_games=5, strategy="balanced", verbose=False)

    assert stats['num_games'] == 5, "Should play 5 games"
    assert stats['wins'] + stats['losses'] == 5, "Wins + losses should equal total games"
    assert stats['avg_mileage'] > 0, "Should have average mileage"
    assert stats['avg_turns'] > 0, "Should have average turns"
    print("  ✓ PASSED: Multiple games run successfully")


def test_all_strategies():
    """Test that all strategies work"""
    print("\nTest 8: All strategy types...")

    for strategy in ["balanced", "aggressive", "conservative"]:
        won, replay_data = play_automated_game(seed=50, strategy=strategy, verbose=False)
        assert replay_data is not None, f"Strategy {strategy} failed"
        print(f"  ✓ {strategy.upper()} strategy works")

    print("  ✓ PASSED: All strategies functional")


def test_game_completes():
    """Test that game completes without hanging"""
    print("\nTest 9: Game completion (no hangs)...")

    # Test with aggressive strategy for quick completion
    won, replay_data = play_automated_game(seed=999, strategy="aggressive", verbose=False)

    assert replay_data is not None, "Game should complete"
    print("  ✓ PASSED: Game completes without hanging")


def test_no_rider_messages_in_output():
    """Test that no rider messages appear in actual gameplay"""
    print("\nTest 10: No rider messages in gameplay...")

    # Capture output from a game
    auto_player = AutoPlayer(strategy="balanced")
    game = OregonTrail(seed=42, auto_player=auto_player)

    output_buffer = io.StringIO()
    with contextlib.redirect_stdout(output_buffer):
        game.play()

    output = output_buffer.getvalue()

    # Check for any rider-related messages
    rider_messages = [
        "RIDERS AHEAD",
        "LOOK HOSTILE",
        "FRIENDLY RIDERS",
        "TACTICS",
        "RIDERS WERE",
        "MASSACRED BY THE RIDERS",
        "KNIFED",
    ]

    for msg in rider_messages:
        assert msg not in output, f"Found rider message in output: {msg}"

    print("  ✓ PASSED: No rider messages in gameplay output")


# ============================================================================
# MAIN TEST SUITE
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("OREGON TRAIL - COMPREHENSIVE TEST SUITE")
    print("Version 1.4 - No Riders")
    print("="*60)

    try:
        test_manual_game_syntax()
        test_no_riders()
        test_winning_game()
        test_losing_game()
        test_replay_file_format()
        test_determinism()
        test_multiple_games()
        test_all_strategies()
        test_game_completes()
        test_no_rider_messages_in_output()

        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nSummary:")
        print("  • Game runs without errors")
        print("  • All rider code removed")
        print("  • Winning and losing paths work")
        print("  • Replay system is functional")
        print("  • Determinism is verified")
        print("  • All strategies work")
        print("  • No hangs or crashes")
        print("\nOregon Trail implementation is production ready!")
        print("="*60)

        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point with command line argument handling"""
    parser = argparse.ArgumentParser(
        description='Oregon Trail - Game, Automated Player, and Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Play manually
  python3 oregon_trail.py

  # Run all tests
  python3 oregon_trail.py --test

  # Play a single automated game
  python3 oregon_trail.py --play --seed 200 --strategy aggressive

  # Play multiple games
  python3 oregon_trail.py --play --seed 1 --multiple 5 --strategy balanced

  # Play quietly (less output)
  python3 oregon_trail.py --play --seed 42 --quiet

  # Verify no riders in code
  python3 oregon_trail.py --verify-no-riders
        """
    )

    parser.add_argument('--test', action='store_true',
                        help='Run comprehensive test suite')
    parser.add_argument('--play', action='store_true',
                        help='Run automated playthrough mode')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for deterministic gameplay (default: 42)')
    parser.add_argument('--strategy', type=str, default='balanced',
                        choices=['balanced', 'aggressive', 'conservative'],
                        help='AI strategy to use (default: balanced)')
    parser.add_argument('--multiple', type=int, metavar='N',
                        help='Play N games with consecutive seeds')
    parser.add_argument('--quiet', action='store_true',
                        help='Reduce output verbosity')
    parser.add_argument('--verify-no-riders', action='store_true',
                        help='Only run rider removal verification test')

    args = parser.parse_args()

    # Run tests
    if args.test:
        return run_all_tests()

    # Verify no riders mode
    if args.verify_no_riders:
        print("="*60)
        print("VERIFYING RIDER REMOVAL")
        print("="*60)
        try:
            test_no_riders()
            test_no_rider_messages_in_output()
            print("\n✓ Verification complete - no riders found!")
            return 0
        except AssertionError as e:
            print(f"\n✗ Verification failed: {e}")
            return 1

    # Play mode
    if args.play:
        if args.multiple:
            # Multiple games
            play_multiple_games(
                seed=args.seed,
                num_games=args.multiple,
                strategy=args.strategy,
                verbose=not args.quiet
            )
        else:
            # Single game
            play_automated_game(
                seed=args.seed,
                strategy=args.strategy,
                verbose=not args.quiet
            )
        return 0

    # Default: run manual game
    game = OregonTrail()
    game.play()
    return 0


if __name__ == "__main__":
    sys.exit(main())
