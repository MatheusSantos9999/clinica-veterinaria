"""Modulo do menu principal interativo da Clinica Veterinaria."""

from clinica.demonstracao.executor_demo import ExecutorDemo
from clinica.fachada.clinica_veterinaria import ClinicaVeterinaria
from clinica.simulacao.simulador_atendimento import SimuladorAtendimento
from interface.entrada.leitor_console import ler_texto
from interface.exibicao.formatador_saida import (
    imprimir_erro,
    imprimir_titulo,
)
from interface.menus.atendimento.menu_atendimento import MenuAtendimento
from interface.menus.estoque.menu_estoque import MenuEstoque
from interface.menus.prontuario.menu_prontuario import MenuProntuario
from interface.menus.tutores.menu_tutores import MenuTutores


class MenuPrincipal:
    """Coordena a navegacao entre a simulacao completa e os submenus."""

    def __init__(self, clinica=None):
        """Inicializa o menu principal e seus submenus tematicos.

        Args:
            clinica: Instancia opcional de ClinicaVeterinaria.
        """
        # Compartilha a mesma instancia da fachada entre todos os menus
        self.clinica = (
            ClinicaVeterinaria() if clinica is None else clinica
        )
        self._menu_tutores = MenuTutores(self.clinica)
        self._menu_atendimento = MenuAtendimento(self.clinica)
        self._menu_estoque = MenuEstoque(self.clinica)
        self._menu_prontuario = MenuProntuario(self.clinica)

    def executar(self):
        """Executa o laco principal do sistema ate a escolha de saida."""
        while True:
            self._exibir_opcoes()
            opcao = ler_texto("Opcao: ")
            if opcao == "0":
                print("Encerrando sistema da Clinica Veterinaria.")
                return
            self._despachar(opcao)

    def _exibir_opcoes(self):
        """Exibe o cabecalho principal com todas as modulos da clinica."""
        imprimir_titulo("SISTEMA DE CLINICA VETERINARIA - ESTRUTURA DE DADOS")
        print("1 - Executar simulacao completa de atendimento (5 passos)")
        print("2 - Controle de Tutores e Animais")
        print("3 - Controle de Atendimento e Consultorios")
        print("4 - Controle de Estoque de Medicamentos e Vacinas")
        print("5 - Prontuario, Diagnostico, Pagamento e Consumo")
        print("6 - Resumo geral | 7 - Teste automatizado | 0 - Sair")

    def _despachar(self, opcao):
        """Direciona o fluxo para a simulacao ou para o submenu escolhido.

        Args:
            opcao: Codigo informado pelo usuario.
        """
        if opcao == "1":
            SimuladorAtendimento().executar()
        elif opcao == "2":
            self._menu_tutores.executar()
        elif opcao == "3":
            self._menu_atendimento.executar()
        else:
            self._despachar_restante(opcao)

    def _despachar_restante(self, opcao):
        """Despacha opcoes 4 a 7 ou reporta opcao invalida.

        Args:
            opcao: Codigo informado pelo usuario.
        """
        if opcao == "4":
            self._menu_estoque.executar()
        elif opcao == "5":
            self._menu_prontuario.executar()
        elif opcao == "6":
            self._exibir_resumo()
        else:
            self._despachar_extra(opcao)

    def _despachar_extra(self, opcao):
        """Despacha opcao 7 (teste automatizado) ou informa erro.

        Args:
            opcao: Codigo informado pelo usuario.
        """
        if opcao == "7":
            ExecutorDemo().executar()
        else:
            imprimir_erro("Opcao invalida.")

    def _exibir_resumo(self):
        """Exibe indicadores gerais atuais da clinica em execucao."""
        cli = self.clinica
        imprimir_titulo("RESUMO GERAL DA CLINICA")
        print(f"Tutores cadastrados: {len(cli.tutores.tutores)}")
        print(f"Animais na espera:   {cli.atendimento.total_em_espera()}")
        print(f"Produtos no estoque: {len(cli.estoque.produtos)}")
        abertos = len(cli.prontuarios.prontuarios_abertos)
        total = cli.pagamentos.calcular_total_recebido()
        print(f"Prontuarios abertos: {abertos} | Recebido: R$ {total:.2f}")
