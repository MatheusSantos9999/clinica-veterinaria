"""Modulo que define o iterador proprio para nos encadeados."""


class IteradorEncadeado:
    """Iterador proprio que percorre uma cadeia de nos encadeados."""

    def __init__(self, no_inicial):
        """Inicializa o iterador apontando para o primeiro no.

        Args:
            no_inicial: Primeiro no da sequencia ou None.
        """
        # Mantem referencia para o no atual da travessia
        self._atual = no_inicial

    def __iter__(self):
        """Retorna a propria instancia como iterador.

        Returns:
            IteradorEncadeado: A propria instancia iteravel.
        """
        return self

    def __next__(self):
        """Avanca para o proximo no e devolve o dado atual.

        Returns:
            O dado armazenado no no corrente.

        Raises:
            StopIteration: Quando nao ha mais nos a percorrer.
        """
        # Encerra a iteracao ao atingir o fim da cadeia
        if self._atual is None:
            raise StopIteration
        dado = self._atual.dado
        self._atual = self._atual.proximo
        return dado
