# Author: Miguel Sancho

from mesa import Agent


class Worker(Agent):

    def __init__(self, unique_id, warehouse):
        super().__init__(unique_id, warehouse)
        self.warehouse = warehouse
        self.destination = None
        self.products = 0
        self.packages = 0

    def step(self):
        if self.destination is None:
            if self.packages == 0 and self.products == 0:
                self.random_walk()
        else:
            self.move_to_destination()

    def move_to_destination(self):
        next_pos = self.warehouse.step_to_dest(self.pos, self.destination)
        self.warehouse.grid.move_agent(self, next_pos)

    def random_walk(self):
        next_pos = self.warehouse.find_next_position_for_random_walk(self.pos)
        self.warehouse.grid.move_agent(self, next_pos)

    def is_free(self):
        if self.destination is None:
            return True
        else:
            return False
