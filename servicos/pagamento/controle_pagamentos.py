"""Modulo de servico para controle de pagamentos realizados na clinica."""

from estruturas.lista.lista_encadeada import ListaEncadeada
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento
from modelos.pagamento.pagamento.pagamento import Pagamento


class ControlePagamentos:
    """Gerencia o historico de pagamentos efetuados no fechamento.

    Attributes:
        pagamentos: ListaEncadeada contendo todos os pagamentos registrados.
    """

    def __init__(self):
        """Inicializa a lista encadeada de pagamentos vazia."""
        self.pagamentos = ListaEncadeada()

    def registrar_pagamento(
        self, prontuario, dados_pagamento, valor_meds, valor_procs
    ):
        """Valida e registra o pagamento unico de um prontuario.

        Args:
            prontuario: Prontuario sendo fechado.
            dados_pagamento: Instancia validada de DadosPagamento.
            valor_meds: Valor final dos medicamentos baixados.
            valor_procs: Valor final dos procedimentos realizados.

        Returns:
            Pagamento: Registro de pagamento armazenado.

        Raises:
            TypeError: Se dados_pagamento nao for DadosPagamento.
            ValueError: Se o prontuario ja possuir pagamento registrado.
        """
        # Bloqueia cobranca duplicada para o mesmo prontuario
        self._validar_entrada(prontuario.numero, dados_pagamento)
        pagamento = Pagamento(
            prontuario, dados_pagamento, valor_meds, valor_procs
        )
        self.pagamentos.adicionar(pagamento)
        return pagamento

    def _validar_entrada(self, numero_prontuario, dados_pagamento):
        """Garante tipo valido e ausencia de pagamento anterior.

        Args:
            numero_prontuario: Numero do prontuario alvo.
            dados_pagamento: Objeto de entrada do pagamento.

        Raises:
            TypeError: Se o tipo de dados_pagamento for incorreto.
            ValueError: Se ja existir pagamento para este prontuario.
        """
        if not isinstance(dados_pagamento, DadosPagamento):
            raise TypeError("dados_pagamento deve ser DadosPagamento.")
        if self.buscar_por_prontuario(numero_prontuario) is not None:
            raise ValueError("Prontuario ja possui pagamento registrado.")

    def buscar_por_prontuario(self, numero_prontuario):
        """Localiza o pagamento associado a um numero de prontuario.

        Args:
            numero_prontuario: Numero identificador do prontuario.

        Returns:
            Pagamento: Pagamento encontrado ou None.
        """
        return self.pagamentos.buscar(
            lambda pag: pag.numero_prontuario == numero_prontuario
        )

    def calcular_total_recebido(self):
        """Soma o valor total de todos os pagamentos registrados.

        Returns:
            float: Faturamento acumulado da clinica.
        """
        total = 0.0
        for pagamento in self.pagamentos:
            total += pagamento.valor_total
        return round(total, 2)
