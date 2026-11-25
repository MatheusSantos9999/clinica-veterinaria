"""Servico que integra fechamento, baixa FIFO, pagamento e consumo."""

from estruturas.lista.lista_encadeada import ListaEncadeada
from modelos.consumo.registro_consumo.registro_consumo import RegistroConsumo
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    normalizar_cpf,
)


class ControleConsumo:
    """Coordena baixa de estoque, pagamento e auditoria de consumo por animal.

    Attributes:
        registros: ListaEncadeada de RegistroConsumo concluidos.
    """

    def __init__(self, estoque, prontuarios, pagamentos):
        """Inicializa o controle com referencias aos servicos integrados.

        Args:
            estoque: Instancia de ControleEstoque.
            prontuarios: Instancia de ControleProntuarios.
            pagamentos: Instancia de ControlePagamentos.
        """
        # Integra estoque, prontuarios e pagamentos sem acoplar estruturas
        self._estoque = estoque
        self._prontuarios = prontuarios
        self._pagamentos = pagamentos
        self.registros = ListaEncadeada()

    def fechar_e_consumir(
        self, numero_prontuario, dados_pagamento, data_referencia=None
    ):
        """Executa fechamento atomico com baixa FIFO, pagamento e consumo.

        Args:
            numero_prontuario: Numero do prontuario com alta concedida.
            dados_pagamento: Instancia validada de DadosPagamento.
            data_referencia: Data opcional para validar vencimentos.

        Returns:
            RegistroConsumo: Consolidacao do consumo e pagamento efetuado.
        """
        # Pre-valida todas as regras antes de alterar estoque ou prontuario
        prontuario = self._pre_validar(
            numero_prontuario, dados_pagamento, data_referencia
        )
        itens = self._baixar_medicamentos(prontuario, data_referencia)
        pag = self._registrar_pagamento(prontuario, dados_pagamento, itens)
        return self._concluir_fechamento(prontuario, itens, pag)

    def _pre_validar(self, numero, dados_pagamento, data_ref):
        """Valida prontuario com alta, pagamento e estoque total atomico.

        Args:
            numero: Numero do prontuario.
            dados_pagamento: Dados do pagamento.
            data_ref: Data de referencia de validade.

        Returns:
            Prontuario: Prontuario validado e pronto para fechamento.
        """
        if not isinstance(dados_pagamento, DadosPagamento):
            raise TypeError("dados_pagamento deve ser DadosPagamento.")
        prontuario = self._prontuarios.exigir_aberto(numero)
        prontuario.validar_para_fechamento()
        self._estoque.descartar_vencidos(data_ref)
        self._validar_estoque_consolidado(prontuario, data_ref)
        return prontuario

    def _validar_estoque_consolidado(self, prontuario, data_ref):
        """Garante estoque suficiente mesmo com itens repetidos no prontuario.

        Args:
            prontuario: Prontuario contendo os medicamentos prescritos.
            data_ref: Data de referencia para checar validade.

        Raises:
            ValueError: Se o saldo valido total for insuficiente.
        """
        # Soma demanda total por codigo para evitar baixa parcial
        for item in prontuario.medicamentos:
            total = self._somar_demanda(prontuario, item.codigo_produto)
            disponivel = self._estoque.verificar_disponibilidade(
                item.codigo_produto, total, data_ref
            )
            if not disponivel:
                msg = f"Estoque insuficiente para [{item.codigo_produto}]."
                raise ValueError(msg)

    def _somar_demanda(self, prontuario, codigo_produto):
        """Soma todas as quantidades prescritas de um mesmo codigo.

        Args:
            prontuario: Prontuario inspecionado.
            codigo_produto: Codigo do produto somado.

        Returns:
            int: Quantidade total demandada deste produto.
        """
        chave = normalizar_chave(codigo_produto)
        soma = 0
        for item in prontuario.medicamentos:
            if item.chave_codigo() == chave:
                soma += item.quantidade
        return soma

    def _baixar_medicamentos(self, prontuario, data_ref):
        """Realiza a baixa FIFO de cada medicamento prescrito no prontuario.

        Args:
            prontuario: Prontuario cujos medicamentos serao baixados.
            data_ref: Data de referencia de validade.

        Returns:
            ListaEncadeada: Todos os ItemConsumido gerados nas baixas.
        """
        # Acumula cada parcela de lote consumida em ListaEncadeada propria
        todos_itens = ListaEncadeada()
        for med in prontuario.medicamentos:
            baixas = self._estoque.baixar_estoque(
                med.codigo_produto, med.quantidade, data_ref
            )
            for item in baixas:
                todos_itens.adicionar(item)
        return todos_itens

    def _registrar_pagamento(self, prontuario, dados_pagamento, itens):
        """Calcula valores reais da baixa e registra o pagamento.

        Args:
            prontuario: Prontuario sendo encerrado.
            dados_pagamento: DadosPagamento validados.
            itens: ListaEncadeada de ItemConsumido.

        Returns:
            Pagamento: Pagamento registrado no controle de pagamentos.
        """
        valor_meds = self._somar_venda_itens(itens)
        valor_procs = prontuario.calcular_total_procedimentos()
        return self._pagamentos.registrar_pagamento(
            prontuario, dados_pagamento, valor_meds, valor_procs
        )

    def _somar_venda_itens(self, itens):
        """Soma o valor real de venda de todos os lotes consumidos.

        Args:
            itens: ListaEncadeada de ItemConsumido.

        Returns:
            float: Total efetivo de medicamentos baseado nos lotes FIFO.
        """
        total = 0.0
        for item in itens:
            total += item.subtotal_venda()
        return round(total, 2)

    def _concluir_fechamento(self, prontuario, itens, pagamento):
        """Encerra o prontuario e registra a auditoria de consumo.

        Args:
            prontuario: Prontuario quitado.
            itens: ListaEncadeada de ItemConsumido.
            pagamento: Pagamento efetuado.

        Returns:
            RegistroConsumo: Registro salvo no historico de consumo.
        """
        self._prontuarios.encerrar_prontuario(prontuario.numero)
        registro = RegistroConsumo(prontuario, itens, pagamento)
        self.registros.adicionar(registro)
        return registro

    def consultar_por_tutor(self, cpf_tutor):
        """Retorna todos os registros de consumo de um tutor pelo CPF.

        Args:
            cpf_tutor: CPF do tutor consultado.

        Returns:
            ListaEncadeada: Registros de consumo do tutor.
        """
        cpf = normalizar_cpf(cpf_tutor)
        return self.registros.filtrar(lambda reg: reg.cpf_tutor == cpf)

    def consultar_por_animal(self, cpf_tutor, nome_animal):
        """Retorna registros de consumo de um animal especifico.

        Args:
            cpf_tutor: CPF do tutor responsavel.
            nome_animal: Nome do animal consultado.

        Returns:
            ListaEncadeada: Registros de consumo do animal.
        """
        cpf = normalizar_cpf(cpf_tutor)
        chave = normalizar_chave(nome_animal)
        return self.registros.filtrar(
            lambda r: (
                r.cpf_tutor == cpf
                and normalizar_chave(r.nome_animal) == chave
            )
        )
