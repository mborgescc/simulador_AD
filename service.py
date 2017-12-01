import random
from log import get_client
from chronos import Chronometer

LOGGER = get_client("service")


class Service:

    def __init__(self, steps, label):
        self.t_line1 = Chronometer("Service {} - Line 1".format(label)) # Finalize
        self.t_line2 = Chronometer("Service {} - Line 2".format(label))
        self.t_server1 = Chronometer("Service {} - Server 1".format(label))
        self.t_server2 = Chronometer("Service {} - Server 2".format(label))

        self.label = "Service {}".format(label)
        self.steps = steps
        self.actual_step = 0
        if steps < 1:
            self.finished = True
        else:
            self.finished = False

        LOGGER.info("{} created".format(self.label))

    def hard_work(self):
        randomic = random.randint(1, 10000)**random.randint(1, 10)

    def walk(self):
        self.hard_work()
        self.actual_step += 1
        if self.actual_step >= self.steps:
            self.finished = True
