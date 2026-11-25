"""Modulo de menu interativo para filas de espera e consultorios."""

from interface.entrada.leitor_console import ler_confirmacao, ler_texto
from interface.exibicao.formatador_saida import (
    imprimir_erro,
    imprimir_lista,
    imprimir_sucesso,
    imprimir_titulo,
)


class MenuAtendimento:
    """Fornece interface de console para espera prioritaria e consultorios."""

    def __init__(self, clinica):
        """Inicializa o submenu com referencia a fachada da clinica.

        Args:
            clinica: Instancia de ClinicaVeterinaria.
        """
        self._clinica = clinica

    def executar(self):
        """Executa o laco do submenu de atendimento ate o usuario voltar."""
        while True:
            self._exibir_opcoes()
            opcao = ler_texto("Opcao: ")
            if opcao == "0":
                return
            self._processar_opcao(opcao)

    def _exibir_opcoes(self):
        """Exibe as opcoes do controle de atendimento e salas."""
        imprimir_titulo("CONTROLE DE ATENDIMENTO (FILA + FILA)")
        print("1 - Registrar chegada | 2 - Indicar proximo")
        print("3 - Chamar proximo    | 4 - Ver filas e consultorios")
        print("0 - Voltar")

    def _processar_opcao(self, opcao):
        """Despacha a acao escolhida com tratamento de erros.

        Args:
            opcao: Codigo da opcao digitada.
        """
        try:
            self._despachar(opcao)
        except (ValueError, TypeError) as erro:
            imprimir_erro(erro)

    def _despachar(self, opcao):
        """Executa o comando correspondente a opcao selecionada.

        Args:
            opcao: Codigo da acao.
        """
        if opcao == "1":
            self._registrar_chegada()
        elif opcao == "2":
            self._indicar_proximo()
        else:
            self._despachar_restante(opcao)

    def _despachar_restante(self, opcao):
        """Executa opcoes 3 e 4 ou alerta opcao invalida.

        Args:
            opcao: Codigo da acao.
        """
        if opcao == "3":
            self._chamar_proximo()
        elif opcao == "4":
            self._exibir_situacao()
        else:
            imprimir_erro("Opcao invalida.")

    def _registrar_chegada(self):
        """Registra chegada de um animal na fila normal ou emergencia."""
        cpf = ler_texto("CPF do tutor: ")
        animal = ler_texto("Nome do animal: ")
        queixa = ler_texto("Queixa relatada: ")
        emerg = ler_confirmacao("Caso de emergencia? (s/n): ")
        ficha = self._clinica.registrar_chegada_animal(
            cpf, animal, queixa, emerg
        )
        imprimir_sucesso(f"Na fila: {ficha}")

    def _indicar_proximo(self):
        """Exibe o proximo animal indicado pelas filas prioritarias."""
        proximo = self._clinica.atendimento.indicar_proximo()
        if proximo is None:
            print("Nenhum animal aguardando nas filas.")
            return
        imprimir_sucesso(f"Proximo indicado: {proximo}")

    def _chamar_proximo(self):
        """Chama o proximo animal para sala livre e abre o prontuario."""
        vet = ler_texto("Veterinario responsavel: ")
        prontuario = self._clinica.chamar_proximo_atendimento(vet)
        imprimir_sucesso(f"Atendimento iniciado: {prontuario}")

    def _exibir_situacao(self):
        """Exibe consultorios, fila de emergencia e fila normal."""
        print("\nConsultorios:")
        imprimir_lista(self._clinica.atendimento.consultorios)
        print("\nFila de Emergencia:")
        imprimir_lista(
            self._clinica.atendimento.fila_emergencia, "  Vazia."
        )
        print("\nFila Normal:")
        imprimir_lista(self._clinica.atendimento.fila_normal, "  Vazia.")
