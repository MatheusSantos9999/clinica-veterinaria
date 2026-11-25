"""Modulo de servico para controle de estoque com Lista + Fila de lotes."""

from estruturas.fila.fila_encadeada import FilaEncadeada
from estruturas.lista.lista_encadeada import ListaEncadeada
from modelos.consumo.item_consumido.item_consumido import ItemConsumido
from modelos.estoque.alerta_estoque.alerta_estoque import AlertaEstoque
from modelos.estoque.lote.lote import Lote
from modelos.estoque.perda_estoque.perda_estoque import PerdaEstoque
from modelos.estoque.produto_estoque.produto_estoque import ProdutoEstoque
from utilitarios.data_hora.validador_data import resolver_data
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_inteiro_nao_negativo,
    validar_inteiro_positivo,
)


class ControleEstoque:
    """Gerencia produtos em ListaEncadeada com FilaEncadeada FIFO de lotes.

    Attributes:
        produtos: ListaEncadeada de ProdutoEstoque.
        perdas: ListaEncadeada de PerdaEstoque por vencimento.
        alertas: ListaEncadeada de AlertaEstoque emitidos.
    """

    def __init__(self):
        """Inicializa produtos, perdas, alertas e contador de lotes."""
        # Estrutura externa da combinacao Lista de produtos + Fila de lotes
        self.produtos = ListaEncadeada()
        self.perdas = ListaEncadeada()
        self.alertas = ListaEncadeada()
        self._proximo_lote = 1

    def cadastrar_produto(self, codigo, nome, quantidade_minima=5):
        """Cadastra um novo produto sem lotes garantindo codigo unico.

        Args:
            codigo: Codigo unico do produto.
            nome: Nome comercial do produto.
            quantidade_minima: Limite minimo para emissao de alerta.

        Returns:
            ProdutoEstoque: Produto criado e inserido na lista.

        Raises:
            ValueError: Se ja existir produto com o codigo informado.
        """
        if self.buscar_produto(codigo) is not None:
            raise ValueError("Ja existe produto cadastrado com este codigo.")
        produto = ProdutoEstoque(codigo, nome, quantidade_minima)
        self.produtos.adicionar(produto)
        return produto

    def buscar_produto(self, codigo):
        """Localiza um produto na lista pelo codigo normalizado.

        Args:
            codigo: Codigo do medicamento, vacina ou material.

        Returns:
            ProdutoEstoque: Produto localizado ou None.
        """
        chave = normalizar_chave(codigo)
        return self.produtos.buscar(lambda prod: prod.chave_codigo() == chave)

    def adicionar_lote(
        self, codigo, nome_produto, dados_lote, quantidade_minima=5
    ):
        """Enfileira novo lote no produto, criando o produto se necessario.

        Args:
            codigo: Codigo do produto.
            nome_produto: Nome do produto.
            dados_lote: Instancia validada de DadosLote.
            quantidade_minima: Minimo usado caso o produto seja novo.

        Returns:
            Lote: Novo lote enfileirado na fila FIFO do produto.
        """
        # Obtem ou cria o produto e enfileira o lote no fim da fila
        prod = self._obter_ou_criar(codigo, nome_produto, quantidade_minima)
        lote = Lote(self._proximo_lote, prod.codigo, prod.nome, dados_lote)
        self._proximo_lote += 1
        prod.adicionar_lote(lote)
        return lote

    def _obter_ou_criar(self, codigo, nome_produto, quantidade_minima):
        """Recupera produto existente ou cadastra automaticamente um novo.

        Args:
            codigo: Codigo do produto.
            nome_produto: Nome do produto.
            quantidade_minima: Estoque minimo caso seja criado.

        Returns:
            ProdutoEstoque: Produto existente ou recem-criado.
        """
        produto = self.buscar_produto(codigo)
        if produto is not None:
            return produto
        return self.cadastrar_produto(codigo, nome_produto, quantidade_minima)

    def descartar_vencidos(self, data_referencia=None):
        """Descarta lotes vencidos de todos os produtos registrando perdas.

        Args:
            data_referencia: Data para validar vencimento (padrao hoje).

        Returns:
            ListaEncadeada: Perdas registradas nesta execucao.
        """
        # Percorre todos os produtos limpando lotes vencidos das filas
        ref = resolver_data(data_referencia)
        novas_perdas = ListaEncadeada()
        for produto in self.produtos:
            self._descartar_vencidos_produto(produto, ref, novas_perdas)
        return novas_perdas

    def _descartar_vencidos_produto(self, produto, data_ref, destino):
        """Remove lotes vencidos de um produto preservando a ordem FIFO.

        Args:
            produto: ProdutoEstoque inspecionado.
            data_ref: Data de referencia convertida.
            destino: ListaEncadeada acumulando novas perdas.
        """
        # Reconstroi fila apenas com lotes validos e contabiliza perdas
        fila_valida = FilaEncadeada()
        houve_perda = self._filtrar_lotes_validos(
            produto, data_ref, fila_valida, destino
        )
        produto.lotes = fila_valida
        if houve_perda:
            self.emitir_alerta_se_necessario(produto, data_ref)

    def _filtrar_lotes_validos(self, produto, data_ref, fila_valida, destino):
        """Separa lotes validos de vencidos preservando a ordem FIFO.

        Args:
            produto: ProdutoEstoque cuja fila sera drenada.
            data_ref: Data de referencia.
            fila_valida: FilaEncadeada destino dos lotes dentro da validade.
            destino: ListaEncadeada destino das perdas registradas.

        Returns:
            bool: True se ao menos um lote vencido foi descartado.
        """
        houve_perda = False
        while not produto.lotes.esta_vazia():
            lote = produto.lotes.desenfileirar()
            if lote.esta_vencido(data_ref):
                houve_perda = self._registrar_perda(lote, data_ref, destino)
            else:
                fila_valida.enfileirar(lote)
        return houve_perda

    def _registrar_perda(self, lote, data_ref, destino):
        """Cria e armazena registro de perda para um lote expirado.

        Args:
            lote: Lote vencido removido da fila.
            data_ref: Data do descarte.
            destino: ListaEncadeada local de retorno.

        Returns:
            bool: Sempre True indicando ocorrencia de perda.
        """
        perda = PerdaEstoque(lote, data_ref)
        self.perdas.adicionar(perda)
        destino.adicionar(perda)
        return True

    def ajustar_quantidade(
        self, codigo, numero_lote, nova_quantidade, data_referencia=None
    ):
        """Realiza ajuste manual de inventario em um lote especifico.

        Args:
            codigo: Codigo do produto.
            numero_lote: Numero do lote a ajustar.
            nova_quantidade: Novo saldo inteiro (>= 0).
            data_referencia: Data opcional para reavaliar alertas.

        Returns:
            Lote: Lote ajustado.

        Raises:
            ValueError: Se produto ou lote nao forem encontrados.
        """
        # Localiza lote preservando ordem FIFO e remove se zerado
        produto = self._exigir_produto(codigo)
        qtd = validar_inteiro_nao_negativo(nova_quantidade, "Nova quantidade")
        alvo = self._atualizar_lote_na_fila(produto, numero_lote, qtd)
        self.emitir_alerta_se_necessario(produto, data_referencia)
        return alvo

    def _atualizar_lote_na_fila(self, produto, numero_lote, nova_qtd):
        """Altera o saldo do lote alvo e remove da fila se ficar zerado.

        Args:
            produto: ProdutoEstoque dono da fila.
            numero_lote: Numero do lote procurado.
            nova_qtd: Nova quantidade validada.

        Returns:
            Lote: Instancia do lote encontrado e ajustado.

        Raises:
            ValueError: Se o lote nao existir na fila do produto.
        """
        # Drena e reconstroi fila mantendo a ordem cronologica FIFO
        nova_fila = FilaEncadeada()
        alvo = self._reconstruir_apos_ajuste(
            produto.lotes, numero_lote, nova_qtd, nova_fila
        )
        produto.lotes = nova_fila
        if alvo is None:
            raise ValueError(f"Lote #{numero_lote} nao encontrado.")
        return alvo

    def _reconstruir_apos_ajuste(self, fila, num_lote, nova_qtd, nova_fila):
        """Percorre fila aplicando ajuste ao lote correspondente.

        Args:
            fila: FilaEncadeada original do produto.
            num_lote: Numero do lote desejado.
            nova_qtd: Quantidade ajustada.
            nova_fila: FilaEncadeada reconstruida.

        Returns:
            Lote: Lote ajustado ou None se ausente.
        """
        alvo = None
        while not fila.esta_vazia():
            lote = fila.desenfileirar()
            if lote.numero_lote == num_lote:
                lote.ajustar_quantidade(nova_qtd)
                alvo = lote
            if lote.quantidade > 0:
                nova_fila.enfileirar(lote)
        return alvo

    def verificar_disponibilidade(self, codigo, quantidade, data_ref=None):
        """Verifica se ha saldo valido suficiente para o produto.

        Args:
            codigo: Codigo do produto.
            quantidade: Quantidade necessaria (> 0).
            data_ref: Data usada para checar validade.

        Returns:
            bool: True se produto existe e possui saldo valido suficiente.
        """
        qtd = validar_inteiro_positivo(quantidade, "Quantidade")
        produto = self.buscar_produto(codigo)
        if produto is None:
            return False
        return produto.quantidade_valida(data_ref) >= qtd

    def baixar_estoque(self, codigo, quantidade, data_referencia=None):
        """Consome unidades do produto a partir do lote valido mais antigo.

        Args:
            codigo: Codigo do produto a baixar.
            quantidade: Quantidade a consumir (> 0).
            data_referencia: Data usada para descartar lotes vencidos.

        Returns:
            ListaEncadeada: Lista de ItemConsumido de cada lote utilizado.

        Raises:
            ValueError: Se produto inexistente ou saldo valido insuficiente.
        """
        # Descarta vencidos antes de baixar e consome em ordem FIFO
        ref = resolver_data(data_referencia)
        produto = self._preparar_baixa(codigo, quantidade, ref)
        consumidos = self._consumir_fila_fifo(produto, quantidade)
        self.emitir_alerta_se_necessario(produto, ref)
        return consumidos

    def _preparar_baixa(self, codigo, quantidade, data_ref):
        """Valida produto, limpa vencidos e garante saldo para baixa.

        Args:
            codigo: Codigo do produto.
            quantidade: Quantidade solicitada.
            data_ref: Data de referencia de validade.

        Returns:
            ProdutoEstoque: Produto validado com saldo suficiente.
        """
        produto = self._exigir_produto(codigo)
        qtd = validar_inteiro_positivo(quantidade, "Quantidade")
        self._descartar_vencidos_produto(produto, data_ref, ListaEncadeada())
        if produto.quantidade_valida(data_ref) < qtd:
            raise ValueError(f"Estoque insuficiente para [{produto.codigo}].")
        return produto

    def _consumir_fila_fifo(self, produto, quantidade):
        """Retira unidades da frente da fila de lotes ate zerar a demanda.

        Args:
            produto: ProdutoEstoque com saldo suficiente garantido.
            quantidade: Total a consumir (> 0).

        Returns:
            ListaEncadeada: Itens consumidos detalhando lotes e precos.
        """
        # Consome sempre o lote da frente e desenfileira quando zera
        consumidos = ListaEncadeada()
        restante = quantidade
        while restante > 0:
            restante -= self._consumir_lote_frente(
                produto, restante, consumidos
            )
        return consumidos

    def _consumir_lote_frente(self, produto, restante, consumidos):
        """Consome unidades do lote na frente e desenfileira se zerar.

        Args:
            produto: ProdutoEstoque dono da fila de lotes.
            restante: Quantidade ainda pendente de baixa.
            consumidos: ListaEncadeada destino de ItemConsumido.

        Returns:
            int: Quantidade efetivamente consumida deste lote.
        """
        lote = produto.lotes.espiar()
        retirado = lote.consumir(restante)
        consumidos.adicionar(ItemConsumido(lote, retirado))
        if lote.quantidade == 0:
            produto.lotes.desenfileirar()
        return retirado

    def emitir_alerta_se_necessario(self, produto, data_referencia=None):
        """Registra AlertaEstoque se o saldo valido ficar abaixo do minimo.

        Args:
            produto: ProdutoEstoque avaliado.
            data_referencia: Data usada para computar saldo valido.

        Returns:
            AlertaEstoque: Alerta gerado ou None se saldo adequado.
        """
        saldo = produto.quantidade_valida(data_referencia)
        if saldo >= produto.quantidade_minima:
            return None
        alerta = AlertaEstoque(produto, saldo)
        self.alertas.adicionar(alerta)
        return alerta

    def _exigir_produto(self, codigo):
        """Busca produto pelo codigo ou levanta ValueError se ausente.

        Args:
            codigo: Codigo procurado.

        Returns:
            ProdutoEstoque: Produto localizado.

        Raises:
            ValueError: Quando o codigo nao esta cadastrado.
        """
        produto = self.buscar_produto(codigo)
        if produto is None:
            raise ValueError(f"Produto '{codigo}' nao encontrado no estoque.")
        return produto
