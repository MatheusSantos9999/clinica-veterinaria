"""Modulo de menu interativo para controle de tutores e animais."""

from interface.entrada.leitor_console import ler_inteiro, ler_texto
from interface.exibicao.formatador_saida import (
    imprimir_erro,
    imprimir_lista,
    imprimir_sucesso,
    imprimir_titulo,
)


class MenuTutores:
    """Fornece interface de console para gerenciar tutores e seus animais."""

    def __init__(self, clinica):
        """Inicializa o submenu com referencia a fachada da clinica.

        Args:
            clinica: Instancia de ClinicaVeterinaria.
        """
        self._clinica = clinica

    def executar(self):
        """Executa o laco do submenu de tutores e animais ate voltar."""
        while True:
            self._exibir_opcoes()
            opcao = ler_texto("Opcao: ")
            if opcao == "0":
                return
            self._processar_opcao(opcao)

    def _exibir_opcoes(self):
        """Exibe as opcoes disponiveis no submenu de tutores."""
        imprimir_titulo("CONTROLE DE TUTORES E ANIMAIS")
        print("1 - Cadastrar tutor | 2 - Buscar tutor (CPF)")
        print("3 - Remover tutor   | 4 - Cadastrar animal")
        print("5 - Buscar animal   | 6 - Remover animal")
        print("7 - Listar tutores  | 0 - Voltar")

    def _processar_opcao(self, opcao):
        """Despacha a opcao selecionada tratando erros de validacao.

        Args:
            opcao: Texto digitado pelo usuario.
        """
        try:
            self._despachar(opcao)
        except (ValueError, TypeError) as erro:
            imprimir_erro(erro)

    def _despachar(self, opcao):
        """Chama a acao correspondente a opcao escolhida.

        Args:
            opcao: Codigo da acao no menu.
        """
        if opcao == "1":
            self._cadastrar_tutor()
        elif opcao == "2":
            self._buscar_tutor()
        elif opcao == "3":
            self._remover_tutor()
        else:
            self._despachar_secundarias(opcao)

    def _despachar_secundarias(self, opcao):
        """Despacha opcoes 4 a 7 ou reporta opcao invalida.

        Args:
            opcao: Codigo da acao no menu.
        """
        if opcao == "4":
            self._cadastrar_animal()
        elif opcao == "5":
            self._buscar_animal()
        elif opcao == "6":
            self._remover_animal()
        else:
            self._despachar_terciarias(opcao)

    def _despachar_terciarias(self, opcao):
        """Trata opcao 7 (listar) ou opcao invalida.

        Args:
            opcao: Codigo da acao no menu.
        """
        if opcao == "7":
            imprimir_lista(self._clinica.tutores.tutores)
        else:
            imprimir_erro("Opcao invalida.")

    def _cadastrar_tutor(self):
        """Solicita dados no console e cadastra um novo tutor."""
        nome = ler_texto("Nome do tutor: ")
        cpf = ler_texto("CPF (11 digitos): ")
        telefone = ler_texto("Telefone: ")
        tutor = self._clinica.tutores.cadastrar_tutor(nome, cpf, telefone)
        imprimir_sucesso(f"Tutor cadastrado: {tutor}")

    def _buscar_tutor(self):
        """Busca e exibe um tutor e seus animais a partir do CPF."""
        cpf = ler_texto("CPF do tutor: ")
        tutor = self._clinica.tutores.buscar_tutor_por_cpf(cpf)
        if tutor is None:
            imprimir_erro("Tutor nao encontrado.")
            return
        print(tutor)
        imprimir_lista(tutor.animais, "  Sem animais cadastrados.")

    def _remover_tutor(self):
        """Remove um tutor validando ausencia de atendimentos ativos."""
        cpf = ler_texto("CPF do tutor a remover: ")
        removido = self._clinica.remover_tutor_seguro(cpf)
        imprimir_sucesso(f"Tutor removido: {removido.nome}")

    def _cadastrar_animal(self):
        """Cadastra um novo animal para um tutor ja existente."""
        cpf = ler_texto("CPF do tutor: ")
        nome = ler_texto("Nome do animal: ")
        especie = ler_texto("Especie: ")
        raca = ler_texto("Raca: ")
        idade = ler_inteiro("Idade (anos): ")
        animal = self._clinica.tutores.cadastrar_animal(
            cpf, nome, especie, raca, idade
        )
        imprimir_sucesso(f"Animal cadastrado: {animal}")

    def _buscar_animal(self):
        """Busca um animal combinando CPF do tutor e nome do animal."""
        cpf = ler_texto("CPF do tutor: ")
        nome = ler_texto("Nome do animal: ")
        animal = self._clinica.tutores.buscar_animal(cpf, nome)
        if animal is None:
            imprimir_erro("Animal nao encontrado.")
            return
        imprimir_sucesso(str(animal))

    def _remover_animal(self):
        """Remove um animal verificando que nao esta em atendimento."""
        cpf = ler_texto("CPF do tutor: ")
        nome = ler_texto("Nome do animal: ")
        removido = self._clinica.remover_animal_seguro(cpf, nome)
        imprimir_sucesso(f"Animal removido: {removido.nome}")
