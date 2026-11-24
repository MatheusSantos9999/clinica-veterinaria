"""Modulo que implementa uma arvore N-aria generica nao binaria."""

from estruturas.arvore.no_arvore.no_arvore import NoArvore
from estruturas.lista.lista_encadeada import ListaEncadeada


class ArvoreNAria:
    """Arvore N-aria generica com percurso em profundidade pre-ordem.

    Attributes:
        raiz: NoArvore raiz da hierarquia.
    """

    def __init__(self, raiz):
        """Inicializa a arvore com um no raiz valido.

        Args:
            raiz: Instancia de NoArvore que inicia a hierarquia.

        Raises:
            TypeError: Se a raiz nao for uma instancia de NoArvore.
        """
        # Garante raiz valida na criacao da arvore
        if not isinstance(raiz, NoArvore):
            raise TypeError("A raiz deve ser uma instancia de NoArvore.")
        self.raiz = raiz

    def percorrer_pre_ordem(self, acao):
        """Executa uma acao em cada no usando DFS pre-ordem.

        Args:
            acao: Funcao que recebe (no, nivel) durante a visita.
        """
        self._visitar_pre_ordem(self.raiz, 0, acao)

    def _visitar_pre_ordem(self, no, nivel, acao):
        """Visita recursivamente o no atual e depois cada filho.

        Args:
            no: NoArvore sendo visitado.
            nivel: Profundidade atual a partir da raiz.
            acao: Funcao aplicada ao no e seu nivel.
        """
        # Visita o pai primeiro e propaga para todos os filhos
        acao(no, nivel)
        for filho in no.filhos:
            self._visitar_pre_ordem(filho, nivel + 1, acao)

    def buscar_no(self, criterio):
        """Busca o primeiro no que satisfaz o criterio em pre-ordem.

        Args:
            criterio: Funcao booleana aplicada ao dado de cada no.

        Returns:
            NoArvore: Primeiro no correspondente ou None.
        """
        return self._buscar_recursivo(self.raiz, criterio)

    def _buscar_recursivo(self, no, criterio):
        """Realiza busca em profundidade pre-ordem a partir de um no.

        Args:
            no: NoArvore atual da busca.
            criterio: Funcao booleana de correspondencia.

        Returns:
            NoArvore: No encontrado ou None.
        """
        # Testa o no corrente antes de descer pelos filhos
        if criterio(no.dado):
            return no
        for filho in no.filhos:
            encontrado = self._buscar_recursivo(filho, criterio)
            if encontrado is not None:
                return encontrado
        return None

    def filtrar_dados(self, criterio):
        """Coleta em pre-ordem os dados que satisfazem um criterio.

        Args:
            criterio: Funcao booleana aplicada ao dado de cada no.

        Returns:
            ListaEncadeada: Lista propria com os dados encontrados.
        """
        # Usa ListaEncadeada propria como acumulador de resultados
        resultado = ListaEncadeada()
        self._coletar_filtrados(self.raiz, criterio, resultado)
        return resultado

    def _coletar_filtrados(self, no, criterio, destino):
        """Percorre em pre-ordem acumulando dados correspondentes.

        Args:
            no: NoArvore corrente.
            criterio: Funcao booleana de filtro.
            destino: ListaEncadeada onde os dados serao inseridos.
        """
        if criterio(no.dado):
            destino.adicionar(no.dado)
        for filho in no.filhos:
            self._coletar_filtrados(filho, criterio, destino)

    def contar_nos(self):
        """Conta o total de nos presentes na arvore.

        Returns:
            int: Quantidade total de nos da hierarquia.
        """
        return self._contar_subarvore(self.raiz)

    def _contar_subarvore(self, no):
        """Conta recursivamente os nos de uma subarvore.

        Args:
            no: NoArvore raiz da subarvore avaliada.

        Returns:
            int: Total de nos na subarvore.
        """
        # Soma o proprio no com os totais de cada filho
        total = 1
        for filho in no.filhos:
            total += self._contar_subarvore(filho)
        return total
