from mesa import Agent


class CargoBay(Agent):

    def __init__(self, unique_id, warehouse, pos):
        super().__init__(unique_id, warehouse)
        self.pos = pos
        self.warehouse = warehouse
        self.packages = 0

    def step(self):
        self.dispatch()
        print("[cargo_bay] packages: {}".format(self.packages))

    def dispatch(self):
        worker_at_location = self.warehouse.free_worker_at_pos(self.pos)
        if worker_at_location:
            if worker_at_location.destination == self.pos:
                if worker_at_location.packages > 0:
                    self.packages += worker_at_location.packages
                    worker_at_location.packages = 0
                    worker_at_location.destination = None
