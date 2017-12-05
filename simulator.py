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


# Classe responsável pelo simulador como um todo
class Simulator:

    def __init__(self, server_use, rounds, seed=None):
        self.running = False
        self.server_use = server_use
        self.server = Server()  # Servidor
        self.f_line = Line()  # Fila 1
        self.s_line = Line(last_line=True)  # Fila 2
        self.flags = {  # Dicionário usado para comunicação entre threads
            "stop": False,
            "services_num": 0,
            "served": 0,
        }
        self.rounds = rounds
        self.seed = seed
        self.iter = 0

        # Inicializando clientes de LOG
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

    # Método gerador de fregueses (roda em thread separada)
    def arrivals(self, rate):
        if self.seed:
            LOGGER2.info("Semente: {}".format(self.seed))
            random.seed(self.seed)

        arrivals_sample = []
        chron = Chronometer("Arrivals")
        while not self.flags["stop"]:  # Enquanto o simulador não parar
            chron.start()  # Inicia o temporizador
            next_sample = random.expovariate(rate)  # Gera um número com distribuição exponencial e taxa dada
            LOGGER2.info("Waiting: {}".format(next_sample))
            arrivals_sample.append(next_sample)
            while not chron.spent()/1000000 > next_sample:  # Enquanto o temporizador for menor que o número
                pass  # Continua em loop
            chron.stop(final=True)  # Ao terminar, reseta o temporizador,
            chron.take_note("Service {} goes to line 1".format(self.iter), "arrivals".format(self.iter))
            service = Service(self.iter)  # Cria um serviço
            self.f_line.add(service)  # e o adiciona na fila 1
            service.t_line1.start()
            self.iter += 1
            self.flags["services_num"] += 1

    @property
    def rate(self):  # Taxa = uso do servidor/2
        return self.server_use/2

    # Inicia o simulador
    def start(self):
        self.running = True

        # Gera as threads de servidor e de chegadas de fregueses
        LOGGER1.info("Initializing server")
        t_server = Thread(target=self.server.start, args=(self.flags, self.f_line, self.s_line), name="server")
        LOGGER1.info("Initializing arrivals")
        t_arrivals = Thread(target=self.arrivals, args=(self.rate,), name="arrivals")
        t_server.start()
        t_arrivals.start()

        LOGGER1.info("Server and arrivals threads initialized")

        while self.flags["served"] < self.rounds:   # Enquanto o número de fregueses servidos for menor
                                                    # que o número de rodadas definido
            if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:  # A menos que se pressione ESC
                LOGGER1.info("Finished by ESC Key press")
                break
            # Continua em loop

        self.flags["stop"] = True  # Ao terminar, manda um sinal para todas as threads finalizarem
        print("Aguarde a finalização do simulador...")
        t_server.join()
        t_arrivals.join()

        LOGGER1.info("Finished simulator")

        # É hora de calcular: E[W], E[T], E[Nq], E[N], V[W] (PARA FILAS 1 E 2)



