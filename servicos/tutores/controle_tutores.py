"""Modulo de servico para gestao de tutores e seus animais (Lista + Lista)."""

from estruturas.lista.lista_encadeada import ListaEncadeada
from modelos.animal.animal import Animal
from modelos.tutor.tutor import Tutor
from utilitarios.validacao.validador_entrada import normalizar_cpf


class ControleTutores:
    """Gerencia tutores em ListaEncadeada, cada qual com lista de animais.

    Attributes:
        tutores: ListaEncadeada contendo todos os tutores cadastrados.
    """

    def __init__(self):
        """Inicializa o controle com lista vazia de tutores."""
        # Estrutura externa da combinacao Lista + Lista
        self.tutores = ListaEncadeada()

    def cadastrar_tutor(self, nome, cpf, telefone):
        """Cadastra um novo tutor garantindo unicidade de CPF.

        Args:
            nome: Nome completo do tutor.
            cpf: CPF com 11 digitos (com ou sem pontuacao).
            telefone: Telefone de contato.

        Returns:
            Tutor: Instancia cadastrada.

        Raises:
            ValueError: Se ja houver tutor cadastrado com o mesmo CPF.
        """
        # Valida duplicidade de CPF antes de inserir na lista
        cpf_limpo = normalizar_cpf(cpf)
        if self.buscar_tutor_por_cpf(cpf_limpo) is not None:
            raise ValueError("Ja existe tutor cadastrado com este CPF.")
        tutor = Tutor(nome, cpf_limpo, telefone)
        self.tutores.adicionar(tutor)
        return tutor

    def buscar_tutor_por_cpf(self, cpf):
        """Localiza um tutor na lista encadeada pelo CPF.

        Args:
            cpf: CPF do tutor procurado.

        Returns:
            Tutor: Instancia encontrada ou None.
        """
        cpf_limpo = normalizar_cpf(cpf)
        return self.tutores.buscar(lambda tutor: tutor.cpf == cpf_limpo)

    def remover_tutor(self, cpf):
        """Remove um tutor e sua relacao de animais pelo CPF.

        Args:
            cpf: CPF do tutor a ser removido.

        Returns:
            Tutor: Tutor removido da lista.

        Raises:
            ValueError: Se nenhum tutor for encontrado com o CPF.
        """
        # Remove pela chave CPF normalizada
        cpf_limpo = normalizar_cpf(cpf)
        removido = self.tutores.remover_por_criterio(
            lambda tutor: tutor.cpf == cpf_limpo
        )
        if removido is None:
            raise ValueError("Tutor nao encontrado para remocao.")
        return removido

    def cadastrar_animal(self, cpf_tutor, nome, especie, raca, idade):
        """Cadastra um animal na lista de um tutor existente.

        Args:
            cpf_tutor: CPF do tutor responsavel.
            nome: Nome do animal.
            especie: Especie do animal.
            raca: Raca do animal.
            idade: Idade em anos (>= 0).

        Returns:
            Animal: Animal vinculado ao tutor.

        Raises:
            ValueError: Se o tutor nao existir ou dados forem invalidos.
        """
        # Localiza o tutor e adiciona o animal na lista interna dele
        tutor = self._exigir_tutor(cpf_tutor)
        animal = Animal(nome, especie, raca, idade)
        tutor.adicionar_animal(animal)
        return animal

    def buscar_animal(self, cpf_tutor, nome_animal):
        """Busca animal percorrendo a lista de tutores e a lista de animais.

        Args:
            cpf_tutor: CPF do tutor responsavel.
            nome_animal: Nome do animal desejado.

        Returns:
            Animal: Animal encontrado ou None.
        """
        # Operacao da combinacao Lista de tutores + Lista de animais
        tutor = self.buscar_tutor_por_cpf(cpf_tutor)
        if tutor is None:
            return None
        return tutor.buscar_animal(nome_animal)

    def remover_animal(self, cpf_tutor, nome_animal):
        """Remove um animal especifico da lista de um tutor.

        Args:
            cpf_tutor: CPF do tutor responsavel.
            nome_animal: Nome do animal a remover.

        Returns:
            Animal: Animal removido.

        Raises:
            ValueError: Se tutor ou animal nao forem encontrados.
        """
        tutor = self._exigir_tutor(cpf_tutor)
        removido = tutor.remover_animal(nome_animal)
        if removido is None:
            raise ValueError("Animal nao encontrado para este tutor.")
        return removido

    def _exigir_tutor(self, cpf_tutor):
        """Recupera um tutor pelo CPF ou lanca erro se inexistente.

        Args:
            cpf_tutor: CPF a consultar.

        Returns:
            Tutor: Instancia encontrada.

        Raises:
            ValueError: Quando o CPF nao esta cadastrado.
        """
        tutor = self.buscar_tutor_por_cpf(cpf_tutor)
        if tutor is None:
            raise ValueError("Tutor nao encontrado pelo CPF informado.")
        return tutor
