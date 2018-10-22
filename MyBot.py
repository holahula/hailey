
import sys
# Import the Halite SDK, which will let you interact with the game.
import hlt
# This library contains constant values.
from hlt import constants

from hlt.positionals import Direction

import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """
ship_status = {}

while True:
    game.update_frame()
    me = game.me
    game_map = game.game_map

    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

    for ship in me.get_ships():
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))
        position_options = ship.position.get_surrounding_cardinals() + [ship.position]

        # {(0,1): (19,38)}
        position_dict = {}

        # {(0,1):500}
        halite_dict = {}

        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]

        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount
            halite_dict[position] = halite_amount

        if game.turn_number == 15:
            logging.info(choices)

        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            command_queue.append(ship.move(max(halite_dict, key=halite_dict.get)))
        else:
            command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
