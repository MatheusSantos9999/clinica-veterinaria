"""Modulo fabrica para montar a arvore pre-definida de sistemas animais."""

from estruturas.arvore.arvore_n_aria.arvore_n_aria import ArvoreNAria
from estruturas.arvore.no_arvore.no_arvore import NoArvore
from modelos.diagnostico.item_diagnostico.item_diagnostico import (
    ItemDiagnostico,
)


class FabricaArvoreAnimal:
    """Constroi instancias independentes da arvore anatomica padrao."""

    @staticmethod
    def criar_padrao():
        """Cria uma nova arvore N-aria pre-definida para um diagnostico.

        Returns:
            ArvoreNAria: Arvore anatomica com sistemas, orgaos e codigos.
        """
        # Monta raiz Animal e acopla quatro sistemas com 0 a N filhos
        raiz = NoArvore(ItemDiagnostico("Animal"))
        raiz.adicionar_filho(FabricaArvoreAnimal._criar_digestorio())
        raiz.adicionar_filho(FabricaArvoreAnimal._criar_respiratorio())
        raiz.adicionar_filho(FabricaArvoreAnimal._criar_pele())
        raiz.adicionar_filho(FabricaArvoreAnimal._criar_locomotor())
        return ArvoreNAria(raiz)

    @staticmethod
    def _no(nome, codigo=None):
        """Instancia um NoArvore contendo um ItemDiagnostico.

        Args:
            nome: Nome do sistema, orgao ou estrutura.
            codigo: Codigo de folha opcional.

        Returns:
            NoArvore: Novo no pronto para acoplar na arvore.
        """
        return NoArvore(ItemDiagnostico(nome, codigo))

    @staticmethod
    def _criar_digestorio():
        """Constroi a subarvore do Sistema digestorio.

        Returns:
            NoArvore: No do Sistema digestorio com seus orgaos.
        """
        # Inclui Estomago, Intestino e Figado com codigos de folha
        no = FabricaArvoreAnimal._no
        sistema = no("Sistema digestório")
        sistema.adicionar_filho(no("Estômago", "DIG-01"))
        sistema.adicionar_filho(no("Intestino", "DIG-02"))
        sistema.adicionar_filho(no("Fígado", "DIG-03"))
        return sistema

    @staticmethod
    def _criar_respiratorio():
        """Constroi a subarvore do Sistema respiratorio.

        Returns:
            NoArvore: No do Sistema respiratorio com seus orgaos.
        """
        # Inclui Pulmoes, Traqueia e Cavidade nasal
        no = FabricaArvoreAnimal._no
        sistema = no("Sistema respiratório")
        sistema.adicionar_filho(no("Pulmões", "RES-01"))
        sistema.adicionar_filho(no("Traqueia", "RES-02"))
        sistema.adicionar_filho(no("Cavidade nasal", "RES-03"))
        return sistema

    @staticmethod
    def _criar_pele():
        """Constroi a subarvore de Pele e anexos cutaneos.

        Returns:
            NoArvore: No da Pele com pelos, unhas e derme.
        """
        # Inclui Pelos, Unhas e Derme
        sistema = NoArvore(ItemDiagnostico("Pele"))
        sistema.adicionar_filho(NoArvore(ItemDiagnostico("Pelos", "PEL-01")))
        sistema.adicionar_filho(NoArvore(ItemDiagnostico("Unhas", "PEL-02")))
        sistema.adicionar_filho(NoArvore(ItemDiagnostico("Derme", "PEL-03")))
        return sistema

    @staticmethod
    def _criar_locomotor():
        """Constroi a subarvore do Sistema locomotor com subestruturas.

        Returns:
            NoArvore: No do Sistema locomotor incluindo patas detalhadas.
        """
        # Acopla subarvore de patas e estruturas articulares
        sistema = NoArvore(ItemDiagnostico("Sistema locomotor"))
        sistema.adicionar_filho(FabricaArvoreAnimal._criar_patas())
        art = NoArvore(ItemDiagnostico("Articulações", "LOC-03"))
        sistema.adicionar_filho(art)
        sistema.adicionar_filho(NoArvore(ItemDiagnostico("Coluna", "LOC-04")))
        return sistema

    @staticmethod
    def _criar_patas():
        """Constroi a subarvore detalhada de Patas com dois itens folha.

        Returns:
            NoArvore: No Patas contendo Coxins e Dedos.
        """
        # Demonstra profundidade extra abaixo de Sistema locomotor
        patas = NoArvore(ItemDiagnostico("Patas"))
        patas.adicionar_filho(NoArvore(ItemDiagnostico("Coxins", "LOC-01")))
        patas.adicionar_filho(NoArvore(ItemDiagnostico("Dedos", "LOC-02")))
        return patas
