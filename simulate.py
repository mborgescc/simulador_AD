# -*- coding: utf-8 -*-
import argparse
from simulator import Simulator

parser = argparse.ArgumentParser(description="Roda um simulador MG1 com duas filas FCFS e um servidor")
parser.add_argument("-u", "--use", type=float, help="Define uma taxa para o processo de chegada de fregueses")
parser.add_argument("-e", "--events", default=100, type=int, help="Define o número de fregueses a serem servidos antes de terminar o simulador")
parser.add_argument("-r", "--rounds", default=1, type=int, help="Define o número de vezes que o simulador será executado")
parser.add_argument(
    "-s",
    "--seed", 
    default=None, 
    type=float, 
    help="Define a semente para o gerador de números aleatórios que alimenta as chegadas de fregueses e o tempo de serviço"
)

args = parser.parse_args()

simulations = []
for i in range(args.rounds)
    simulator = Simulator(
        args.use,
        args.events,
        args.seed
    )
    simulations.append(simulator)
    simulator.start()

# Calcular intervalo de confiança

