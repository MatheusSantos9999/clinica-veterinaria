"""Modulo que define a entidade Pagamento de fechamento do prontuario."""

from utilitarios.data_hora.validador_data import obter_data_hora_atual
from utilitarios.validacao.validador_entrada import (
    validar_inteiro_positivo,
    validar_valor_nao_negativo,
)


class Pagamento:
    """Representa o comprovante de pagamento realizado no fechamento.

    Attributes:
        numero_prontuario: Numero do prontuario quitado.
        nome_pagador: Nome de quem efetuou o pagamento.
        forma_pagamento: PIX, DINHEIRO, CARTAO_AVISTA ou CARTAO_PARCELADO.
        numero_parcelas: Numero de parcelas contratadas.
        valor_medicamentos: Total gasto em medicamentos e vacinas.
        valor_procedimentos: Total gasto em procedimentos clinicos.
        valor_total: Soma final paga.
        data_hora_pagamento: Carimbo temporal do pagamento.
        nome_animal: Nome do animal referente ao prontuario.
        cpf_tutor: CPF do tutor referente ao prontuario.
    """

    def __init__(
        self, prontuario, dados_pagamento, valor_medicamentos,
        valor_procedimentos,
    ):
        """Inicializa o registro de pagamento com os totais apurados.

        Args:
            prontuario: Instancia de Prontuario sendo quitada.
            dados_pagamento: Instancia validada de DadosPagamento.
            valor_medicamentos: Total dos medicamentos consumidos.
            valor_procedimentos: Total dos procedimentos realizados.
        """
        # Associa identificadores do prontuario e valores financeiros
        self._definir_origem(prontuario, dados_pagamento)
        self._definir_valores(valor_medicamentos, valor_procedimentos)
        self.data_hora_pagamento = obter_data_hora_atual()

    def _definir_origem(self, prontuario, dados):
        """Atribui referencia ao prontuario e detalhes da forma escolhida.

        Args:
            prontuario: Prontuario associado ao pagamento.
            dados: DadosPagamento validados.
        """
        self.numero_prontuario = validar_inteiro_positivo(
            prontuario.numero, "Numero prontuario"
        )
        self.nome_animal = prontuario.nome_animal
        self.cpf_tutor = prontuario.cpf_tutor
        self.nome_pagador = dados.nome_pagador
        self.forma_pagamento = dados.forma_pagamento
        self.numero_parcelas = dados.numero_parcelas

    def _definir_valores(self, valor_medicamentos, valor_procedimentos):
        """Valida subtotais e calcula o valor total pago.

        Args:
            valor_medicamentos: Subtotal de medicamentos.
            valor_procedimentos: Subtotal de procedimentos.
        """
        # Arredonda valores monetarios para duas casas decimais
        meds = validar_valor_nao_negativo(valor_medicamentos, "Medicamentos")
        procs = validar_valor_nao_negativo(
            valor_procedimentos, "Procedimentos"
        )
        self.valor_medicamentos = round(meds, 2)
        self.valor_procedimentos = round(procs, 2)
        soma = self.valor_medicamentos + self.valor_procedimentos
        self.valor_total = round(soma, 2)

    def valor_por_parcela(self):
        """Calcula o valor aproximado de cada parcela paga.

        Returns:
            float: Valor total dividido pelo numero de parcelas.
        """
        return round(self.valor_total / self.numero_parcelas, 2)

    def __str__(self):
        """Retorna resumo legivel do comprovante de pagamento.

        Returns:
            str: Resumo com prontuario, pagador, forma, parcelas e totais.
        """
        return (
            f"Pagamento Prontuario #{self.numero_prontuario} | Pagador: "
            f"{self.nome_pagador} | {self.forma_pagamento} "
            f"({self.numero_parcelas}x) | "
            f"Meds: R$ {self.valor_medicamentos:.2f} "
            f"| Procs: R$ {self.valor_procedimentos:.2f} | "
            f"Total: R$ {self.valor_total:.2f} ({self.data_hora_pagamento})"
        )
