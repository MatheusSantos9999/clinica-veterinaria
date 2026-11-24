"""Modulo que define o no generico para estruturas encadeadas."""


class No:
    """Representa um no simples contendo dado e referencia ao proximo.

    Attributes:
        dado: Valor armazenado no no.
        proximo: Referencia para o proximo no ou None.
    """

    def __init__(self, dado, proximo=None):
        """Inicializa o no com o valor e o ponteiro para o proximo.

        Args:
            dado: Elemento a ser armazenado no no.
            proximo: Proximo no na cadeia encadeada.
        """
        # Armazena dado e referencia encadeada
        self.dado = dado
        self.proximo = proximo
