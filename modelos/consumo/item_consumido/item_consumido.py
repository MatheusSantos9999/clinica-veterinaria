"""Modulo que registra cada lote consumido em uma baixa de estoque."""

from utilitarios.validacao.validador_entrada import (
    validar_inteiro_positivo,
    validar_texto_obrigatorio,
    validar_valor_nao_negativo,
)


class ItemConsumido:
    """Detalha uma parcela de medicamento baixada de um lote especifico.

    Attributes:
        codigo_produto: Codigo do produto consumido.
        nome_produto: Nome do produto consumido.
        numero_lote: Lote especifico de onde ocorreu a baixa FIFO.
        quantidade: Quantidade efetivamente retirada do lote.
        preco_unitario_venda: Preco unitario de venda daquele lote.
        preco_unitario_compra: Preco unitario de compra daquele lote.
    """

    def __init__(self, lote, quantidade):
        """Cria um item consumido a partir do lote e da quantidade baixada.

        Args:
            lote: Instancia de Lote que forneceu as unidades.
            quantidade: Quantidade efetivamente consumida (> 0).
        """
        # Captura snapshot de identificacao e precos do lote usado
        self._definir_identificacao(lote, quantidade)
        self._definir_precos(lote)

    def _definir_identificacao(self, lote, quantidade):
        """Valida produto, lote e quantidade retirada.

        Args:
            lote: Lote de origem.
            quantidade: Unidades baixadas (> 0).
        """
        self.codigo_produto = validar_texto_obrigatorio(lote.codigo, "Codigo")
        self.nome_produto = validar_texto_obrigatorio(
            lote.nome_produto, "Produto"
        )
        self.numero_lote = validar_inteiro_positivo(lote.numero_lote, "Lote")
        self.quantidade = validar_inteiro_positivo(quantidade, "Quantidade")

    def _definir_precos(self, lote):
        """Valida e registra os precos unitarios de venda e compra do lote.

        Args:
            lote: Lote de origem.
        """
        self.preco_unitario_venda = validar_valor_nao_negativo(
            lote.preco_venda, "Preco venda"
        )
        self.preco_unitario_compra = validar_valor_nao_negativo(
            lote.preco_compra, "Preco compra"
        )

    def subtotal_venda(self):
        """Calcula o valor de venda desta baixa de lote.

        Returns:
            float: Quantidade multiplicada pelo preco de venda do lote.
        """
        return round(self.quantidade * self.preco_unitario_venda, 2)

    def subtotal_custo(self):
        """Calcula o custo de aquisicao desta baixa de lote.

        Returns:
            float: Quantidade multiplicada pelo preco de compra do lote.
        """
        return round(self.quantidade * self.preco_unitario_compra, 2)

    def __str__(self):
        """Retorna resumo legivel do consumo ocorrido no lote.

        Returns:
            str: Produto, lote, quantidade e subtotal cobrado.
        """
        return (
            f"[{self.codigo_produto}] {self.nome_produto} (Lote "
            f"#{self.numero_lote}) x{self.quantidade} = "
            f"R$ {self.subtotal_venda():.2f}"
        )
