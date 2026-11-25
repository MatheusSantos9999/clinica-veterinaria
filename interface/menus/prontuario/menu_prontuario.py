"""Modulo de menu interativo para prontuario, diagnostico e fechamento."""

from interface.entrada.leitor_console import (
    ler_float,
    ler_inteiro,
    ler_texto,
)
from interface.exibicao.formatador_saida import (
    imprimir_erro,
    imprimir_lista,
    imprimir_sucesso,
    imprimir_titulo,
)
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento


class MenuProntuario:
    """Interface de console para diagnostico, prescricoes, alta e pagamento."""

    def __init__(self, clinica):
        """Inicializa o submenu com referencia a fachada da clinica.

        Args:
            clinica: Instancia de ClinicaVeterinaria.
        """
        self._clinica = clinica

    def executar(self):
        """Executa o laco do submenu de prontuario ate voltar."""
        while True:
            self._exibir_opcoes()
            opcao = ler_texto("Opcao: ")
            if opcao == "0":
                return
            self._processar_opcao(opcao)

    def _exibir_opcoes(self):
        """Imprime as operacoes clinicas, diagnosticas e financeiras."""
        imprimir_titulo("PRONTUARIO, DIAGNOSTICO E PAGAMENTO")
        print("1 - Ver prontuarios | 2 - Exibir arvore diagnostico")
        print("3 - Marcar Alterado | 4 - Add medicamento | 5 - Rem med")
        print("6 - Add procedimento| 7 - Rem procedim.   | 8 - Desfazer")
        print("9 - Conceder alta   | 10 - Fechar e pagar | 11 - Consumo")
        print("0 - Voltar")

    def _processar_opcao(self, opcao):
        """Trata erros de entrada e regras de negocio durante execucao.

        Args:
            opcao: Opcao selecionada pelo usuario.
        """
        try:
            self._despachar_grupo_1(opcao)
        except (ValueError, TypeError) as erro:
            imprimir_erro(erro)

    def _despachar_grupo_1(self, opcao):
        """Despacha opcoes 1 a 3 ou encaminha para o grupo 2.

        Args:
            opcao: Codigo da acao escolhida.
        """
        if opcao == "1":
            self._listar_prontuarios()
        elif opcao == "2":
            self._exibir_arvore()
        elif opcao == "3":
            self._marcar_alterado()
        else:
            self._despachar_grupo_2(opcao)

    def _despachar_grupo_2(self, opcao):
        """Despacha opcoes 4 a 6 ou encaminha para o grupo 3.

        Args:
            opcao: Codigo da acao escolhida.
        """
        if opcao == "4":
            self._adicionar_medicamento()
        elif opcao == "5":
            self._remover_medicamento()
        elif opcao == "6":
            self._adicionar_procedimento()
        else:
            self._despachar_grupo_3(opcao)

    def _despachar_grupo_3(self, opcao):
        """Despacha opcoes 7 a 9 ou encaminha para o grupo 4.

        Args:
            opcao: Codigo da acao escolhida.
        """
        if opcao == "7":
            self._remover_procedimento()
        elif opcao == "8":
            self._desfazer_acao()
        elif opcao == "9":
            self._dar_alta()
        else:
            self._despachar_grupo_4(opcao)

    def _despachar_grupo_4(self, opcao):
        """Despacha opcoes 10 e 11 ou informa opcao invalida.

        Args:
            opcao: Codigo da acao escolhida.
        """
        if opcao == "10":
            self._fechar_e_pagar()
        elif opcao == "11":
            self._ver_pagamentos_e_consumo()
        else:
            imprimir_erro("Opcao invalida.")

    def _listar_prontuarios(self):
        """Mostra prontuarios abertos e historico empilhado de fechados."""
        print("\nProntuarios abertos:")
        imprimir_lista(self._clinica.prontuarios.prontuarios_abertos)
        print("\nProntuarios fechados (mais recente primeiro):")
        imprimir_lista(self._clinica.prontuarios.prontuarios_fechados)

    def _exibir_arvore(self):
        """Exibe a arvore de sistemas em pre-ordem para um prontuario."""
        num = ler_inteiro("Numero do prontuario: ")
        pront = self._clinica.prontuarios.buscar_por_numero(num)
        if pront is None:
            imprimir_erro("Prontuario nao encontrado.")
            return
        print(self._clinica.diagnostico.gerar_arvore_indentada(
            pront.arvore_diagnostico
        ))

    def _marcar_alterado(self):
        """Marca um no da arvore do prontuario aberto como Alterado."""
        num = ler_inteiro("Numero do prontuario: ")
        alvo = ler_texto("Codigo ou nome da estrutura: ")
        item = self._clinica.marcar_diagnostico_alterado(num, alvo)
        imprimir_sucesso(f"Marcado: {item}")

    def _adicionar_medicamento(self):
        """Adiciona medicamento prescrito validando saldo em estoque."""
        num = ler_inteiro("Numero do prontuario: ")
        cod = ler_texto("Codigo do produto: ")
        qtd = ler_inteiro("Quantidade: ")
        item = self._clinica.adicionar_medicamento_prontuario(num, cod, qtd)
        imprimir_sucesso(f"Prescrito: {item}")

    def _remover_medicamento(self):
        """Remove medicamento do prontuario antes do fechamento."""
        num = ler_inteiro("Numero do prontuario: ")
        cod = ler_texto("Codigo do produto a remover: ")
        rem = self._clinica.prontuarios.remover_medicamento(num, cod)
        imprimir_sucesso(f"Removido: {rem}")

    def _adicionar_procedimento(self):
        """Inclui um procedimento clinico no prontuario aberto."""
        num = ler_inteiro("Numero do prontuario: ")
        nome = ler_texto("Nome do procedimento: ")
        valor = ler_float("Valor (R$): ")
        desc = ler_texto("Descricao (opcional): ")
        proc = self._clinica.adicionar_procedimento_prontuario(
            num, nome, valor, desc
        )
        imprimir_sucesso(f"Incluido: {proc}")

    def _remover_procedimento(self):
        """Remove um procedimento nao autorizado antes do fechamento."""
        num = ler_inteiro("Numero do prontuario: ")
        nome = ler_texto("Nome do procedimento a remover: ")
        rem = self._clinica.prontuarios.remover_procedimento(num, nome)
        imprimir_sucesso(f"Removido: {rem}")

    def _desfazer_acao(self):
        """Reverte a ultima acao registrada na pilha do prontuario."""
        num = ler_inteiro("Numero do prontuario: ")
        acao = self._clinica.prontuarios.desfazer_ultima_acao(num)
        if acao is None:
            print("Nenhuma acao disponivel para desfazer.")
            return
        imprimir_sucesso(f"Acao desfeita: {acao}")

    def _dar_alta(self):
        """Registra a alta do animal no prontuario selecionado."""
        num = ler_inteiro("Numero do prontuario: ")
        pront = self._clinica.prontuarios.dar_alta(num)
        imprimir_sucesso(f"Alta registrada: {pront}")

    def _fechar_e_pagar(self):
        """Fecha o prontuario com alta, baixa FIFO e registra pagamento."""
        num = ler_inteiro("Numero do prontuario: ")
        pagador = ler_texto("Nome de quem pagou: ")
        forma = ler_texto(
            "Forma (PIX/DINHEIRO/CARTAO_AVISTA/CARTAO_PARCELADO): "
        )
        parcelas = ler_inteiro("Numero de parcelas (1 ou 2..12): ")
        dados = DadosPagamento(pagador, forma, parcelas)
        reg = self._clinica.fechar_atendimento(num, dados)
        imprimir_sucesso(str(reg))

    def _ver_pagamentos_e_consumo(self):
        """Mostra pagamentos, total recebido e consumo por tutor/animal."""
        print("\nPagamentos realizados:")
        imprimir_lista(self._clinica.pagamentos.pagamentos)
        total = self._clinica.pagamentos.calcular_total_recebido()
        print(f"Total recebido: R$ {total:.2f}")
        print("\nRegistros de consumo:")
        imprimir_lista(self._clinica.consumo.registros)
