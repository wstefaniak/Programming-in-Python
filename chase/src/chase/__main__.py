import argparse
import configparser
import json
import csv
import os
from math import sqrt
import random
import logging


class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Sheep(Animal):
    counter = 0

    def __init__(self, init_pos_limit):
        self.s_id = Sheep.counter
        Sheep.counter += 1
        self.alive = True
        self.x = random.uniform(-init_pos_limit, init_pos_limit)
        self.y = random.uniform(-init_pos_limit, init_pos_limit)

    def move(self, sheep_move_dist):
        logging.debug('Sheep.move() method called.')
        direction = random.choice(["north", "south", "east", "west"])
        if direction == "north":
            self.y += sheep_move_dist
            logging.info(f"Sheep[{self.s_id}] moved north to position ({self.x:.3f}, {self.y:.3f})")
        elif direction == "south":
            self.y -= sheep_move_dist
            logging.info(f"Sheep[{self.s_id}] moved south to position ({self.x:.3f}, {self.y:.3f})")
        elif direction == "east":
            self.x += sheep_move_dist
            logging.info(f"Sheep[{self.s_id}] moved east to position ({self.x:.3f}, {self.y:.3f})")
        elif direction == "west":
            self.x -= sheep_move_dist
            logging.info(f"Sheep[{self.s_id}] moved west to position ({self.x:.3f}, {self.y:.3f})")


class Wolf(Animal):
    def __init__(self, move_dist):
        self.x = 0.0
        self.y = 0.0
        self.move_dist = move_dist
        self.chased_sheep = None
        self.eaten_sheep = None

    def move(self, sheep_positions):
        logging.info("'wolf.move()' method called")
        if not sheep_positions:
            return
        min_dist = float("inf")
        min_dist_index = None
        for sheep in sheep_positions:
            if not sheep.alive:
                continue
            dist = sqrt((sheep.x - self.x) ** 2 + (sheep.y - self.y) ** 2)
            if dist < min_dist:
                min_dist = dist
                min_dist_index = sheep.s_id
        if min_dist <= self.move_dist:
            self.eaten_sheep = min_dist_index
            self.x = sheep_positions[min_dist_index].x
            self.y = sheep_positions[min_dist_index].y
            logging.info(f"Wolf moved to eaten Sheep[{min_dist_index}] position ({self.x:.3f}, {self.y:.3f})")
            sheep_positions[min_dist_index].alive = False
            sheep_positions[min_dist_index].x = None
            sheep_positions[min_dist_index].y = None
        else:
            self.chased_sheep = min_dist_index
            self.x += (sheep_positions[min_dist_index].x - self.x) * self.move_dist / min_dist
            self.y += (sheep_positions[min_dist_index].y - self.y) * self.move_dist / min_dist
            logging.info(f"Wolf moved to position ({self.x:.3f}, {self.y:.3f})")


def move_sheep(sheep_positions, sheep_move_dist):
    logging.info("'move_sheep()' function called")
    for sheep in sheep_positions:
        if not sheep.alive:
            logging.info(f"Sheep[{sheep.s_id}] was eaten.")
            continue
        sheep.move(sheep_move_dist)


def display_status(round_num, wolf, sheep_positions):
    logging.debug("'display_status()' function called")
    print(f"\nRound {round_num + 1}")
    print(f"Wolf position: ({wolf.x:.3f}, {wolf.y:.3f})")
    num_alive = sum(1 for sheep in sheep_positions if sheep.alive)
    print(f"Number of alive sheep: {num_alive}")
    if wolf.eaten_sheep is not None:
        print(f"Sheep {wolf.eaten_sheep} was eaten")
        logging.info(f"Sheep {wolf.eaten_sheep} was eaten, {num_alive} sheep left.")
        wolf.eaten_sheep = None
        wolf.chased_sheep = None
    if wolf.chased_sheep is not None:
        print(f"Wolf is chasing sheep {wolf.chased_sheep}")
        logging.info(f"Wolf is chasing sheep {wolf.chased_sheep}")


def save_positions(data, save_dir):
    logging.debug("'save_positions()' function called.")
    if save_dir is None:
        path = "pos.json"
    else:
        path = f"{save_dir}/pos.json"
    with open(path, "w") as file:
        json.dump([data], file, indent=4)
        logging.debug("Saved positions of animals in every round of this simulation to file 'pos.json'.")


