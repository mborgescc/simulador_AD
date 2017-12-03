# -*- coding: utf-8 -*-

from threading import Thread
from log import get_client
from time import sleep

LOGGER = get_client("server")


class Server:

    def __init__(self):
        self.running = False
        self.serving = None

    def serve(self, service, flags, line):
        LOGGER.info(">> Serving {}".format(service.label))
        while not flags["save_service"] and not service.finished and not flags["stop"]:
            service.walk(line)
        if service.finished:
            LOGGER.info(">> {} finished".format(service.label))
        else:
            LOGGER.info(">> {} leaving without finishing".format(service.label))

    def capture_measures(self, flags, line1, line2):
        with open("line_measures.csv", "w") as f:
            f.write('"N1","Nq1","N2","Nq2"\n')

            while not flags["stop"]:
                if self.running:
                    if flags["line2"]:
                        s1 = 0
                        s2 = 1
                    else:
                        s1 = 1
                        s2 = 0
                else:
                    s1 = 0
                    s2 = 0

                sleep(0.01)
                f.write("{},{},{},{}\n".format(
                    line1.size,
                    line1.size - s1,
                    line2.size,
                    line2.size - s2
                ))

    def start(self, flags, line1, line2):
        flags["line2"] = False
        capt = Thread(target=self.capture_measures, args=(flags, line1, line2), name="capture_server_measures")
        capt.start()
        while not flags["stop"]:
            print(flags)
            if line1.empty():
                if not line2.empty() and not self.running:
                    LOGGER.info("Line 1 is empty... Requesting service from line 2")
                    flags["line2"] = True
                    flags["save_service"] = False
                    self.running = True
                    next_service = line2.next()
                    next_service.t_line2.stop()
                    self.serving = Thread(
                        target=self.serve, args=(next_service, flags, 2), name="{}_serving".format(next_service.label)
                    )
                    next_service.t_server2.start()
                    self.serving.start()
                elif not line2.empty():
                    if not self.serving.isAlive():
                        if next_service.finished:
                            LOGGER.info("{} finished".format(next_service.label))
                            line2.remove_service()
                            next_service.t_server2.stop(final=True)
                            flags["services_num"] -= 1
                        else:
                            next_service.t_server2.stop()
                            next_service.t_line2.start()
                        flags["line2"] = False

            elif flags["line2"]:
                flags["save_service"] = True
                self.serving.join()
                LOGGER.info("Removing service from server")
                if next_service.finished:
                    LOGGER.info("{} finished".format(next_service.label))
                    line2.remove_service()
                    next_service.t_server2.stop(final=True)
                    flags["services_num"] -= 1
                else:
                    next_service.t_server2.stop()
                    next_service.t_line2.start()
                flags["line2"] = False
            else:
                LOGGER.info("Requesting service from line 1")
                flags["save_service"] = False
                next_service = line1.next()
                next_service.t_line1.stop(final=True)
                self.running = True
                next_service.t_server1.start()
                self.serve(next_service, flags, 1)
                next_service.t_server1.stop(final=True)
                self.running = False
                line1.remove_service()
                LOGGER.info("Removing service from server")
                line2.add(next_service)
                next_service.t_line2.start()
        capt.join()
        if self.serving:
            if self.serving.isAlive():
                self.serving.join()
        LOGGER.info("Server finished")
