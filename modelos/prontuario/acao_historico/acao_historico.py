"""Modulo que define uma acao registrada na pilha de historico (undo)."""

from utilitarios.data_hora.validador_data import obter_data_hora_atual


class AcaoHistorico:
    """Registra uma alteracao reversivel no prontuario para pilha LIFO.

    Attributes:
        tipo: Tipo da acao ('MEDICAMENTO', 'PROCEDIMENTO', 'DIAGNOSTICO').
        alvo: Referencia ao objeto ou item alterado.
        data_hora: Momento em que a acao foi executada.
    """

    def __init__(self, tipo, alvo):
        """Inicializa uma acao de historico com carimbo temporal.

        Args:
            tipo: Identificador do tipo de alteracao registrada.
            alvo: Objeto afetado que pode ser revertido.
        """
        # Armazena tipo, referencia ao alvo e horario da operacao
        self.tipo = tipo
        self.alvo = alvo
        self.data_hora = obter_data_hora_atual()

    def __str__(self):
        """Retorna descricao resumida da acao registrada na pilha.

        Returns:
            str: Tipo, alvo e carimbo temporal da acao.
        """
        return f"[{self.tipo}] {self.alvo} ({self.data_hora})"
