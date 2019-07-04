# Author: Miguel Sancho

from mesa import Agent


class Storage(Agent):

    def __init__(self, unique_id, warehouse, pos):
        super().__init__(unique_id, warehouse)
        self.pos = pos
        self.warehouse = warehouse
        self.products = 100
        self.orders = 0

    def step(self):
        self.summon_worker()
        self.dispatch()
        print("[storage] products: {}  orders: {}".format(self.products, self.orders))

    def summon_worker(self):  # Call worker if orders in queue
        if self.orders > 0:
            if self.products > 0:
                nearest_worker = self.warehouse.nearest_free_worker(self.pos)
                if nearest_worker:
                    nearest_worker.destination = self.pos
                    self.orders -= 1
            else:
                print("[storage] WARNING: No stock available to process order.")

    def dispatch(self):
        worker_at_location = self.warehouse.free_worker_at_pos(self.pos)
        if worker_at_location:
            if worker_at_location.destination == self.pos:
                worker_at_location.destination = self.warehouse.packaging.pos # next station
                worker_at_location.products += 1
                self.products -= 1

