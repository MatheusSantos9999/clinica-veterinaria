"""Ponto de entrada principal (main) do projeto Clinica Veterinaria."""

import sys

from clinica.demonstracao.executor_demo import ExecutorDemo
from clinica.simulacao.simulador_atendimento import SimuladorAtendimento
from interface.menus.principal.menu_principal import MenuPrincipal


def executar_aplicacao(argumentos):
    """Inicializa modo demo, simulacao direta ou menu interativo.

    Args:
        argumentos: Sequencia de argumentos da linha de comando.
    """
    # Aceita '--demo' (teste completo), '--simulacao' ou menu interativo
    if _contem_flag(argumentos, "--demo"):
        ExecutorDemo().executar()
        return
    if _contem_flag(argumentos, "--simulacao"):
        SimuladorAtendimento().executar()
        return
    MenuPrincipal().executar()


def _contem_flag(argumentos, alvo):
    """Verifica se determinada flag foi informada na linha de comando.

    Args:
        argumentos: Sequencia de argumentos recebidos.
        alvo: Flag procurada (ex: '--demo').

    Returns:
        bool: True se a flag estiver presente.
    """
    for arg in argumentos:
        if arg == alvo:
            return True
    return False


if __name__ == "__main__":
    executar_aplicacao(sys.argv)
