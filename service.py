import random


class Service:

    def __init__(self, steps):
		line1_time = Chronometer() # Finalize
		line2_time = Chronometer()
		server1_time = Chronometer()
		server2_time = Chronometer()
		
        self.steps = steps
        self.actual_step = 0
        if steps < 1:
            self.finished = True
        else:
            self.finished = False

    def hard_work(self):
        randomic = random.randint(1, 10000)**random.randint(1, 10)

    def walk(self):
        self.hard_work()
        self.actual_step += 1
        if self.actual_step >= self.steps:
            self.finished = True