def save_alive_count(round_num, num_alive, save_dir):
    logging.debug("'save_alive_count()' function called.")
    if round_num == 0:
        mode = "w"
    else:
        mode = "a"
    if save_dir is None:
        path = "alive.csv"
    else:
        path = f"{save_dir}/alive.csv"
    with open(path, mode) as file:
        writer = csv.writer(file)
        writer.writerow([round_num, num_alive])
        logging.debug(f"Count of alive sheep in round {round_num} appended to file 'alive.csv'")


def simulate(max_rounds, size_of_flock, init_pos_limit, sheep_move_dist, wolf_move_dist, save_dir, numeric_log_level,
             wait):
    data = []
    if numeric_log_level is not None:
        if save_dir is None:
            logging.basicConfig(filename='chase.log', filemode='w', level=numeric_log_level)
        else:
            logging.basicConfig(filename=f'{save_dir}/chase.log', filemode='w', level=numeric_log_level)
    sheep_positions = [Sheep(init_pos_limit) for _ in range(size_of_flock)]
    logging.info("Sheep positions initialized")
    wolf = Wolf(wolf_move_dist)
    logging.info(f"Wolf position initialized: x={wolf.x}, y={wolf.y}")
    round_num = 0
    while round_num < max_rounds:
        logging.debug(f"Starting round: {round_num}.")
        move_sheep(sheep_positions, sheep_move_dist)
        wolf.move(sheep_positions)
        num_alive = sum(1 for sheep in sheep_positions if sheep.alive)
        display_status(round_num, wolf, sheep_positions)
        round_data = {
            "round_no": round_num + 1,
            "wolf_pos": (wolf.x, wolf.y),
            "sheep_pos": [(sheep.x, sheep.y) for sheep in sheep_positions]
        }
        data.append(round_data)
        logging.debug(f"Appended data from round {round_num}.")
        save_alive_count(round_num, num_alive, save_dir)
        round_num += 1
        if num_alive == 0:
            logging.info("All sheep have been eaten")
            break
        if wait:
            os.system('pause')
    save_positions(data, save_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="auxiliary configuration file")
    parser.add_argument("-d", "--dir",
                        help="subdirectory where files pos.json, alive.csv, and — optionally — chase.log should be placed")
    parser.add_argument("-l", "--log",
                        help="if events should be logged (can be: DEBUG, INFO, WARNING, ERROR, or CRITICAL)")
    parser.add_argument("-r", "--rounds", type=int, help="maximum number of rounds")
    parser.add_argument("-s", "--sheep", type=int, help="size of a flock of sheep")
    parser.add_argument("-w", "--wait",
                        help="if simulation should be paused at the end of each round after displaying the basic information about the state of a simulation set to True")
    args = parser.parse_args()
    max_rounds = 50
    size_of_flock = 15
    init_pos_limit = 10.0
    sheep_move_dist = 0.5
    wolf_move_dist = 1.0
    save_dir = None
    numeric_log_level = None
    wait = False
    if args.config is not None:
        logging.debug("Using configuration file")
        config = configparser.ConfigParser()
        config.read(args.config)
        if config.getfloat('Terrain', 'InitPosLimit') <= 0:
            raise ValueError('Limit for sheep initial positions must be positive.')
        init_pos_limit = config.getfloat('Terrain', 'InitPosLimit')
        if config.getfloat('Movement', 'SheepMoveDist') <= 0 or config.getfloat('Movement', 'WolfMoveDist') <= 0:
            raise ValueError('Length by which animals move must be positive.')
        sheep_move_dist = config.getfloat('Movement', 'SheepMoveDist')
        wolf_move_dist = config.getfloat('Movement', 'WolfMoveDist')
    if args.dir is not None:
        if not os.path.exists(args.dir):
            logging.debug("Requested directory doesn't exist. Creating directory.")
            os.makedirs(args.dir)
        save_dir = args.dir
    if args.rounds is not None:
        if args.rounds <= 0:
            raise ValueError('Number of rounds must be a positive integer.')
        max_rounds = args.rounds
    if args.sheep is not None:
        if args.sheep <= 0:
            raise ValueError('Number of sheep in flock must be a positive integer.')
        size_of_flock = args.sheep
    if args.wait is not None:
        if str(args.wait) in ('true', 'True'):
            wait = True
        elif str(args.wait) in ('false', 'False'):
            wait = False
        else:
            raise TypeError("'wait' argument can only be either True or False")
    if args.log is not None:
        log_level = args.log
        numeric_log_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_log_level, int):
            raise ValueError(f'Invalid log level: "{log_level}". Try using "--help".')
    simulate(max_rounds, size_of_flock, init_pos_limit, sheep_move_dist, wolf_move_dist, save_dir, numeric_log_level,
             wait)


if __name__ == "__main__":
    main()
