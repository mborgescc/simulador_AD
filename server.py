from threading import Thread


class Server:

    def __init__(self):
        self.running = False
        self.serving = None

    def serve(self, service, flags):
        while not flags["save_service"] and not service.finished:
            service.walk()
        self.running = False

    def start(self, flags, line1, line2):
        while not flags["stop"]:
            if line1.empty():
                if not line2.empty() and not self.running:
                    flags["line2"] = True
                    flags["save_service"] = False
                    self.running = True
                    self.serving = Thread(self.serve, (line2.next(), flags))
                    self.serving.start()
            elif flags["line2"]:
                flags["save_service"] = True
                self.serving.join()
                line2.remove_service()
                flags["line2"] = False
            else:
                flags["save_service"] = False
                next_service = line1.next()
                self.serve(next_service, flags)
                line1.remove_service()
                line2.add(next_service)
