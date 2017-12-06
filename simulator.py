# -*- coding: utf-8 -*-
import numpy as np
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

    def __init__(self, server_use, rounds, round, seed=None):
        self.running = False
        self.server_use = server_use
        self.server = Server()  # Servidor
        self.measures = {}
        self.flags = {  # Dicionário usado para comunicação entre threads
            "stop": False,
            "services_num": 0,
            "served": 0,
			"round": round
        }
        self.f_line = Line(flags)  # Fila 1
        self.s_line = Line(flags, last_line=True)  # Fila 2
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

    def mean(self, values):
        sum = 0
        for item in values:
            sum += item
        if len(values) == 0:
            return 0
        return sum/len(values)

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
        # print("Aguarde a finalização do simulador...")
        t_server.join()
        t_arrivals.join()

        LOGGER1.info("Finished simulator")

        # É hora de calcular: E[W], E[T], E[Nq], E[N], V[W] (PARA FILAS 1 E 2)
		self.take_off_transient()
        self.calculate_measures()
		
    def calculate_measures(self):
		self.measures["E[W1]"] = np.mean(self.measures["W1"])
        self.measures["E[T1]"] = np.mean(self.measures["T1"])
        self.measures["E[N1]"] = np.mean(self.measures["N1"])
        self.measures["E[Nq1]"] = np.mean(self.measures["Nq1"])
        self.measures["V[W1]"] = np.var(self.measures["W1"])
        self.measures["E[W2]"] = np.mean(self.measures["W2"])
        self.measures["E[T2]"] = np.mean(self.measures["T2"])
        self.measures["E[N2]"] = np.mean(self.measures["N2"])
        self.measures["E[Nq2]"] = np.mean(self.measures["Nq2"])
        self.measures["V[W2]"] = np.var(self.measures["W2"])

        print(
            "Simulador {}:\n"
            "- Fila 1:\n    >> E[W] = {}\n    >> E[T] = {}\n    >> E[N] = {}\n    >> E[Nq] = {}\n    >> Var[W] = {}\n\n"
            "- Fila 2:\n    >> E[W] = {}\n    >> E[T] = {}\n    >> E[N] = {}\n    >> E[Nq] = {}\n    >> Var[W] = {}\n".format(
                self.flags["round"]
                self.measures["E[W1]"],
                self.measures["E[T1]"],
                self.measures["E[N1]"],
                self.measures["E[Nq1]"],
                self.measures["V[W1]"],
                self.measures["E[W2]"],
                self.measures["E[T2]"],
                self.measures["E[N2]"],
                self.measures["E[Nq2]"],
                self.measures["V[W2]"]
            )
        )

    def take_off_transient(self):
        self.measures = {
            "W1": [],
            "W2": [],
            "T1": [],
            "T2": [],
            "Nq1": [],
            "Nq2": [],
            "N1": [],
            "N2": [],
        }

        with open("line_measures.csv", "r") as f:
            f.readline()
            for line in f:
                splitted = line.split(",")
                self.measures["N1"].append(int(splitted[0]))
                self.measures["Nq1"].append(int(splitted[1]))
                self.measures["N2"].append(int(splitted[2]))
                self.measures["Nq2"].append(int(splitted[3]))
				
        with open("service_measures.csv", "r") as f:
            f.readline()
            for line in f:
                splitted = line.split(",")
                self.measures["T1"].append(int(splitted[0])/1000000)
                self.measures["W1"].append(int(splitted[1])/1000000)
                self.measures["T2"].append(int(splitted[2])/1000000)
                self.measures["W2"].append(int(splitted[3])/1000000)

		# Calcular fase transiente

