# -*- coding: utf-8 -*-

import random
from log import get_client

LOGGER = get_client("line")


class Line:

    def __init__(self, last_line=False):
        self.items = []
        self.last = last_line
        self.id = random.randint(0, 1000)

        LOGGER.info("Line {} being created".format(self.id))
        if self.last:
            with open("service_measures.csv", "w") as f:
                f.write('"T1","W1","T2","W2"\n')

    @property
    def size(self):
        return len(self.items)

    def next(self):
        if self.items:
            LOGGER.info("Next service have been requested to line {}".format(self.id))
            return self.items[0]

    def add(self, service):
        self.items.append(service)
        LOGGER.info("Service added to line {}".format(self.id))

    def empty(self):
        return not self.items

    def remove_service(self):
        service = self.items.pop(0)
        service.finished = False
        LOGGER.info("Service removed from line {}".format(self.id))
        if self.last:
            with open("service_measures.csv", "a") as f:
                f.write("{},{},{},{}\n".format(
                    service.t_line1.spent() + service.t_server1.spent(),
                    service.t_line1.spent(),
                    service.t_line2.spent() + service.t_server2.spent(),
                    service.t_line2.spent()
                ))


