from simulacao import simular
from configuracoes import CENARIO_1, CENARIO_2
from logs import registrar

simular("CENÁRIO 1 - Estável", CENARIO_1, registrar)
simular("CENÁRIO 2 - Crítico", CENARIO_2, registrar)