"""Modulo que consolida o consumo de medicamentos por tutor e animal."""

from utilitarios.data_hora.validador_data import obter_data_hora_atual


class RegistroConsumo:
    """Relaciona tutor, animal, prontuario, baixas FIFO e pagamento.

    Attributes:
        numero_prontuario: Numero do prontuario encerrado.
        nome_tutor: Nome do tutor responsavel.
        cpf_tutor: CPF normalizado do tutor.
        nome_animal: Nome do animal que recebeu os medicamentos.
        itens_consumidos: ListaEncadeada de ItemConsumido.
        pagamento: Instancia de Pagamento vinculada ao fechamento.
        data_hora: Momento da consolidacao do consumo.
    """

    def __init__(self, prontuario, itens_consumidos, pagamento):
        """Cria um registro consolidado de consumo e faturamento.

        Args:
            prontuario: Prontuario que acabou de ser fechado.
            itens_consumidos: ListaEncadeada com baixas FIFO executadas.
            pagamento: Pagamento registrado para este prontuario.
        """
        # Vincula tutor, animal, itens baixados e pagamento
        self.numero_prontuario = prontuario.numero
        self.nome_tutor = prontuario.nome_tutor
        self.cpf_tutor = prontuario.cpf_tutor
        self.nome_animal = prontuario.nome_animal
        self.itens_consumidos = itens_consumidos
        self.pagamento = pagamento
        self.data_hora = obter_data_hora_atual()

    def total_unidades_consumidas(self):
        """Soma todas as unidades de medicamentos consumidas no atendimento.

        Returns:
            int: Soma das quantidades baixadas de todos os lotes.
        """
        total = 0
        for item in self.itens_consumidos:
            total += item.quantidade
        return total

    def __str__(self):
        """Retorna resumo legivel do consumo consolidado do atendimento.

        Returns:
            str: Prontuario, tutor, animal, itens e valor pago.
        """
        return (
            f"Consumo Prontuario #{self.numero_prontuario} | Tutor: "
            f"{self.nome_tutor} ({self.cpf_tutor}) | Animal: "
            f"{self.nome_animal} | Unidades: "
            f"{self.total_unidades_consumidas()} | "
            f"Pago: R$ {self.pagamento.valor_total:.2f}"
        )
