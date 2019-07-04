# Author: Miguel Sancho Peña

import numpy as np
import seaborn as sb
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from mesa import Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from pypaths import astar
from worker import *
from cargoBay import *
from packaging import *
from storage import *
import math
from datetime import datetime
import random


class Warehouse(Model):

    def __init__(self, grid_w, grid_h, n_workers):
        self.orders = 0
        self.n_workers = n_workers
        self.scheduler = RandomActivation(self)
        self.grid = SingleGrid(grid_w, grid_h, torus=False)
        self.path_finder = astar.pathfinder(neighbors=self.get_empty_neighbourhood,
                                            distance=self.absolute_distance,
                                            cost=astar.fixed_cost(1))

        self.init_workers()
        self.packaging = Packaging("packaging", self, (14, 2)) #  for random pos self.grid.find_empty()
        self.storage = Storage("storage", self, (11, 19))
        self.cargo_bay = CargoBay("cargo_bay", self, (0, 9))
        self.stations_locs = [self.packaging.pos, self.storage.pos, self.cargo_bay.pos]
        plt.ion()

    def add_order(self):
        self.orders += 1

    def step(self):
        if self.orders > 0:
            self.storage.orders += 1  # Transfer orders to storage
            self.orders -= 1

        self.storage.step()
        self.packaging.step()
        self.cargo_bay.step()
        self.scheduler.step()  # Step through workers.
        self.visualize()

    def init_workers(self):  # Creates workers and places them in random locations
        for i in range(self.n_workers):
            r = Worker(i, self)
            pos = self.grid.find_empty()
            self.grid.place_agent(r, pos)
            self.scheduler.add(r)

    def get_empty_neighbourhood(self, pos):
        return [n for n in self.grid.get_neighborhood(pos=pos, moore=True) if self.grid.is_cell_empty(n)]

    @staticmethod
    def absolute_distance(initial, final):
        return math.sqrt((initial[0] - final[0]) ** 2 + (initial[1] - final[1]) ** 2)

    def nearest_free_worker(self, pos):
        free_workers = [worker for worker in self.scheduler.agents if worker.is_free()]
        if len(free_workers) != 0:
            nearest_worker = np.argmin([self.absolute_distance(pos, worker.pos) for worker in free_workers])
            return free_workers[nearest_worker]
        else:
            return None

    def free_worker_at_pos(self, pos):  # Returns a free worker if any at position
        for worker in self.scheduler.agents:
            if worker.pos == pos:
                return worker
        return None

    def is_pos_empty(self, pos):
        if self.grid.is_cell_empty(pos) and pos not in self.stations_locs:
            return True
        else:
            return False

    def step_to_dest(self, pos, destination):
        n_steps, path = self.path_finder(pos, destination)
        if n_steps is None or n_steps <= 0:  # No path to destination
            next_pos = pos
        else:
            next_pos = path[1]
        return next_pos

    def find_next_position_for_random_walk(self, curr_pos):
        neighborhood = self.grid.get_neighborhood(curr_pos, moore=True)
        empty_neighborhood = [n for n in neighborhood if self.is_pos_empty(n)]
        if len(empty_neighborhood) > 0:
            next_index = np.random.randint(len(empty_neighborhood))
            next_pos = empty_neighborhood[next_index]
        else:
            next_pos = curr_pos
        return next_pos

    @staticmethod
    def print_grid(grid):
        colours = ListedColormap(['white', 'mediumblue', 'c', 'm', 'darkgreen', 'darkred'])  #  bg, storage, packaging, cargo, free worker, busy worker
        sb.heatmap(grid, vmin=0, vmax=6, cmap=colours, cbar=False, xticklabels=False,
                   yticklabels=False, linecolor='black', linewidths=0.7)
        plt.pause(0.15)
        plt.clf()

    def visualize(self):
        grid = np.zeros((self.grid.height, self.grid.width), dtype=int)
        grid[self.storage.pos] = 1
        grid[self.packaging.pos] = 2
        grid[self.cargo_bay.pos] = 3
        for worker in self.scheduler.agents:
            if worker.is_free():
                grid[worker.pos] = 4
            else:
                grid[worker.pos] = 5

        self.print_grid(grid)


class Clients:
    def __init__(self, demand_time):
        self.demand_t = demand_time  # demand time in seconds

    def make_order(self):
        if float(datetime.now().strftime('%S')) % self.demand_t == 0:
            return random.randint(0, 4)
        else:
            return 0


if __name__ == '__main__':
    warehouse = Warehouse(25, 25, 5)
    clients = Clients(36)

    while 1:
        orders = clients.make_order()
        for i in range(orders):
            warehouse.add_order()
        warehouse.step()
