"""Modulo de servico para diagnostico na arvore N-aria de sistemas."""


class ControleDiagnostico:
    """Realiza travessias pre-ordem e marcacoes de diagnostico na arvore."""

    def gerar_arvore_indentada(self, arvore):
        """Formata toda a arvore de forma indentada via DFS pre-ordem.

        Args:
            arvore: Instancia de ArvoreNAria do diagnostico.

        Returns:
            str: Texto multi-linha indentado por profundidade.
        """
        # Usa lista encadeada interna como acumulador ou objeto mutavel
        acumulador = _AcumuladorTexto()
        arvore.percorrer_pre_ordem(acumulador.registrar_no)
        return acumulador.texto

    def marcar_alterado(self, prontuario, identificador):
        """Marca um no da arvore do prontuario como Alterado.

        Args:
            prontuario: Prontuario aberto em diagnostico.
            identificador: Codigo do item folha ou nome da estrutura.

        Returns:
            ItemDiagnostico: Item encontrado e marcado como Alterado.

        Raises:
            ValueError: Se prontuario fechado ou estrutura nao encontrada.
        """
        # Garante prontuario aberto e busca no em pre-ordem
        prontuario.exigir_aberto()
        no = prontuario.arvore_diagnostico.buscar_no(
            lambda item: item.corresponde(identificador)
        )
        if no is None:
            raise ValueError(f"Estrutura '{identificador}' nao encontrada.")
        return self._aplicar_alteracao(prontuario, no.dado)

    def _aplicar_alteracao(self, prontuario, item):
        """Aplica marcacao Alterado e empilha no historico se mudou estado.

        Args:
            prontuario: Prontuario aberto.
            item: ItemDiagnostico alvo da marcacao.

        Returns:
            ItemDiagnostico: Item atualizado.
        """
        # Empilha na PilhaEncadeada apenas quando ha mudanca real
        if not item.esta_alterado():
            item.marcar_alterado()
            prontuario.registrar_diagnostico_alterado(item)
        return item

    def listar_alterados(self, arvore):
        """Retorna todos os itens marcados como Alterado em pre-ordem.

        Args:
            arvore: ArvoreNAria do diagnostico.

        Returns:
            ListaEncadeada: Lista propria contendo itens alterados.
        """
        return arvore.filtrar_dados(lambda item: item.esta_alterado())


class _AcumuladorTexto:
    """Auxiliar leve para concatenar linhas da arvore sem listas built-in.

    Attributes:
        texto: Texto acumulado durante a travessia pre-ordem.
    """

    def __init__(self):
        """Inicializa o acumulador com texto vazio."""
        self.texto = ""

    def registrar_no(self, no, nivel):
        """Acrescenta uma linha indentada para o no visitado.

        Args:
            no: NoArvore sendo visitado.
            nivel: Profundidade do no na arvore.
        """
        # Aplica dois espacos por nivel de profundidade
        linha = f"{'  ' * nivel}- {no.dado}"
        self.texto = linha if not self.texto else f"{self.texto}\n{linha}"
