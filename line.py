from datetime import datetime


class Line:

    def __init__(self):
        self.items = []

    def next(self):
        if self.items:
            return self.items[0]

    def add(self, service):
        self.items.append(service)
		service.initial = datetime.now()

    def empty(self):
        return not self.items

    def remove_service(self):
        self.items.pop(0)