"""Modulo que define a entidade Tutor com sua lista propria de animais."""

from estruturas.lista.lista_encadeada import ListaEncadeada
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    normalizar_cpf,
    validar_texto_obrigatorio,
)


class Tutor:
    """Representa um tutor e sua relacao ilimitada de animais.

    Attributes:
        nome: Nome completo do tutor.
        cpf: CPF normalizado com 11 digitos.
        telefone: Telefone de contato do tutor.
        animais: ListaEncadeada com os animais pertencentes ao tutor.
    """

    def __init__(self, nome, cpf, telefone):
        """Inicializa um tutor com lista encadeada vazia de animais.

        Args:
            nome: Nome completo do tutor.
            cpf: CPF do tutor (com ou sem mascara).
            telefone: Numero de telefone para contato.

        Raises:
            ValueError: Se nome, CPF ou telefone forem invalidos.
        """
        # Valida dados cadastrais e cria lista propria de animais
        self.nome = validar_texto_obrigatorio(nome, "Nome do tutor")
        self.cpf = normalizar_cpf(cpf)
        self.telefone = validar_texto_obrigatorio(telefone, "Telefone")
        self.animais = ListaEncadeada()

    def adicionar_animal(self, animal):
        """Vincula um novo animal a lista do tutor sem limite fixo.

        Args:
            animal: Instancia de Animal a ser cadastrada.

        Raises:
            ValueError: Se ja existir animal com o mesmo nome no tutor.
        """
        # Evita nomes duplicados sob o mesmo tutor
        if self.buscar_animal(animal.nome) is not None:
            raise ValueError("Tutor ja possui animal com este nome.")
        self.animais.adicionar(animal)

    def buscar_animal(self, nome_animal):
        """Busca um animal deste tutor pelo nome sem diferenciar caixa.

        Args:
            nome_animal: Nome do animal procurado.

        Returns:
            Animal: Instancia encontrada ou None.
        """
        # Normaliza o nome e pesquisa na ListaEncadeada de animais
        chave = normalizar_chave(nome_animal)
        return self.animais.buscar(lambda pet: pet.chave_nome() == chave)

    def remover_animal(self, nome_animal):
        """Remove um animal da lista do tutor pelo nome.

        Args:
            nome_animal: Nome do animal a remover.

        Returns:
            Animal: Animal removido ou None se nao encontrado.
        """
        chave = normalizar_chave(nome_animal)
        return self.animais.remover_por_criterio(
            lambda pet: pet.chave_nome() == chave
        )

    def __str__(self):
        """Retorna representacao legivel do tutor e total de animais.

        Returns:
            str: Resumo com nome, CPF, telefone e quantidade de animais.
        """
        total = len(self.animais)
        return (
            f"{self.nome} | CPF: {self.cpf} | "
            f"Tel: {self.telefone} | Animais: {total}"
        )
