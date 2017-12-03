# -*- coding: utf-8 -*-

import msvcrt
import random
from log import get_client
from line import Line
from server import Server
from service import Service
from chronos import Chronometer
from threading import Thread
from datetime import datetime

LOGGER1 = get_client("simulator")
LOGGER2 = get_client("arrivals")
LOGGER3 = get_client("line")
LOGGER4 = get_client("service")
LOGGER5 = get_client("server")


class Simulator:

    _HIGH = True
    _LOW = False

    def __init__(self, server_use, rounds, seed=None):
        self.running = False
        self.server_use = server_use
        self.server = Server()
        self.f_line = Line()
        self.s_line = Line(last_line=True)
        self.flags = {
            "stop": False,
            "services_num": 0,
        }
        self.rounds = rounds
        self.seed = seed
        self.iter = 0
        LOGGER2.info("## Initializing arrivals ##")
        LOGGER3.info("## Initializing lines ##")
        LOGGER4.info("## Initializing services ##")
        LOGGER5.info("## Initializing server ##")
        LOGGER1.info("## Initializing simulator <> Server user: {} <> Seed: {} <> Rounds: {} ##".format(
            self.server_use,
            self.seed,
            self.rounds
        ))
        self.initial_time = datetime.now()

    def arrivals(self, rate):
        if self.seed:
            LOGGER2.info("Semente: {}".format(self.seed))
            random.seed(self.seed)

        arrivals_sample = []
        chron = Chronometer("Arrivals")
        while not self.flags["stop"]:
            chron.start()
            next_sample = random.expovariate(rate)
            LOGGER2.info("Waiting: {}".format(next_sample))
            arrivals_sample.append(next_sample)
            while not chron.spent()/1000000 > next_sample:
                pass
            chron.stop(final=True)
            chron.take_note("Service {} goes to line 1".format(self.iter), "arrivals".format(self.iter))
            service = Service(self.iter)
            self.f_line.add(service)
            service.t_line1.start()
            self.iter += 1
            self.flags["services_num"] += 1

    @property
    def rate(self):
        return self.server_use/2

    def start(self):
        self.running = True
        LOGGER1.info("Initializing server")
        t_server = Thread(target=self.server.start, args=(self.flags, self.f_line, self.s_line), name="server")
        LOGGER1.info("Initializing arrivals")
        t_arrivals = Thread(target=self.arrivals, args=(self.rate,), name="arrivals")

        t_server.start()
        t_arrivals.start()

        LOGGER1.info("Server and arrivals threads initialized")

        while self.iter < self.rounds:
            if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
                LOGGER1.info("Finished by ESC Key press")
                break

        self.flags["stop"] = True
        print("Aguarde a finalização do simulador...")
        t_server.join()
        t_arrivals.join()

        LOGGER1.info("Finished simulator")
		
		# PRECISAMOS CALCULAR: E[W], E[T], E[Nq], E[N], V[W] (PARA FILAS 1 E 2)

