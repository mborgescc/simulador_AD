# -*- coding: utf-8 -*-
import argparse
from scipy import stats as st
from simulator import Simulator

parser = argparse.ArgumentParser(description="Roda um simulador MG1 com duas filas FCFS e um servidor")
parser.add_argument("-u", "--use", type=float, help="Define uma taxa para o processo de chegada de fregueses")
parser.add_argument("-e", "--events", default=100, type=int, help="Define o número de fregueses a serem servidos antes de terminar o simulador")
parser.add_argument("-r", "--rounds", default=1, type=int, help="Define o número de vezes que o simulador será executado")
parser.add_argument("-t", "--transienterror", default=0.00001, type=float, help="Define o epsilon (erro máximo associado ao cálculo do período transiente)")
parser.add_argument("-w", "--window", default=10000, type=int, help="Define a janela de busca pelo fim do período transiente")
parser.add_argument("-a", "--alpha", default=0.05, type=float, help="Define o alpha (para cálculo do intervalo de confiança)")
parser.add_argument(
    "-s",
    "--seed", 
    default=None, 
    type=float, 
    help="Define a semente para o gerador de números aleatórios que alimenta as chegadas de fregueses e o tempo de serviço"
)

args = parser.parse_args()

simulations = []
for i in range(args.rounds):
    simulator = Simulator(
        args.use,
        args.events,
        i,
        args.transienterror,
        args.window,
        args.seed
    )
    simulations.append(simulator)
    ret = simulator.start()
    if not ret:
        break

# Calcular intervalo de confiança


