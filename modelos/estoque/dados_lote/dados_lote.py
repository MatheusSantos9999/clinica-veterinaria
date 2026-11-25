"""Modulo que agrupa especificacoes de compra e validade de um lote."""

from utilitarios.data_hora.validador_data import converter_data
from utilitarios.validacao.validador_entrada import (
    validar_inteiro_positivo,
    validar_texto_obrigatorio,
    validar_valor_nao_negativo,
)


class DadosLote:
    """Objeto de valor com dados comerciais e temporais de um lote.

    Attributes:
        fornecedor: Nome do fornecedor do lote.
        preco_compra: Custo unitario pago na compra.
        preco_venda: Preco unitario cobrado no atendimento.
        data_compra: Data de aquisicao como objeto date.
        data_validade: Data de vencimento como objeto date.
        quantidade: Quantidade inicial recebida (> 0).
    """

    def __init__(
        self, fornecedor, preco_compra, preco_venda,
        data_compra, data_validade, quantidade,
    ):
        """Valida e inicializa os dados comerciais do lote.

        Args:
            fornecedor: Nome do fornecedor.
            preco_compra: Valor unitario de compra (>= 0).
            preco_venda: Valor unitario de venda (>= 0).
            data_compra: Data de compra (DD/MM/AAAA, AAAA-MM-DD ou date).
            data_validade: Data de validade (>= data_compra).
            quantidade: Quantidade recebida (> 0).
        """
        # Divide validacoes entre valores comerciais e cronologia
        self._definir_comercial(fornecedor, preco_compra, preco_venda)
        self._definir_datas_e_qtd(data_compra, data_validade, quantidade)

    def _definir_comercial(self, fornecedor, preco_compra, preco_venda):
        """Valida fornecedor e precos de compra e venda.

        Args:
            fornecedor: Nome do fornecedor.
            preco_compra: Preco unitario de aquisicao.
            preco_venda: Preco unitario de venda.
        """
        self.fornecedor = validar_texto_obrigatorio(fornecedor, "Fornecedor")
        self.preco_compra = validar_valor_nao_negativo(
            preco_compra, "Preco de compra"
        )
        self.preco_venda = validar_valor_nao_negativo(
            preco_venda, "Preco de venda"
        )

    def _definir_datas_e_qtd(self, data_compra, data_validade, quantidade):
        """Valida coerencia das datas e a quantidade positiva inicial.

        Args:
            data_compra: Data de compra do lote.
            data_validade: Data de validade do lote.
            quantidade: Quantidade inicial de unidades.

        Raises:
            ValueError: Se validade for anterior a data da compra.
        """
        # Impede cadastrar lote com validade anterior a compra
        self.data_compra = converter_data(data_compra)
        self.data_validade = converter_data(data_validade)
        if self.data_validade < self.data_compra:
            raise ValueError("Validade nao pode ser anterior a compra.")
        self.quantidade = validar_inteiro_positivo(quantidade, "Quantidade")
