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
                    next_service = line2.next()
                    next_service.t_line2.stop()
                    self.serving = Thread(self.serve, (next_service, flags))
                    next_service.t_server2.start()
                    self.serving.start()
            elif flags["line2"]:
                flags["save_service"] = True
                self.serving.join()
                if next_service.finished:
                    line2.remove_service()
                    next_service.t_server2.stop(final=True)
                else:
                    next_service.t_server2.stop()
                    next_service.t_line2.start()
                flags["line2"] = False
            else:
                flags["save_service"] = False
                next_service = line1.next()
                next_service.t_line1.stop(final=True)
                next_service.t_server1.start()
                self.serve(next_service, flags)
                next_service.t_server1.stop(final=True)
                line1.remove_service()
                line2.add(next_service)
                next_service.t_line2.start()
