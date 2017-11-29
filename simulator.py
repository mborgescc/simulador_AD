from log import get_client
import msvcrt
import random
from line import Line
from server import Server
from service import Service
from threading import Thread
from datetime import datetime

LOGGER1 = get_client("simulator")
LOGGER2 = get_client("arrivals")

class Simulator:

    _HIGH = True
    _LOW = False

    def __init__(self, server_use, rounds, seed=None):
        self.running = False
        self.server_use = server_use
        self.server = Server()
        self.f_line = Line()
        self.s_line = Line()
        self.flags = {
            "stop": False,
			"services_num": 0,
        }
        self.rounds = rounds
        self.seed = seed
        self.iter = 0
        self.initial_time = datetime.now()

    def arrivals(self, rate):
        if self.seed:
            random.seed(self.seed)

        timing = datetime.now()
        LOGGER2.info("Timing: {}".format(timing))
        self.arrivals_sample = []

        while not self.flags["stop"]:
            next_sample = random.expovariate(rate)
            LOGGER2.info("Waiting: {}".format(next_sample))
            self.arrivals_sample.append(next)
            pick_it = datetime.now()
            delta = pick_it - timing
            while not delta.seconds + delta.microseconds//1000 > next_sample:
                pick_it = datetime.now()
                delta = pick_it - timing
            timing = pick_it
            LOGGER2.info("Timing: {}".format(timing))
            service = Service(random.randint(1, 100))
            self.f_line.add(service)
			self.iter += 1
			self.flags["services_num"] += 1


    @property
    def rate(self):
        return self.server_use/2

    def start(self):
        self.running = True
        LOGGER1.info("Initializing server")
        Thread(target=self.server.start, args=(self.flags, self.f_line, self.s_line))
        LOGGER1.info("Initializing arrivals")
        Thread(target=self.arrivals, args=(0.2,))
        while self.iter < self.rounds:
            if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
                self.flags["stop"] = True
        LOGGER1.info("Finished simulator")
        # Colocar joins AQUI
        self.flags["stop"] = True
		
		# PRECISAMOS CALCULAR: E[W], E[T], E[Nq], E[N], V[W] (PARA FILAS 1 E 2)

