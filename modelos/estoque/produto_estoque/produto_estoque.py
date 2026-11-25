"""Modulo que define ProdutoEstoque com fila FIFO propria de lotes."""

from estruturas.fila.fila_encadeada import FilaEncadeada
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_inteiro_nao_negativo,
    validar_texto_obrigatorio,
)


class ProdutoEstoque:
    """Representa um produto do estoque que gerencia seus lotes em fila FIFO.

    Attributes:
        codigo: Codigo identificador unico do produto.
        nome: Nome comercial do medicamento, vacina ou material.
        quantidade_minima: Limite minimo para disparo de alerta.
        lotes: FilaEncadeada contendo os lotes do mais antigo ao mais novo.
    """

    def __init__(self, codigo, nome, quantidade_minima=5):
        """Inicializa um produto com fila vazia de lotes.

        Args:
            codigo: Codigo unico do produto.
            nome: Nome do produto.
            quantidade_minima: Estoque minimo para alerta (>= 0).
        """
        # Mantem FilaEncadeada propria para garantir baixa FIFO
        self.codigo = validar_texto_obrigatorio(codigo, "Codigo do produto")
        self.nome = validar_texto_obrigatorio(nome, "Nome do produto")
        self.quantidade_minima = validar_inteiro_nao_negativo(
            quantidade_minima, "Quantidade minima"
        )
        self.lotes = FilaEncadeada()

    def chave_codigo(self):
        """Retorna a chave normalizada do codigo para comparacoes.

        Returns:
            str: Codigo do produto em minusculas.
        """
        return normalizar_chave(self.codigo)

    def adicionar_lote(self, lote):
        """Enfileira um novo lote ao final da fila FIFO do produto.

        Args:
            lote: Instancia de Lote pertencente a este produto.
        """
        self.lotes.enfileirar(lote)

    def quantidade_total(self):
        """Soma a quantidade disponivel em todos os lotes na fila.

        Returns:
            int: Saldo total bruto do produto.
        """
        # Percorre todos os lotes da fila acumulando saldos
        total = 0
        for lote in self.lotes:
            total += lote.quantidade
        return total

    def quantidade_valida(self, data_referencia=None):
        """Soma apenas a quantidade em lotes dentro da validade.

        Args:
            data_referencia: Data para checar vencimento ou None.

        Returns:
            int: Total disponivel em lotes nao vencidos.
        """
        total = 0
        for lote in self.lotes:
            if not lote.esta_vencido(data_referencia):
                total += lote.quantidade
        return total

    def esta_abaixo_do_minimo(self, data_referencia=None):
        """Verifica se o saldo valido esta abaixo do minimo definido.

        Args:
            data_referencia: Data de referencia para validade.

        Returns:
            bool: True se saldo valido < quantidade_minima.
        """
        return self.quantidade_valida(data_referencia) < self.quantidade_minima

    def preco_venda_atual(self, data_referencia=None):
        """Retorna o preco de venda do lote valido mais antigo.

        Args:
            data_referencia: Data de comparacao ou None.

        Returns:
            float: Preco unitario do lote mais antigo valido ou 0.0.
        """
        # Localiza primeiro lote valido na fila FIFO
        for lote in self.lotes:
            if not lote.esta_vencido(data_referencia) and lote.quantidade > 0:
                return lote.preco_venda
        return 0.0

    def __str__(self):
        """Retorna resumo legivel do produto e total em estoque.

        Returns:
            str: Descricao com codigo, nome, saldo, minimo e lotes.
        """
        return (
            f"[{self.codigo}] {self.nome} | Total: {self.quantidade_total()} "
            f"| Minimo: {self.quantidade_minima} | Lotes: {len(self.lotes)}"
        )
