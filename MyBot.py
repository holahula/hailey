import sys
import hlt

from hlt import constants
from hlt.positionals import Direction

import random

import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()

# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
me = game.me
game_map = game.game_map
shipyard_position = me.shipyard.position

game.ready("holahula")

""" <<<Game Loop>>> """
ship_status = {}

while True:
    game.update_frame()

    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

    position_choices = [] #physical co-ords on map itself
    
    for ship in me.get_ships():
        #logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        if ship.id not in ship_status:
            logging.info("Ship {} has spawned".format(ship.id))
            ship_status[ship.id] = "collecting"

        position_options = ship.position.get_surrounding_cardinals() + [ship.position]
        shipyard_options = me.shipyard.position.get_surrounding_cardinals()

        # {(0,1): (19,38)}
        position_dict = {} #holds all possible moves

        # {(0,1):500}
        halite_dict = {} #holds all halite at x, y coordinate
        #{(0, 1):200} cost to move to this tile
        cost_dict = {}

        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n] 

        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            if position not in position_choices: #not a tile another ship is moving into
                if direction == Direction.Still:   #affects logic for "collecting" - makes it more likely to stay still than to move 
                    halite_dict[direction] = halite_amount * 2
                else:
                    halite_dict[direction] = halite_amount

        if ship_status[ship.id] == "depositing":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "collecting"
            else:
                if game_map[ship.position].halite_amount > (ship.halite_amount / 8) and ship.halite_amount < 800:
                    move = Direction.Still
                    position_choices.append(position_dict[move])
                    command_queue.append(ship.move(move))
                else:
                    move = game_map.naive_navigate(ship, me.shipyard.position)
                    position_choices.append(position_dict[move])
                    command_queue.append(ship.move(move))
            
        elif ship_status[ship.id] == "collecting":
            if ship.position == me.shipyard.position:
                for position in shipyard_options:
                    if game_map[position].is_empty:
                        move = game_map.naive_navigate(ship, position)
                        command_queue.append(ship.move(move))
                        deadlock = False
                        break
                if deadlock:
                    command_queue.append(ship.move(Direction.East))
            else:
                directional_choice = max(halite_dict, key=halite_dict.get)
                if halite_dict[directional_choice] == 0:
                    position_choices.append(position_dict[Direction.West])
                    command_queue.append(ship.move(Direction.West))
                else:
                    position_choices.append(position_dict[directional_choice])
                    command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))

            if ship.halite_amount > constants.MAX_HALITE / 2.5: #ship collects to 250 then returns
                ship_status[ship.id] = "depositing"

        deadlock = True

    if game.turn_number <= constants.MAX_TURNS *.75 and len(me.get_ships()) < 20:    #first period, prioritize making ships 
        if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and me.shipyard.position not in position_choices:# and len(me.get_ships()) < 10:
            command_queue.append(me.shipyard.spawn())
    # elif me.halite_amount >= constants.SHIP_COST and game_map[me.shipyard].is_occupied and me.shipyard.position not in position_choices:
    #     command_queue.append(me.shipyard.spawn())
    #END OF TURN    
    game.end_turn(command_queue)


# for direction in direction_order:
#                         if position_dict[direction] not in position_choices and position_dict[direction] != me.shipyard.position:
#                             position_choices.append(position_dict[direction])
#                             command_queue.append(ship.move(direction))
#                             break