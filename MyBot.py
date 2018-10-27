import sys
import hlt

from hlt import constants
from hlt.positionals import Direction

import random
#import numpy as np
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()

# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
me = game.me
game_map = game.game_map
shipyard_position = me.shipyard.position

if me.shipyard.position.x == (game_map.width / 4) or me.shipyard.position.y == (game_map.height / 4):
    PLAYERS = 2
else:
    PLAYERS = 4

board_sizes = [32, 40, 48, 56, 64]
for b in board_sizes:
    if game_map.width == b:
        BOARD_SIZE = b
 

#MAX_SHIPS = 



#constants: PLAYERS | BOARD_SIZE | 
game.ready("holahula") #ready up

""" <<<Game Loop>>> """
ship_status = {}

while True:
    game.update_frame()

    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    directions_not_still = [Direction.North, Direction.South, Direction.East, Direction.West]

    position_choices = [] #co-ords that ships are moving to
    ships = me.get_ships()

    #go from least halite to most to avoid crashes
    ships.sort(key = lambda x: x.halite_amount)#, reverse = True)


    #LOGIC FOR SHIPS THAT CANNOT MOVE
    for ship in ships:
        if ship.halite_amount < game_map[ship.position].halite_amount * 0.1:
            position_choices.append(ship.position)
            command_queue.append(ship.stay_still())
            ships.remove(ship)

    for ship in ships:
        if ship.id not in ship_status:
            logging.info("Ship {} has spawned on turn {} at {}".format(ship.id, game.turn_number, me.shipyard.position))
            ship_status[ship.id] = "depositing"


        position_options = ship.position.get_surrounding_cardinals() + [ship.position]
        shipyard_options = me.shipyard.position.get_surrounding_cardinals()

        # {(0,1): (19,38)}
        position_dict = {} #holds all the ship's possible moves
 
        # {(0,1):500}
        halite_dict = {} #holds amount of halite at x, y coordinate

        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n] 

        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            #if position not in position_choices: #not a tile another ship is moving into
            if direction == Direction.Still:   #affects logic for "collecting" - makes it more likely to stay still than to move 
                halite_dict[direction] = halite_amount * 2.5
            else:
                halite_dict[direction] = halite_amount #- (0.1 * game_map[ship.position].halite_amount)

        if ship_status[ship.id] == "depositing":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "collecting"
                directions = Direction().get_all_cardinals()
                random.shuffle(directions)
                for dir in directions:
                    if position_dict[dir] not in position_choices:# and game_map[position_dict[dir]].is_empty:
                        position_choices.append(position_dict[dir])
                        command_queue.append(ship.move(dir))
                        logging.info("Ship {} is moving {} from {} to {}".format(ship.id,Direction().convert(dir), ship.position , position_dict[dir]))
                        no_legal_moves = False
                        break
                if no_legal_moves:
                    position_choices.append(position_dict[Direction.East])
                    command_queue.append(ship.move(Direction.East))
            else:
                if game_map[ship.position].halite_amount > (ship.halite_amount / 8) and ship.halite_amount < 800 and ship.position not in position_choices:
                    move = Direction.Still
                    logging.info("Ship {} is moving {} from {} to {}".format(ship.id, Direction().convert(move), ship.position , position_dict[Direction.Still]))
                    position_choices.append(position_dict[move])
                    command_queue.append(ship.move(move))
                else:
                    moves = game_map.get_unsafe_moves(ship.position, me.shipyard.position)
                    for move in moves:
                        if position_dict[move] not in position_choices:
                            position_choices.append(position_dict[move])
                            command_queue.append(ship.move(move))
                            logging.info("Ship {} is moving {} from {} to {}".format(ship.id, Direction().convert(move), ship.position, position_dict[move]))
                            no_legal_moves = False
                            break
                    if no_legal_moves:
                        for dir in sorted(halite_dict, key = halite_dict.get, reverse = True):
                            move = position_dict[dir]
                            if move not in position_choices:
                                position_choices.append(move)
                                command_queue.append(ship.move(dir))
                                logging.info("Ship {} is moving {} from {} to {}".format(ship.id, Direction().convert(dir), ship.position, position_dict[dir]))
                                break
                        
        elif ship_status[ship.id] == "collecting":
            for dir in sorted(halite_dict, key = halite_dict.get, reverse = True):
                move = position_dict[dir]
                if move not in position_choices:
                    position_choices.append(move)
                    command_queue.append(ship.move(dir))
                    logging.info("Ship {} is moving {} from {} to {}".format(ship.id, Direction().convert(dir), ship.position, position_dict[dir]))
                    no_legal_moves = False
                    break
            if no_legal_moves:
                move = Direction.West
                logging.info("Ship {} is moving {} from {} to {}".format(ship.id, Direction().convert(move), ship.position, position_dict[Direction.West]))
                position_choices.append(position_dict[move])
                command_queue.append(ship.move(move))

        if ship.halite_amount >= constants.MAX_HALITE / 2: #ship collects to 250 then returns
            ship_status[ship.id] = "depositing"
            
        no_legal_moves = True

    if game.turn_number <= constants.MAX_TURNS *.75 and len(me.get_ships()) <= 20:    #first period, prioritize making ships 
        if me.halite_amount >= constants.SHIP_COST and me.shipyard.position not in position_choices:# and len(me.get_ships()) < 10:
            command_queue.append(me.shipyard.spawn())
    
    #end of ships for loop
    game.end_turn(command_queue)

