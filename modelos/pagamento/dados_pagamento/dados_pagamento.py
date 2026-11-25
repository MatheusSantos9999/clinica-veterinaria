"""Modulo que define os dados de entrada de um pagamento."""

from utilitarios.validacao.validador_entrada import (
    validar_inteiro_positivo,
    validar_texto_obrigatorio,
)

FORMA_PIX = "PIX"
FORMA_DINHEIRO = "DINHEIRO"
FORMA_CARTAO_AVISTA = "CARTAO_AVISTA"
FORMA_CARTAO_PARCELADO = "CARTAO_PARCELADO"
MAX_PARCELAS_CARTAO = 12


class DadosPagamento:
    """Objeto de valor validado para processar o pagamento de um prontuario.

    Attributes:
        nome_pagador: Nome da pessoa que efetuou o pagamento.
        forma_pagamento: Modalidade aceita (PIX, DINHEIRO ou CARTAO_*).
        numero_parcelas: Quantidade de parcelas (1 ou 2..12 no parcelado).
    """

    def __init__(self, nome_pagador, forma_pagamento, numero_parcelas=1):
        """Valida pagador, forma de pagamento e coerencia de parcelas.

        Args:
            nome_pagador: Nome de quem realiza o pagamento.
            forma_pagamento: PIX, DINHEIRO, CARTAO_AVISTA ou CARTAO_PARCELADO.
            numero_parcelas: Numero de parcelas (padrao 1).
        """
        # Valida campos e regras de parcelamento
        self.nome_pagador = validar_texto_obrigatorio(
            nome_pagador, "Nome do pagador"
        )
        self.forma_pagamento = self._validar_forma(forma_pagamento)
        self.numero_parcelas = self._validar_parcelas(numero_parcelas)

    def _validar_forma(self, forma):
        """Normaliza e verifica se a forma de pagamento e suportada.

        Args:
            forma: Texto indicando o meio de pagamento.

        Returns:
            str: Forma normalizada em caixa alta.

        Raises:
            ValueError: Se a forma de pagamento for desconhecida.
        """
        limpa = validar_texto_obrigatorio(forma, "Forma de pagamento").upper()
        if not self._eh_forma_suportada(limpa):
            raise ValueError(f"Forma de pagamento invalida: {limpa}.")
        return limpa

    def _eh_forma_suportada(self, limpa):
        """Indica se a forma normalizada pertence as opcoes aceitas.

        Args:
            limpa: Forma em caixa alta.

        Returns:
            bool: True se suportada pela clinica.
        """
        return (
            limpa == FORMA_PIX
            or limpa == FORMA_DINHEIRO
            or limpa == FORMA_CARTAO_AVISTA
            or limpa == FORMA_CARTAO_PARCELADO
        )

    def _validar_parcelas(self, numero_parcelas):
        """Valida o numero de parcelas conforme a forma selecionada.

        Args:
            numero_parcelas: Inteiro positivo de parcelas.

        Returns:
            int: Quantidade de parcelas validada.

        Raises:
            ValueError: Se a combinacao forma/parcelas for incoerente.
        """
        # Apenas cartao parcelado admite mais de 1 parcela
        qtd = validar_inteiro_positivo(numero_parcelas, "Numero de parcelas")
        if self.forma_pagamento == FORMA_CARTAO_PARCELADO:
            return self._validar_faixa_parcelado(qtd)
        if qtd != 1:
            raise ValueError("Apenas CARTAO_PARCELADO aceita > 1 parcela.")
        return qtd

    def _validar_faixa_parcelado(self, qtd):
        """Garante que cartao parcelado tenha entre 2 e 12 parcelas.

        Args:
            qtd: Quantidade de parcelas informada.

        Returns:
            int: Quantidade dentro do limite permitido.

        Raises:
            ValueError: Se menor que 2 ou maior que o maximo.
        """
        if qtd < 2 or qtd > MAX_PARCELAS_CARTAO:
            raise ValueError("Cartao parcelado exige de 2 a 12 parcelas.")
        return qtd
