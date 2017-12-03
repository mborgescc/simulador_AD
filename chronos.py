# -*- coding: utf-8 -*-

from log import get_client
from datetime import datetime

_START = 0
_PAUSE = 1
_RESUME = 2
_STOP = 3


# Classe implementada para auxiliar na cronometragem dos tempos de fila e tempos de serviço
# Cada cronômetro possui uma linha do tempo onde podem ser realizados vários processos de cronometragem
class Chronometer:

    def __init__(self, label):
        self.history = []
        self._label = label
        self.started = False
        self.paused = True

    def set_label(self, label):
        self._label = label

    @property
    def label(self):
        return self._label

    # Inicia ou continua um cronômetro pausado
    def start(self):
        if not self.started:
            self.history.append((_START, datetime.now()))
            self.started = True
            self.paused = False
        else:
            if not self.paused:
                raise Exception("{} resumed without being paused.".format(self.label))
            else:
                self.paused = False
                self.history.append((_RESUME, datetime.now()))

    # Pausa ou para e reseta o cronômetro
    def stop(self, final=False):
        if not self.started:
            pass
        elif not final:
            self.paused = True
            self.history.append((_PAUSE, datetime.now()))
        else:
            self.history.append((_STOP, datetime.now()))
            self.started = False
            self.paused = True

    # Calcula o tempo cronometrado, subtraindo os tempos pausados (seja para a linha do tempo
    # completa ou apenas para a execução do último processo de cronometragem
    def spent(self, complete=False):
        if not self.history:
            return 0

        # Para o caso de usar apenas a última execução, calcula-se onde ela inicia:
        if not complete:
            for i in list(range(0, len(self.history)))[::-1]:
                if self.history[i][0] == _START:
                    spent_array = self.history[i::]
                    break
        else:
            spent_array = self.history
        time_sum = 0

        # Varre o vetor e soma todos os tempos entre algum ponto de START e de STOP
        for item in spent_array:
            if item[0] == _START or item[0] == _RESUME:
                initial = item[1]
                last_start = True
            elif last_start:
                end = item[1]
                delta = end - initial
                time_sum += delta.seconds * 1000000 + delta.microseconds
                last_start = False

        # Verifica se o cronômetro está rodando, e para esse caso soma o tempo desde o último
        # START até o tempo atual
        if spent_array[-1][0] == _START or spent_array[-1][0] == _RESUME:
            end = datetime.now()
            delta = end - initial
            time_sum += delta.seconds * 1000000 + delta.microseconds

        return time_sum

    # Simplificação do processo de LOG para o tempo gasto
    def take_note(self, action, module):
        LOGGER = get_client(module)
        LOGGER.info("{} - {} - Running for: {} Microsseconds;".format(
            self.label, action, self.spent()
        ))
