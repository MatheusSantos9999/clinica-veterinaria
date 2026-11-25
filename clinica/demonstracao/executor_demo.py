"""Modulo que executa demonstracao e teste automatizado do sistema."""

import os

from clinica.simulacao.simulador_atendimento import SimuladorAtendimento
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento
from testes.executor.rodar_testes import executar_resumo_testes


class ExecutorDemo:
    """Roda simulacao, validacoes de regras e suite de testes num comando."""

    def __init__(self, escritor=print):
        """Inicializa o executor com funcao de exibicao configuravel.

        Args:
            escritor: Funcao para imprimir a saida (padrao print).
        """
        self._escrever = escritor

    def executar(self):
        """Executa simulacao completa, checagens de regras e suite de testes.

        Returns:
            ClinicaVeterinaria: Instancia resultante da execucao.
        """
        # Roda os 5 passos, valida regras extras e dispara suite automatizada
        self._escrever("=== TESTE AUTOMATIZADO COMPLETO DO SISTEMA ===")
        clinica = SimuladorAtendimento(escritor=self._escrever).executar()
        self._verificar_regras_extras(clinica)
        self._executar_suite_final()
        return clinica

    def _verificar_regras_extras(self, clinica):
        """Demonstra busca Lista+Lista, bloqueio sem alta e ajuste manual.

        Args:
            clinica: ClinicaVeterinaria ja populada pela simulacao.
        """
        self._escrever("\n=== VERIFICACOES AUTOMATICAS DE REGRAS ===")
        self._checar_busca_e_ajuste(clinica)
        self._checar_bloqueio_sem_alta(clinica)

    def _checar_busca_e_ajuste(self, clinica):
        """Valida busca por CPF+animal e ajuste manual de inventario.

        Args:
            clinica: Instancia ativa de ClinicaVeterinaria.
        """
        pet = clinica.tutores.buscar_animal("11122233344", "Luna")
        self._escrever(f"[OK] Busca Lista+Lista (CPF+Nome): {pet}")
        lote = clinica.estoque.ajustar_quantidade("VAC01", 4, 8)
        self._escrever(f"[OK] Ajuste de inventario VAC01: {lote}")

    def _checar_bloqueio_sem_alta(self, clinica):
        """Chama proximo animal e comprova bloqueio ao fechar antes da alta.

        Args:
            clinica: Instancia ativa de ClinicaVeterinaria.
        """
        pront = clinica.chamar_proximo_atendimento("Dr. Lucas")
        self._escrever(f"[OK] Proximo chamado automaticamente: {pront}")
        self._tentar_fechar_sem_alta(clinica, pront.numero)

    def _tentar_fechar_sem_alta(self, clinica, numero):
        """Tenta fechar prontuario sem alta para exibir bloqueio da regra.

        Args:
            clinica: Fachada da clinica.
            numero: Numero do prontuario sem alta.
        """
        try:
            clinica.fechar_atendimento(numero, DadosPagamento("Ana", "PIX"))
        except ValueError as erro:
            self._escrever(f"[OK] Regra validada (bloqueio): {erro}")

    def _executar_suite_final(self):
        """Dispara todos os testes unitarios, integrados e auditoria AST."""
        # Evita recursao infinita quando chamado de dentro da propria suite
        self._escrever("\n=== SUITE DE TESTES + AUDITORIA AST ===")
        if os.environ.get("CLINICA_EM_TESTE") == "1":
            self._escrever("[OK] Execucao aninhada da suite ignorada.")
            return
        self._escrever(f"[OK] Resultado: {executar_resumo_testes()}")
