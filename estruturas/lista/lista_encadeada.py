"""Modulo que implementa uma lista simplesmente encadeada propria."""

from estruturas.iterador.iterador_encadeado import IteradorEncadeado
from estruturas.no.no import No


class ListaEncadeada:
    """Lista encadeada generica com insercao O(1) nas extremidades."""

    def __init__(self):
        """Inicializa uma lista encadeada vazia."""
        # Ponteiros de inicio, fim e contador de elementos
        self._inicio = None
        self._fim = None
        self._tamanho = 0

    def __len__(self):
        """Retorna a quantidade de elementos na lista.

        Returns:
            int: Numero total de elementos armazenados.
        """
        return self._tamanho

    def __iter__(self):
        """Retorna um iterador proprio sobre os elementos da lista.

        Returns:
            IteradorEncadeado: Iterador posicionado no inicio.
        """
        return IteradorEncadeado(self._inicio)

    def esta_vazia(self):
        """Verifica se a lista nao possui elementos.

        Returns:
            bool: True se estiver vazia, False caso contrario.
        """
        return self._tamanho == 0

    def adicionar(self, dado):
        """Insere um novo elemento ao final da lista em O(1).

        Args:
            dado: Elemento a ser inserido na lista.
        """
        # Cria no e vincula ao fim da lista
        novo = No(dado)
        if self._inicio is None:
            self._inicio = novo
        else:
            self._fim.proximo = novo
        self._fim = novo
        self._tamanho += 1

    def adicionar_inicio(self, dado):
        """Insere um novo elemento no inicio da lista em O(1).

        Args:
            dado: Elemento a ser inserido na primeira posicao.
        """
        # Novo no aponta para o inicio anterior
        novo = No(dado, self._inicio)
        self._inicio = novo
        if self._fim is None:
            self._fim = novo
        self._tamanho += 1

    def obter_por_indice(self, indice):
        """Retorna o elemento armazenado em um indice especifico.

        Args:
            indice: Posicao inteira baseada em zero.

        Returns:
            O elemento na posicao solicitada.

        Raises:
            IndexError: Se o indice estiver fora dos limites.
        """
        # Valida intervalo e percorre ate o indice desejado
        self._validar_indice(indice)
        atual = self._inicio
        passo = 0
        while passo < indice:
            atual = atual.proximo
            passo += 1
        return atual.dado

    def buscar(self, criterio):
        """Busca o primeiro elemento que satisfaz uma funcao criterio.

        Args:
            criterio: Funcao booleana aplicada a cada elemento.

        Returns:
            Primeiro elemento correspondente ou None.
        """
        # Percorre os nos avaliando o criterio informado
        atual = self._inicio
        while atual is not None:
            if criterio(atual.dado):
                return atual.dado
            atual = atual.proximo
        return None

    def filtrar(self, criterio):
        """Retorna uma nova lista com os itens que atendem ao criterio.

        Args:
            criterio: Funcao booleana de filtragem.

        Returns:
            ListaEncadeada: Nova lista contendo os itens filtrados.
        """
        # Constroi lista resultante sem usar colecoes built-in
        resultado = ListaEncadeada()
        atual = self._inicio
        while atual is not None:
            if criterio(atual.dado):
                resultado.adicionar(atual.dado)
            atual = atual.proximo
        return resultado

    def remover_por_criterio(self, criterio):
        """Remove e retorna o primeiro elemento que atende ao criterio.

        Args:
            criterio: Funcao booleana que identifica o alvo.

        Returns:
            Elemento removido ou None se nao encontrado.
        """
        # Mantem ponteiro anterior para religar o encadeamento
        anterior = None
        atual = self._inicio
        while atual is not None:
            if criterio(atual.dado):
                return self._desvincular(anterior, atual)
            anterior = atual
            atual = atual.proximo
        return None

    def remover_elemento(self, alvo):
        """Remove a primeira ocorrencia de um elemento igual ao alvo.

        Args:
            alvo: Objeto a ser removido da lista.

        Returns:
            bool: True se removeu, False caso nao encontrado.
        """
        removido = self.remover_por_criterio(lambda item: item == alvo)
        return removido is not None

    def limpar(self):
        """Remove todos os elementos da lista."""
        # Zera ponteiros e contador para esvaziar a estrutura
        self._inicio = None
        self._fim = None
        self._tamanho = 0

    def _validar_indice(self, indice):
        """Valida se o indice pertence ao intervalo valido da lista.

        Args:
            indice: Posicao inteira a ser verificada.

        Raises:
            IndexError: Quando o indice e negativo ou >= tamanho.
        """
        if indice < 0 or indice >= self._tamanho:
            raise IndexError("Indice fora dos limites da lista.")

    def _desvincular(self, anterior, atual):
        """Desvincula um no da lista atualizando inicio, fim e tamanho.

        Args:
            anterior: No anterior ao alvo ou None se for o primeiro.
            atual: No que sera removido da cadeia.

        Returns:
            O dado contido no no removido.
        """
        # Atualiza inicio ou religa no anterior ao proximo
        if anterior is None:
            self._inicio = atual.proximo
        else:
            anterior.proximo = atual.proximo
        if atual is self._fim:
            self._fim = anterior
        self._tamanho -= 1
        return atual.dado
