"""Modulo que define o item de diagnostico armazenado em cada no."""

from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_texto_obrigatorio,
)

ESTADO_SAUDAVEL = "Saudável"
ESTADO_ALTERADO = "Alterado"


class ItemDiagnostico:
    """Representa um sistema, orgao ou estrutura anatomica do animal.

    Attributes:
        nome: Nome do sistema, orgao ou estrutura.
        codigo: Codigo de identificacao (presente em nos folha) ou None.
        estado: Estado clinico ('Saudável' ou 'Alterado').
    """

    def __init__(self, nome, codigo=None):
        """Inicializa o item anatomico no estado saudavel.

        Args:
            nome: Nome da estrutura anatomica.
            codigo: Codigo unico para itens finais da hierarquia ou None.
        """
        # Todo item inicia saudavel ate alteracao no diagnostico
        self.nome = validar_texto_obrigatorio(nome, "Nome da estrutura")
        self.codigo = (
            None
            if codigo is None
            else validar_texto_obrigatorio(codigo, "Codigo do item")
        )
        self.estado = ESTADO_SAUDAVEL

    def marcar_alterado(self):
        """Altera o estado clinico desta estrutura para Alterado."""
        self.estado = ESTADO_ALTERADO

    def marcar_saudavel(self):
        """Restaura o estado clinico desta estrutura para Saudavel."""
        self.estado = ESTADO_SAUDAVEL

    def esta_alterado(self):
        """Indica se o item esta marcado como Alterado.

        Returns:
            bool: True se o estado for Alterado, False caso contrario.
        """
        return self.estado == ESTADO_ALTERADO

    def corresponde(self, identificador):
        """Verifica se o item corresponde a um codigo ou nome informado.

        Args:
            identificador: Codigo ou nome procurado (sem diferenciar caixa).

        Returns:
            bool: True se houver correspondencia exata normalizada.
        """
        # Permite localizar tanto por codigo quanto por nome
        chave = normalizar_chave(identificador)
        if self.codigo is not None and normalizar_chave(self.codigo) == chave:
            return True
        return normalizar_chave(self.nome) == chave

    def __str__(self):
        """Retorna representacao formatada do item anatomico.

        Returns:
            str: Nome, codigo (se folha) e estado clinico atual.
        """
        trecho_codigo = f" [{self.codigo}]" if self.codigo else ""
        return f"{self.nome}{trecho_codigo} - {self.estado}"
