"""Modulo que define o registro de perda por descarte de lote vencido."""

from utilitarios.data_hora.validador_data import formatar_data


class PerdaEstoque:
    """Registra um lote vencido descartado e o prejuizo financeiro gerado.

    Attributes:
        codigo_produto: Codigo do produto descartado.
        nome_produto: Nome do produto descartado.
        numero_lote: Numero identificador do lote vencido.
        fornecedor: Fornecedor do lote.
        quantidade_perdida: Unidades descartadas.
        valor_prejuizo: Prejuizo calculado com base no preco de compra.
        data_validade: Data em que o lote venceu.
        data_descarte: Data em que o descarte foi registrado.
    """

    def __init__(self, lote, data_descarte):
        """Cria um registro de perda a partir de um lote vencido.

        Args:
            lote: Instancia de Lote que expirou.
            data_descarte: Data do registro do descarte.
        """
        # Extrai metadados e calcula prejuizo pelo custo de compra
        self._copiar_identificacao(lote)
        self.quantidade_perdida = lote.quantidade
        self.valor_prejuizo = round(lote.quantidade * lote.preco_compra, 2)
        self.data_validade = lote.data_validade
        self.data_descarte = data_descarte

    def _copiar_identificacao(self, lote):
        """Copia codigo, nome, numero e fornecedor do lote descartado.

        Args:
            lote: Instancia de Lote vencido.
        """
        self.codigo_produto = lote.codigo
        self.nome_produto = lote.nome_produto
        self.numero_lote = lote.numero_lote
        self.fornecedor = lote.fornecedor

    def __str__(self):
        """Retorna resumo legivel da perda registrada.

        Returns:
            str: Texto detalhando produto, lote, validade, qtd e prejuizo.
        """
        val = formatar_data(self.data_validade)
        return (
            f"PERDA [{self.codigo_produto}] {self.nome_produto} "
            f"(Lote #{self.numero_lote}, Val: {val}) | "
            f"Qtd: {self.quantidade_perdida} | "
            f"Prejuizo: R$ {self.valor_prejuizo:.2f}"
        )
