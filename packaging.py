# Author: Miguel Sancho

from mesa import Agent


class Packaging(Agent):

    def __init__(self, unique_id, warehouse, pos):
        super().__init__(unique_id, warehouse)
        self.pos = pos
        self.warehouse = warehouse
        self.products = 0
        self.packages = 0
        self.workers_needed = 0

    def step(self):
        self.call_worker()
        self.dispatch()
        self.package_product()
        print("[packaging] products: {}  packages:{}  workers_needed: {}".format(self.products,
                                                                                   self.packages,
                                                                                   self.workers_needed))

    def call_worker(self):
        if self.workers_needed > 0:
            nearest_worker = self.warehouse.nearest_free_worker(self.pos)
            if nearest_worker:
                nearest_worker.destination = self.pos
                self.workers_needed -= 1

    def dispatch(self):
        worker_at_location = self.warehouse.free_worker_at_pos(self.pos)
        if worker_at_location:
            if worker_at_location.destination == self.pos:
                if worker_at_location.products > 0 and self.packages == 0:
                    self.products += 1
                    worker_at_location.products -= 1
                    worker_at_location.destination = None  # I don't have anything packaged yet

                elif worker_at_location.products == 0 and self.packages > 0:
                    self.packages -= 1
                    worker_at_location.packages += 1
                    worker_at_location.destination = self.warehouse.cargo_bay.pos

                elif worker_at_location.products > 0 and self.packages > 0:
                    self.products += 1
                    worker_at_location.products -= 1
                    self.packages -= 1
                    worker_at_location.packages += 1
                    worker_at_location.destination = self.warehouse.cargo_bay.pos
                    if self.workers_needed > 0: self.workers_needed -= 1

                else:
                    worker_at_location.destination = None

    def package_product(self):
        if self.products > 0:
            self.products -= 1
            self.packages += 1
            self.workers_needed += 1
