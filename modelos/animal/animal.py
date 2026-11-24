"""Modulo que define a entidade Animal da clinica veterinaria."""

from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_inteiro_nao_negativo,
    validar_texto_obrigatorio,
)


class Animal:
    """Representa um animal cadastrado sob responsabilidade de um tutor.

    Attributes:
        nome: Nome do animal.
        especie: Especie do animal (ex: cao, gato).
        raca: Raca do animal.
        idade: Idade em anos inteiros nao negativos.
    """

    def __init__(self, nome, especie, raca, idade):
        """Inicializa um animal validando seus dados cadastrais.

        Args:
            nome: Nome do animal.
            especie: Especie biologica do animal.
            raca: Raca do animal.
            idade: Idade em anos (>= 0).

        Raises:
            ValueError: Se algum campo obrigatorio for invalido.
        """
        # Valida cada atributo antes de fixar no objeto
        self.nome = validar_texto_obrigatorio(nome, "Nome do animal")
        self.especie = validar_texto_obrigatorio(especie, "Especie")
        self.raca = validar_texto_obrigatorio(raca, "Raca")
        self.idade = validar_inteiro_nao_negativo(idade, "Idade")

    def chave_nome(self):
        """Retorna a chave normalizada do nome para buscas seguras.

        Returns:
            str: Nome do animal em minusculas e sem espacos extras.
        """
        return normalizar_chave(self.nome)

    def __str__(self):
        """Retorna representacao legivel dos dados do animal.

        Returns:
            str: Resumo formatado com nome, especie, raca e idade.
        """
        return (
            f"{self.nome} ({self.especie}, {self.raca}, "
            f"{self.idade} anos)"
        )
