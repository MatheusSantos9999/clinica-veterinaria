"""Modulo que define a entidade Lote de medicamentos, vacinas ou insumos."""

from utilitarios.data_hora.validador_data import esta_vencido, formatar_data
from utilitarios.validacao.validador_entrada import (
    validar_inteiro_nao_negativo,
    validar_inteiro_positivo,
    validar_texto_obrigatorio,
)


class Lote:
    """Representa um lote especifico de um produto no estoque.

    Attributes:
        numero_lote: Identificador unico sequencial do lote.
        codigo: Codigo do produto ao qual o lote pertence.
        nome_produto: Nome do produto armazenado.
        fornecedor: Fornecedor de origem do lote.
        preco_compra: Preco unitario de compra.
        preco_venda: Preco unitario de venda.
        data_compra: Data de aquisicao do lote.
        data_validade: Data de validade do lote.
        quantidade: Quantidade atual disponivel neste lote.
    """

    def __init__(self, numero_lote, codigo, nome_produto, dados_lote):
        """Inicializa o lote com identificacao e dados comerciais.

        Args:
            numero_lote: Numero inteiro positivo do lote.
            codigo: Codigo do produto.
            nome_produto: Nome do produto.
            dados_lote: Instancia de DadosLote validada.
        """
        # Registra identificadores e copia atributos validados
        self.numero_lote = validar_inteiro_positivo(numero_lote, "Lote")
        self.codigo = validar_texto_obrigatorio(codigo, "Codigo produto")
        self.nome_produto = validar_texto_obrigatorio(nome_produto, "Produto")
        self._copiar_dados(dados_lote)

    def _copiar_dados(self, dados):
        """Copia os campos comerciais e temporais de DadosLote.

        Args:
            dados: Objeto DadosLote validado.
        """
        self.fornecedor = dados.fornecedor
        self.preco_compra = dados.preco_compra
        self.preco_venda = dados.preco_venda
        self.data_compra = dados.data_compra
        self.data_validade = dados.data_validade
        self.quantidade = dados.quantidade

    def esta_vencido(self, data_referencia=None):
        """Verifica se o lote esta vencido em uma data de referencia.

        Args:
            data_referencia: Data de comparacao ou None para hoje.

        Returns:
            bool: True se o lote estiver vencido.
        """
        return esta_vencido(self.data_validade, data_referencia)

    def consumir(self, quantidade):
        """Deduz ate a quantidade disponivel deste lote.

        Args:
            quantidade: Quantidade solicitada (> 0).

        Returns:
            int: Quantidade efetivamente consumida deste lote.
        """
        # Consome o menor valor entre o pedido e o saldo do lote
        solicitado = validar_inteiro_positivo(quantidade, "Quantidade")
        consumido = min(solicitado, self.quantidade)
        self.quantidade -= consumido
        return consumido

    def ajustar_quantidade(self, nova_quantidade):
        """Ajusta manualmente a quantidade em estoque (inventario).

        Args:
            nova_quantidade: Novo saldo inteiro nao negativo.
        """
        self.quantidade = validar_inteiro_nao_negativo(
            nova_quantidade, "Nova quantidade"
        )

    def __str__(self):
        """Retorna descricao resumida do lote com datas e saldo.

        Returns:
            str: Texto formatado com lote, fornecedor, validade e saldo.
        """
        val = formatar_data(self.data_validade)
        comp = formatar_data(self.data_compra)
        return (
            f"Lote #{self.numero_lote} ({self.fornecedor}) | "
            f"Compra: {comp} | Val: {val} | Qtd: {self.quantidade} | "
            f"Venda: R$ {self.preco_venda:.2f}"
        )
