# -*- coding: utf-8 -*-
import numpy
import random
from log import get_client
from chronos import Chronometer

# Definindo cliente de LOG
LOGGER = get_client("service")


# Esta classe implementa o freguês por meio de um serviço preparado para rodar duas vezes
# com tempos de serviço independentes
class Service:

    def __init__(self, label):
        # Inicializando cronômetros para temporização de tempo em filas e nas 2 vezes que passa no servidor
        self.t_line1 = Chronometer("Service {} - Line 1".format(label))
        self.t_line2 = Chronometer("Service {} - Line 2".format(label))
        self.t_server1 = Chronometer("Service {} - Server 1".format(label))
        self.t_server2 = Chronometer("Service {} - Server 2".format(label))

        # Inicializando nome para LOG
        self.label = "Service {}".format(label)

        # Definindo tempos de serviço
        self.t_service1 = random.expovariate(1)
        self.t_service2 = random.expovariate(1)

        # Flag
        self.finished = False

        LOGGER.info("{} being created <> Service time 1: {} <> Service time 2: {}".format(
            self.label,
            self.t_service1,
            self.t_service2
        ))

    # Método que será chamado um número indefinido de vezes, até que o tempo de serviço seja
    # esgotado ou (no caso do serviço estar sendo servido pela segunda vez) chegue um freguês
    # na fila 1
    def walk(self, line):
        if line == 1:
            serving = self.t_server1
            timing = self.t_service1
        else:
            serving = self.t_server2
            timing = self.t_service2

        LOGGER.info("{} is walking".format(self.label))
        if serving.spent() >= timing:
            self.finished = True
