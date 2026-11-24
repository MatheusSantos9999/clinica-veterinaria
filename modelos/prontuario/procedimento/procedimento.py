"""Modulo que representa um procedimento realizado no atendimento."""

from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_texto_obrigatorio,
    validar_valor_nao_negativo,
)


class Procedimento:
    """Representa um procedimento clinico (consulta, exame, curativo, etc.).

    Attributes:
        nome: Nome do procedimento realizado.
        valor: Valor cobrado pelo procedimento.
        descricao: Observacao opcional sobre o procedimento.
    """

    def __init__(self, nome, valor, descricao=""):
        """Inicializa um procedimento validando nome e preco.

        Args:
            nome: Nome do procedimento (ex: Consulta, Curativo, Vacina).
            valor: Preco cobrado (>= 0).
            descricao: Detalhes adicionais opcionais.
        """
        # Valida nome, valor e normaliza descricao opcional
        self.nome = validar_texto_obrigatorio(nome, "Nome do procedimento")
        self.valor = validar_valor_nao_negativo(valor, "Valor procedimento")
        texto = descricao.strip() if isinstance(descricao, str) else ""
        self.descricao = texto

    def chave_nome(self):
        """Retorna chave normalizada do nome para localizacao segura.

        Returns:
            str: Nome do procedimento em minusculas.
        """
        return normalizar_chave(self.nome)

    def __str__(self):
        """Retorna representacao legivel do procedimento e seu preco.

        Returns:
            str: Nome, descricao (se houver) e valor formatado.
        """
        detalhe = f" - {self.descricao}" if self.descricao else ""
        return f"{self.nome}{detalhe} (R$ {self.valor:.2f})"
