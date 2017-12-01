from log import get_client
from datetime import datetime

_START = 0
_PAUSE = 1
_RESUME = 2
_STOP = 3


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

    def stop(self, final=False):
        if not self.started:
            raise Exception("{} stopped without starting.".format(self.label))
        elif not final:
            self.paused=True
            self.history.append((_PAUSE, datetime.now()))
        else:
            self.history.append((_STOP, datetime.now()))
            self.started = False
            self.paused = True

    def spent(self, complete=False):
        if not self.history:
            return 0

        if not complete:
            for i in list(range(0, len(self.history)))[::-1]:
                if self.history[i][0] == _START:
                    spent_array = self.history[i::]
                    break
        else:
            spent_array = self.history
        time_sum = 0
        for item in spent_array:
            if item[0] == _START or item[0] == _RESUME:
                initial = item[1]
                last_start = True
            elif last_start:
                end = item[1]
                delta = end - initial
                time_sum += delta.seconds * 1000000 + delta.microseconds
                last_start = False
        if spent_array[-1][0] == _START or spent_array[-1][0] == _RESUME:
            end = datetime.now()
            delta = end - initial
            time_sum += delta.seconds * 1000000 + delta.microseconds

        return time_sum

    def take_note(self, action, module):
        LOGGER = get_client(module)
        LOGGER.info("{} - {} - Running for: {} Microsseconds;".format(
            self.label, action, self.spent()
        ))
