"""Modulo que define a ficha de espera para controle de atendimento."""

from utilitarios.data_hora.validador_data import obter_data_hora_atual
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    normalizar_cpf,
    validar_texto_obrigatorio,
)


class FichaEspera:
    """Representa um animal aguardando vaga em um consultorio.

    Attributes:
        nome_animal: Nome do animal em espera.
        nome_tutor: Nome do tutor responsavel.
        cpf_tutor: CPF normalizado do tutor.
        queixa: Queixa clinica relatada na chegada.
        emergencia: Indica se o caso exige prioridade.
        data_hora_chegada: Carimbo de data e hora da chegada.
    """

    def __init__(
        self, nome_animal, nome_tutor, cpf_tutor,
        queixa, emergencia=False, data_hora_chegada=None,
    ):
        """Inicializa a ficha de espera validando os campos informados.

        Args:
            nome_animal: Nome do animal.
            nome_tutor: Nome do tutor.
            cpf_tutor: CPF do tutor.
            queixa: Sintoma ou ocorrencia relatada.
            emergencia: True para emergencia, False para atendimento normal.
            data_hora_chegada: Data/hora opcional; padrao usa horario atual.
        """
        # Delega validacao dos grupos de campos para manter concisao
        self._definir_identificacao(nome_animal, nome_tutor, cpf_tutor)
        self._definir_triagem(queixa, emergencia, data_hora_chegada)

    def _definir_identificacao(self, nome_animal, nome_tutor, cpf_tutor):
        """Valida e atribui identificacao do animal e do tutor.

        Args:
            nome_animal: Nome do animal.
            nome_tutor: Nome do tutor.
            cpf_tutor: CPF do tutor.
        """
        self.nome_animal = validar_texto_obrigatorio(
            nome_animal, "Nome do animal"
        )
        self.nome_tutor = validar_texto_obrigatorio(
            nome_tutor, "Nome do tutor"
        )
        self.cpf_tutor = normalizar_cpf(cpf_tutor)

    def _definir_triagem(self, queixa, emergencia, data_hora_chegada):
        """Valida e atribui queixa, prioridade e horario de chegada.

        Args:
            queixa: Queixa relatada.
            emergencia: Sinalizador booleano de emergencia.
            data_hora_chegada: Horario de chegada ou None.
        """
        # Garante tipo booleano explicito para prioridade
        if not isinstance(emergencia, bool):
            raise ValueError("Emergencia deve ser booleano.")
        self.queixa = validar_texto_obrigatorio(queixa, "Queixa")
        self.emergencia = emergencia
        self.data_hora_chegada = self._resolver_chegada(data_hora_chegada)

    def _resolver_chegada(self, data_hora):
        """Usa horario atual ou valida texto de data/hora informado.

        Args:
            data_hora: Carimbo opcional ou None.

        Returns:
            str: Data e hora de chegada validada.
        """
        if data_hora is None:
            return obter_data_hora_atual()
        return validar_texto_obrigatorio(data_hora, "Data/hora")

    def chave_animal(self):
        """Retorna chave composta normalizada para identificar o animal.

        Returns:
            str: Combinacao de CPF do tutor e nome do animal.
        """
        return f"{self.cpf_tutor}:{normalizar_chave(self.nome_animal)}"

    def __str__(self):
        """Retorna resumo legivel da ficha de espera.

        Returns:
            str: Texto contendo prioridade, animal, tutor, hora e queixa.
        """
        nivel = "EMERGENCIA" if self.emergencia else "NORMAL"
        return (
            f"[{nivel}] {self.nome_animal} (Tutor: {self.nome_tutor}) "
            f"- Chegada: {self.data_hora_chegada} | Queixa: {self.queixa}"
        )
