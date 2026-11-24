"""Modulo que implementa uma pilha LIFO encadeada propria."""

from estruturas.iterador.iterador_encadeado import IteradorEncadeado
from estruturas.no.no import No


class PilhaEncadeada:
    """Pilha generica LIFO com operacoes de topo em O(1)."""

    def __init__(self):
        """Inicializa uma pilha vazia."""
        # Ponteiro para o topo e contador de elementos
        self._topo = None
        self._tamanho = 0

    def __len__(self):
        """Retorna a quantidade de elementos empilhados.

        Returns:
            int: Numero total de elementos na pilha.
        """
        return self._tamanho

    def __iter__(self):
        """Retorna iterador do topo ate a base da pilha.

        Returns:
            IteradorEncadeado: Iterador posicionado no topo.
        """
        return IteradorEncadeado(self._topo)

    def esta_vazia(self):
        """Verifica se a pilha nao contem elementos.

        Returns:
            bool: True se vazia, False caso contrario.
        """
        return self._tamanho == 0

    def empilhar(self, dado):
        """Insere um novo elemento no topo da pilha em O(1).

        Args:
            dado: Elemento a ser colocado no topo.
        """
        # Novo no passa a ser o topo apontando para o anterior
        self._topo = No(dado, self._topo)
        self._tamanho += 1

    def desempilhar(self):
        """Remove e retorna o elemento do topo em O(1).

        Returns:
            Elemento removido do topo da pilha.

        Raises:
            IndexError: Se a pilha estiver vazia.
        """
        # Verifica pilha vazia e move topo para o proximo no
        if self._topo is None:
            raise IndexError("Nao e possivel desempilhar pilha vazia.")
        dado = self._topo.dado
        self._topo = self._topo.proximo
        self._tamanho -= 1
        return dado

    def topo(self):
        """Consulta o elemento no topo sem remove-lo em O(1).

        Returns:
            Elemento no topo ou None se a pilha estiver vazia.
        """
        if self._topo is None:
            return None
        return self._topo.dado
