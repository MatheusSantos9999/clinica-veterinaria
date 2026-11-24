"""Modulo que define o no de uma arvore N-aria com 0 a N filhos."""

from estruturas.lista.lista_encadeada import ListaEncadeada


class NoArvore:
    """Representa um no de arvore generica com quantidade livre de filhos.

    Attributes:
        dado: Valor armazenado no no.
        filhos: ListaEncadeada contendo os nos filhos diretos.
    """

    def __init__(self, dado):
        """Inicializa um no de arvore sem filhos.

        Args:
            dado: Conteudo associado ao no.
        """
        # Usa ListaEncadeada propria para suportar 0 a N filhos
        self.dado = dado
        self.filhos = ListaEncadeada()

    def adicionar_filho(self, filho):
        """Vincula um no filho ao final da lista de filhos.

        Args:
            filho: Instancia de NoArvore a ser adicionada.

        Returns:
            NoArvore: O proprio no filho adicionado.

        Raises:
            TypeError: Se o argumento nao for um NoArvore.
        """
        # Garante que apenas nos de arvore sejam acoplados
        if not isinstance(filho, NoArvore):
            raise TypeError("Filho deve ser uma instancia de NoArvore.")
        self.filhos.adicionar(filho)
        return filho

    def eh_folha(self):
        """Indica se o no e um item final sem filhos.

        Returns:
            bool: True se nao possuir filhos, False caso contrario.
        """
        return self.filhos.esta_vazia()

    def quantidade_filhos(self):
        """Retorna o numero de filhos diretos deste no.

        Returns:
            int: Quantidade de filhos ligados ao no.
        """
        return len(self.filhos)
