import sys
import hlt

from hlt import constants
from hlt.positionals import Direction

import random

import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
me = game.me
game_map = game.game_map

shipyard_position = me.shipyard.position


game.ready("holahula")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

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
                halite_dict[direction] = halite_amount #- ship.position.halite_amount / 10
                #cost_dict[direction] = ship.position.halite_amount / 10
            else:
                logging.info("attempting to move to same spot \n")

        if ship_status[ship.id] == "depositing":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "collecting"
            else:
                if game_map[ship.position].halite_amount > (ship.halite_amount / 8) and ship.halite_amount < 800:
                    move = game_map.naive_navigate(ship, ship.position)
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
                        command_queue.append(ship.move(game_map.naive_navigate(ship, position)))
                        break
            else:
                directional_choice = max(halite_dict, key=halite_dict.get)
                position_choices.append(position_dict[directional_choice])
                command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))
            
            if ship.halite_amount > constants.MAX_HALITE / 4: #ship collects to 250 then returns
                ship_status[ship.id] = "depositing"


    if len(me.get_ships()) == 0:
        command_queue.append(me.shipyard.spawn())
    elif game.turn_number <= constants.MAX_TURNS / 2:    #first period, prioritize making ships 
        if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:# and len(me.get_ships()) < 10:
            command_queue.append(me.shipyard.spawn())
    #b/w first third and first half, make ships ONLY if more than 2000 halite and MAX of 5 ships
    # elif game.turn_number <= (constants.MAX_TURNS / 2) and me.halite_amount > constants.SHIP_COST * 2 and len(me.get_ships()) < 5:
    #     if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
    #         command_queue.append(me.shipyard.spawn())
    # #third period, make ships ONLY if no ships alive

    #END OF TURN    
    game.end_turn(command_queue)

