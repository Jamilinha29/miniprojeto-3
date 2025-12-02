from src.atendente import Atendente
from src.servidor import Servidor


def test_servidor_inicializa_sem_atendentes():
    servidor = Servidor(id="Teste", capacidade=3)

    assert servidor.ativo
    assert servidor.atendentes == []


def test_servidor_permite_armazenar_atendentes():
    servidor = Servidor(id="Teste", capacidade=3)
    atendente = Atendente(id=1, tipo="suporte", servidor_id=servidor.id)

    servidor.atendentes.append(atendente)

    assert len(servidor.atendentes) == 1
    assert servidor.atendentes[0].tipo == "suporte"
