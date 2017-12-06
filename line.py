# -*- coding: utf-8 -*-

import random
import logging

LOGGER = logging.getLogger("line")


# Esta classe implementa uma fila FCFS
class Line:

    def __init__(self, flags, last_line=False):
        self.items = []
        self.last = last_line
        self.id = random.randint(0, 1000)

        LOGGER.info("Line {} being created".format(self.id))

        # Apenas a fila 2 gerenciará o arquivo de medidas de tempo
        if self.last:
            with open("service_measures_{}.csv".format(flags["round"]), "w") as f:
                f.write('"T1","W1","T2","W2"\n')

    @property
    def size(self):
        return len(self.items)

    # Retorna o próximo serviço da fila (sem retirar)
    def next(self):
        if self.items:
            LOGGER.info("Next service have been requested to line {}".format(self.id))
            return self.items[0]

    # Adiciona serviço à fila
    def add(self, service):
        self.items.append(service)
        LOGGER.info("Service added to line {}".format(self.id))

    def empty(self):
        return not self.items

    # Remove o serviço da fila
    def remove_service(self, flags):
        service = self.items.pop(0)
        service.finished = False
        LOGGER.info("Service removed from line {}".format(self.id))

        # quando for retirado da fila 2, imprime todas as métricas calculadas
        # no arquivo de medidas de tempo
        if self.last:
            with open("service_measures_{}.csv".format(flags["round"]), "a") as f:
                f.write("{},{},{},{}\n".format(
                    service.t_line1.spent() + service.t_server1.spent(),
                    service.t_line1.spent(),
                    service.t_line2.spent() + service.t_server2.spent(),
                    service.t_line2.spent()
                ))


