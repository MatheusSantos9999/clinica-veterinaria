"""Modulo que representa um medicamento prescrito em um prontuario."""

from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_inteiro_positivo,
    validar_texto_obrigatorio,
    validar_valor_nao_negativo,
)


class ItemMedicamento:
    """Representa um medicamento ou vacina incluido no prontuario.

    Attributes:
        codigo_produto: Codigo do produto no estoque.
        nome_produto: Nome legivel do medicamento ou vacina.
        quantidade: Quantidade aplicada (> 0).
        valor_unitario: Preco unitario estimado de referencia.
    """

    def __init__(
        self, codigo_produto, nome_produto, quantidade, valor_unitario=0.0
    ):
        """Inicializa um item de medicamento prescrito.

        Args:
            codigo_produto: Codigo do produto no estoque.
            nome_produto: Nome do medicamento ou vacina.
            quantidade: Unidades prescritas (> 0).
            valor_unitario: Valor unitario de referencia (>= 0).
        """
        # Valida identificacao e quantidades/precos separadamente
        self._definir_produto(codigo_produto, nome_produto)
        self._definir_quantificacao(quantidade, valor_unitario)

    def _definir_produto(self, codigo_produto, nome_produto):
        """Valida codigo e nome do medicamento.

        Args:
            codigo_produto: Codigo do produto no estoque.
            nome_produto: Nome comercial do produto.
        """
        self.codigo_produto = validar_texto_obrigatorio(
            codigo_produto, "Codigo do produto"
        )
        self.nome_produto = validar_texto_obrigatorio(
            nome_produto, "Nome do produto"
        )

    def _definir_quantificacao(self, quantidade, valor_unitario):
        """Valida quantidade prescrita e valor unitario estimado.

        Args:
            quantidade: Quantidade aplicada (> 0).
            valor_unitario: Preco unitario estimado (>= 0).
        """
        self.quantidade = validar_inteiro_positivo(quantidade, "Quantidade")
        self.valor_unitario = validar_valor_nao_negativo(
            valor_unitario, "Valor unitario"
        )

    def chave_codigo(self):
        """Retorna a chave normalizada do codigo do produto.

        Returns:
            str: Codigo em minusculas e sem espacos laterais.
        """
        return normalizar_chave(self.codigo_produto)

    def valor_estimado(self):
        """Calcula o subtotal estimado do medicamento prescrito.

        Returns:
            float: Quantidade multiplicada pelo valor unitario.
        """
        return round(self.quantidade * self.valor_unitario, 2)

    def __str__(self):
        """Retorna representacao legivel do medicamento no prontuario.

        Returns:
            str: Codigo, nome, quantidade e valor estimado.
        """
        return (
            f"[{self.codigo_produto}] {self.nome_produto} "
            f"x{self.quantidade} (Est.: R$ {self.valor_estimado():.2f})"
        )
