"""Modulo que define o alerta emitido quando o estoque fica baixo."""

from utilitarios.data_hora.validador_data import obter_data_hora_atual


class AlertaEstoque:
    """Representa um alerta de saldo abaixo do minimo para um produto.

    Attributes:
        codigo_produto: Codigo do produto em nivel critico.
        nome_produto: Nome do produto em nivel critico.
        quantidade_atual: Saldo atual disponivel.
        quantidade_minima: Limite minimo configurado.
        data_hora: Carimbo temporal de emissao do alerta.
    """

    def __init__(self, produto, quantidade_atual):
        """Inicializa o alerta com os dados atuais do produto.

        Args:
            produto: Instancia de ProdutoEstoque em estado critico.
            quantidade_atual: Quantidade valida atual do produto.
        """
        # Registra snapshot do nivel critico no momento do evento
        self.codigo_produto = produto.codigo
        self.nome_produto = produto.nome
        self.quantidade_atual = quantidade_atual
        self.quantidade_minima = produto.quantidade_minima
        self.data_hora = obter_data_hora_atual()

    def __str__(self):
        """Retorna mensagem legivel de alerta de estoque baixo.

        Returns:
            str: Aviso destacando produto, saldo atual e minimo.
        """
        return (
            f"ALERTA ESTOQUE BAIXO: [{self.codigo_produto}] "
            f"{self.nome_produto} | Atual: {self.quantidade_atual} "
            f"< Minimo: {self.quantidade_minima} ({self.data_hora})"
        )
