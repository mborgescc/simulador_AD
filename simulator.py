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
from scipy import optimize as opt
from matplotlib import pyplot as plt

LOGGER1 = get_client("simulator")
LOGGER2 = get_client("arrivals")
LOGGER3 = get_client("line")
LOGGER4 = get_client("service")
LOGGER5 = get_client("server")


# Classe responsável pelo simulador como um todo
class Simulator:

    def __init__(self, server_use, rounds, round_number, epsilon, window, seed=None):
        self.epsilon = epsilon
        self.window = window
        self.running = False
        self.server_use = server_use
        self.server = Server()  # Servidor
        self.measures = {}
        self.flags = {  # Dicionário usado para comunicação entre threads
            "stop": False,
            "services_num": 0,
            "served": 0,
            "round": round_number
        }
        self.f_line = Line(self.flags)  # Fila 1
        self.s_line = Line(self.flags, last_line=True)  # Fila 2
        self.rounds = rounds
        self.seed = seed
        self.iter = 0
        self.finished_by_key = False

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
        self.initial_time = None

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
        self.initial_time = datetime.now()
        t_server.start()
        t_arrivals.start()

        LOGGER1.info("Server and arrivals threads initialized")

        while self.flags["served"] < self.rounds:   # Enquanto o número de fregueses servidos for menor
                                                    # que o número de rodadas definido
            if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:  # A menos que se pressione ESC
                LOGGER1.info("Finished by ESC Key press")
                print("Terminando o simulador...")
                self.finished_by_key = True
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

        if self.finished_by_key:
            return False
        return True

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
            "- Fila 1:\n    >> E[W] = {}\n    >> E[T] = {}\n    >> E[N] = {}\n"
            "    >> E[Nq] = {}\n    >> Var[W] = {}\n\n"
            "- Fila 2:\n    >> E[W] = {}\n    >> E[T] = {}\n    >> E[N] = {}\n"
            "    >> E[Nq] = {}\n    >> Var[W] = {}\n\n".format(
                self.flags["round"],
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
        measures = {
            "W1": [],
            "W2": [],
            "T1": [],
            "T2": [],
            "Nq1": [],
            "Nq2": [],
            "N1": [],
            "N2": []
        }

        line_timestamps = []
        service_timestamps = []
        with open("line_measures_{}.csv".format(self.flags["round"]), "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                splitted = line.split(",")
                line_timestamps.append(splitted[0])
                measures["N1"].append(int(splitted[1]))
                measures["Nq1"].append(int(splitted[2]))
                measures["N2"].append(int(splitted[3]))
                measures["Nq2"].append(int(splitted[4]))

        with open("service_measures_{}.csv".format(self.flags["round"]), "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                splitted = line.split(",")
                service_timestamps.append(splitted[0])
                measures["T1"].append(int(splitted[1])/1000000)
                measures["W1"].append(int(splitted[2])/1000000)
                measures["T2"].append(int(splitted[3])/1000000)
                measures["W2"].append(int(splitted[4])/1000000)

        finishes = self.get_time_transient_finishes(line_timestamps, measures)

        for i in range(len(service_timestamps)):
            if service_timestamps[i] > finishes:
                self.measures["W1"] = measures["W1"][i:]
                self.measures["W2"] = measures["W2"][i:]
                self.measures["T1"] = measures["T1"][i:]
                self.measures["T2"] = measures["T2"][i:]
                break

        for i in range(len(line_timestamps)):
            if line_timestamps[i] > finishes:
                self.measures["N1"] = measures["N1"][i:]
                self.measures["N2"] = measures["N2"][i:]
                self.measures["Nq1"] = measures["Nq1"][i:]
                self.measures["Nq2"] = measures["Nq2"][i:]
                break

    def get_time_transient_finishes(self, line_t, measures):

        sum = 0
        initial_t = line_t[0]
        acc_values = []
        timestamps = []
        for i in range(1, len(measures["N1"])):
            services_on_system = measures["N1"][i] + measures["N2"][i]
            passed_time = self.time_passed(line_t[i-1], line_t[i])
            sum += services_on_system * passed_time
            acc_values.append(sum)

            timestamps.append(self.time_passed(initial_t, line_t[i]))

        acc = [x/y for x, y in zip(acc_values, timestamps)]

        for i in range(self.window, len(acc)):
            var = np.var(np.array(acc[i-self.window:i]))
            if var < self.epsilon:
                transient_found = i-self.window
                break

        plt.plot(timestamps, acc, 'b-')
        plt.axvline(x=timestamps[transient_found])
        plt.savefig("transient_{}.png".format(self.flags["round"]))


        """
        t_axis = np.array([self.time_passed(
            self.initial_time,
            datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        ) for time in service_t])
        m_axis = np.array([x+y for x, y in zip(measures["T1"], measures["T2"])])

        constants, matrix = opt.curve_fit(
            self.transient_function,
            t_axis,
            m_axis,
            bounds=([0.0, 1.0], [100000.0, 100000.])
        )
        plt.plot(t_axis, m_axis, 'b-', label='data')
        plt.plot(
            m_axis,
            self.transient_function(m_axis, *constants),
            'r-',
            label='fit: a=%5.3f, b=%5.3f' % tuple(constants)
        )
        plt.legend()
        plt.show()

        for i in range(1, len(service_t)):
            if m_axis[i] - m_axis[i-1] < self.epsilon:
                return service_t[i]

        for i in range(len(measures["T1"])):
            variances.append(
                np.var([x+y for x, y in zip(measures["T1"][i:], measures["T2"][i:])])
            )

        variances = variances[0:-1]
        print("Variâncias de cálculo do período transiente: {}".format(variances))

        for i in range(len(variances)-3):
            if variances[i+1] - variances[i] < self.epsilon:
                if variances[i+2] - variances[i+1] < self.epsilon:
                    if variances[i+3] - variances[i+2] < self.epsilon:
                        return service_t[i]
        """
        return line_t[transient_found+1]

    def time_passed(self, initial, final):
        delta = datetime.strptime(final, "%Y-%m-%d %H:%M:%S.%f") - \
                datetime.strptime(initial, "%Y-%m-%d %H:%M:%S.%f")
        return delta.seconds + delta.microseconds/1000000
