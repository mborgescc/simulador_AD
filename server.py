# -*- coding: utf-8 -*-
import logging
from threading import Thread
from time import sleep

LOGGER = logging.getLogger("server")


# Classe responsável por implementar o servidor
class Server:

    def __init__(self):
        self.running = False
        self.serving = None
        self.l1_on_server = 0
        self.l2_on_server = 0

    # Método para processar os serviços (basicamente manda rodá-los até
    # o próprio servidor pedir para o processo sair, o serviço terminar ou o
    # simulador parar) - Roda em paralelo ao servidor para os serviços da fila 2
    def serve(self, service, flags, line):
        LOGGER.info(">> Serving {}".format(service.label))
        while not flags["save_service"] and not service.finished and not flags["stop"]:
            service.walk(line)
        if service.finished:
            LOGGER.info(">> {} finished".format(service.label))
        else:
            LOGGER.info(">> {} leaving without finishing".format(service.label))

    # Método responsável por gerar o arquivo com as medidas de tamanho de fila
    def capture_measures(self, flags, line1, line2):
        with open("line_measures.csv", "w") as f:
            f.write('"N1","Nq1","N2","Nq2"\n')

            while not flags["stop"]:
                sleep(0.01)
                f.write("{},{},{},{}\n".format(
                    line1.size,
                    line1.size - self.l1_on_server,
                    line2.size,
                    line2.size - self.l2_on_server
                ))

    # Método que implementa o processamento do servidor
    def start(self, flags, line1, line2):
        flags["line2"] = False
        capt = Thread(target=self.capture_measures, args=(flags, line1, line2), name="capture_server_measures")
        capt.start()

        while not flags["stop"]:  # Enquanto o simulador não finalizar,

            print(flags)
            if line1.empty():  # Se a fila 1 estiver vazia,

                if not line2.empty() and not self.running:  # Caso a fila 2 tenha alguém e o
                                                            # servidor não está servindo ninguém
                    LOGGER.info("Line 1 is empty... Requesting service from line 2")
                    flags["line2"] = True
                    flags["save_service"] = False
                    self.running = True
                    service = line2.next()  # Então sirva o próximo serviço da fila 2
                    service.t_line2.stop()
                    self.serving = Thread(
                        target=self.serve, args=(service, flags, 2), name="{}_serving".format(service.label)
                    )
                    service.t_server2.start()
                    self.l2_on_server = 1
                    self.serving.start()

                elif not line2.empty() and not self.serving.isAlive():  # Caso a fila 2 tenha alguém,
                                                                        # mas apesar de o servidor estar
                                                                        # rodando (de acordo com a flag),
                                                                        # a thread já terminou

                    if service.finished:  # Se o serviço tiver terminado
                        self.l2_on_server = 0
                        line2.remove_service()  # Remove da fila 2
                        service.t_server2.stop(final=True)
                        flags["served"] += 1  # Incrementa o número de fregueses servidos
                        flags["services_num"] -= 1
                    else:
                        LOGGER.info(">> Removing service from server without finishing")
                        service.t_server2.stop()
                        self.l2_on_server = 0
                        service.t_line2.start()

                    self.running = False
                    flags["line2"] = False

            # Se a fila 1 não estiver vazia
            elif flags["line2"]:  # Caso haja alguém da fila 2 no servidor
                flags["save_service"] = True  # Salva o serviço e
                self.serving.join()  # retira ele do servidor
                if service.finished:  # Se o serviço tiver terminado
                    LOGGER.info("{} finished".format(service.label))
                    self.l2_on_server = 0
                    line2.remove_service()  # Remove da fila 2
                    service.t_server2.stop(final=True)
                    flags["served"] += 1  # Incrementa o número de fregueses servidos
                    flags["services_num"] -= 1
                else:
                    LOGGER.info(">> Removing service from server without finishing")
                    self.l2_on_server = 0
                    service.t_server2.stop()
                    service.t_line2.start()
                self.running = False
                flags["line2"] = False
            else:  # Após o servidor ser liberado
                LOGGER.info("Requesting service from line 1")
                flags["save_service"] = False
                service = line1.next()  # Sirva o próximo serviço da fila 1
                service.t_line1.stop(final=True)
                self.running = True
                service.t_server1.start()
                self.l1_on_server = 1
                self.serve(service, flags, 1)
                self.l1_on_server = 0
                service.t_server1.stop(final=True)
                self.running = False
                line1.remove_service()
                LOGGER.info("Removing service from server")
                line2.add(service)
                service.t_line2.start()

        # Finalizando servidor
        capt.join()
        if self.serving:
            if self.serving.isAlive():
                self.serving.join()
        LOGGER.info("Server finished")
