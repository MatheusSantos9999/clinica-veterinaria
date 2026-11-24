"""Modulo que implementa uma fila FIFO encadeada propria."""

from estruturas.iterador.iterador_encadeado import IteradorEncadeado
from estruturas.no.no import No


class FilaEncadeada:
    """Fila generica FIFO com operacoes de entrada e saida em O(1)."""

    def __init__(self):
        """Inicializa uma fila vazia."""
        # Ponteiros para frente, tras e contador de elementos
        self._frente = None
        self._tras = None
        self._tamanho = 0

    def __len__(self):
        """Retorna a quantidade de itens atualmente na fila.

        Returns:
            int: Numero total de elementos na fila.
        """
        return self._tamanho

    def __iter__(self):
        """Retorna iterador da frente para o final da fila.

        Returns:
            IteradorEncadeado: Iterador posicionado na frente.
        """
        return IteradorEncadeado(self._frente)

    def esta_vazia(self):
        """Indica se a fila nao possui elementos.

        Returns:
            bool: True se vazia, False caso contrario.
        """
        return self._tamanho == 0

    def enfileirar(self, dado):
        """Adiciona um elemento ao final da fila em O(1).

        Args:
            dado: Elemento a ser enfileirado.
        """
        # Encadeia novo no ao final da fila
        novo = No(dado)
        if self._frente is None:
            self._frente = novo
        else:
            self._tras.proximo = novo
        self._tras = novo
        self._tamanho += 1

    def desenfileirar(self):
        """Remove e retorna o elemento mais antigo da frente em O(1).

        Returns:
            Elemento removido da frente da fila.

        Raises:
            IndexError: Se a fila estiver vazia.
        """
        # Valida fila nao vazia e avanca ponteiro da frente
        if self._frente is None:
            raise IndexError("Nao e possivel desenfileirar fila vazia.")
        dado = self._frente.dado
        self._frente = self._frente.proximo
        if self._frente is None:
            self._tras = None
        self._tamanho -= 1
        return dado

    def espiar(self):
        """Retorna o elemento na frente sem remove-lo em O(1).

        Returns:
            Elemento da frente ou None se a fila estiver vazia.
        """
        if self._frente is None:
            return None
        return self._frente.dado

    def buscar(self, criterio):
        """Procura o primeiro elemento da fila que atende ao criterio.

        Args:
            criterio: Funcao booleana aplicada a cada elemento.

        Returns:
            Elemento encontrado ou None.
        """
        # Percorre a fila da frente ate o final
        atual = self._frente
        while atual is not None:
            if criterio(atual.dado):
                return atual.dado
            atual = atual.proximo
        return None
