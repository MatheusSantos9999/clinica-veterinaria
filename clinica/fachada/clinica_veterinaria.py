"""Modulo fachada que orquestra todo o ciclo da Clinica Veterinaria."""

from modelos.atendimento.ficha_espera.ficha_espera import FichaEspera
from modelos.prontuario.item_medicamento.item_medicamento import (
    ItemMedicamento,
)
from modelos.prontuario.procedimento.procedimento import Procedimento
from servicos.atendimento.controle_atendimento import ControleAtendimento
from servicos.consumo.controle_consumo import ControleConsumo
from servicos.diagnostico.controle_diagnostico import ControleDiagnostico
from servicos.estoque.controle_estoque import ControleEstoque
from servicos.pagamento.controle_pagamentos import ControlePagamentos
from servicos.prontuario.controle_prontuarios import ControleProntuarios
from servicos.tutores.controle_tutores import ControleTutores
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    validar_texto_obrigatorio,
)


class ClinicaVeterinaria:
    """Fachada principal integrando todos os controles da clinica.

    Attributes:
        tutores: ControleTutores (Lista + Lista).
        atendimento: ControleAtendimento (Fila + Fila + Consultorios).
        diagnostico: ControleDiagnostico (Arvore N-aria pre-ordem).
        estoque: ControleEstoque (Lista + Fila FIFO de lotes).
        prontuarios: ControleProntuarios (Lista abertos + Pilha fechados).
        pagamentos: ControlePagamentos.
        consumo: ControleConsumo integrado ao fechamento.
    """

    def __init__(self, quantidade_consultorios=2):
        """Inicializa todos os servicos e estabelece suas dependencias.

        Args:
            quantidade_consultorios: Total de salas da clinica (> 0).
        """
        # Instancia os controles mantendo separacao de responsabilidades
        self.tutores = ControleTutores()
        self.atendimento = ControleAtendimento(quantidade_consultorios)
        self.diagnostico = ControleDiagnostico()
        self.estoque = ControleEstoque()
        self._iniciar_clinico_financeiro()

    def _iniciar_clinico_financeiro(self):
        """Instancia controles de prontuarios, pagamentos e consumo."""
        self.prontuarios = ControleProntuarios()
        self.pagamentos = ControlePagamentos()
        self.consumo = ControleConsumo(
            self.estoque, self.prontuarios, self.pagamentos
        )

    def registrar_chegada_animal(
        self, cpf_tutor, nome_animal, queixa, emergencia=False
    ):
        """Registra a chegada de um animal cadastrado na fila de espera.

        Args:
            cpf_tutor: CPF do tutor cadastrado.
            nome_animal: Nome do animal pertencente ao tutor.
            queixa: Sintoma ou ocorrencia relatada.
            emergencia: True para prioridade de emergencia.

        Returns:
            FichaEspera: Ficha inserida na fila correspondente.

        Raises:
            ValueError: Se tutor ou animal nao estiverem cadastrados.
        """
        # Valida cadastro previo antes de enfileirar para atendimento
        ficha = self._montar_ficha(cpf_tutor, nome_animal, queixa, emergencia)
        self.atendimento.registrar_chegada(ficha)
        return ficha

    def _montar_ficha(self, cpf_tutor, nome_animal, queixa, emergencia):
        """Valida tutor/animal cadastrados e instancia FichaEspera.

        Args:
            cpf_tutor: CPF do tutor.
            nome_animal: Nome do animal.
            queixa: Queixa clinica.
            emergencia: Sinalizador de emergencia.

        Returns:
            FichaEspera: Ficha pronta para enfileiramento.
        """
        tutor = self.tutores.buscar_tutor_por_cpf(cpf_tutor)
        animal = self.tutores.buscar_animal(cpf_tutor, nome_animal)
        if tutor is None or animal is None:
            raise ValueError("Tutor ou animal nao cadastrado na clinica.")
        return FichaEspera(
            animal.nome, tutor.nome, tutor.cpf, queixa, emergencia
        )

    def chamar_proximo_atendimento(self, veterinario):
        """Chama o proximo animal para um consultorio livre e abre prontuario.

        Args:
            veterinario: Nome do veterinario que assumira o caso.

        Returns:
            Prontuario: Prontuario recem-aberto para o atendimento.
        """
        # Valida veterinario antes de desenfileirar para manter consistencia
        vet = validar_texto_obrigatorio(veterinario, "Veterinario")
        numero = self.prontuarios.proximo_numero()
        sala = self.atendimento.chamar_proximo(numero)
        return self.prontuarios.abrir_prontuario(
            sala.ficha_atual, vet, sala.numero
        )

    def marcar_diagnostico_alterado(self, numero_prontuario, identificador):
        """Marca uma estrutura da arvore do prontuario como Alterado.

        Args:
            numero_prontuario: Numero do prontuario aberto.
            identificador: Codigo folha ou nome do sistema/orgao.

        Returns:
            ItemDiagnostico: Estrutura marcada como Alterado.
        """
        prontuario = self.prontuarios.exigir_aberto(numero_prontuario)
        return self.diagnostico.marcar_alterado(prontuario, identificador)

    def adicionar_medicamento_prontuario(
        self, numero, codigo, quantidade, data_ref=None
    ):
        """Prescreve medicamento validando cadastro e saldo valido no estoque.

        Args:
            numero: Numero do prontuario aberto.
            codigo: Codigo do produto no estoque.
            quantidade: Unidades a prescrever (> 0).
            data_ref: Data opcional para checagem de validade.

        Returns:
            ItemMedicamento: Item adicionado ao prontuario.

        Raises:
            ValueError: Se produto inexistente ou saldo insuficiente.
        """
        # Valida saldo acumulado e inclui item prescrito no prontuario
        item = self._montar_item_med(numero, codigo, quantidade, data_ref)
        self.prontuarios.adicionar_medicamento(numero, item)
        return item

    def _montar_item_med(self, numero, codigo, quantidade, data_ref):
        """Valida prontuario/estoque e instancia ItemMedicamento.

        Args:
            numero: Numero do prontuario aberto.
            codigo: Codigo do produto no estoque.
            quantidade: Unidades prescritas (> 0).
            data_ref: Data opcional de validade.

        Returns:
            ItemMedicamento: Item pronto para inclusao.
        """
        pront = self.prontuarios.exigir_aberto(numero)
        prod = self._validar_produto_para_prescricao(
            pront, codigo, quantidade, data_ref
        )
        preco = prod.preco_venda_atual(data_ref)
        return ItemMedicamento(prod.codigo, prod.nome, quantidade, preco)

    def _validar_produto_para_prescricao(
        self, prontuario, codigo, quantidade, data_ref
    ):
        """Garante existencia do produto e saldo total para a prescricao.

        Args:
            prontuario: Prontuario aberto.
            codigo: Codigo do produto.
            quantidade: Nova quantidade solicitada.
            data_ref: Data de referencia de validade.

        Returns:
            ProdutoEstoque: Produto encontrado e disponivel.
        """
        produto = self.estoque.buscar_produto(codigo)
        if produto is None:
            raise ValueError(f"Produto '{codigo}' nao existe no estoque.")
        total = self._somar_no_prontuario(prontuario, codigo) + quantidade
        if not self.estoque.verificar_disponibilidade(codigo, total, data_ref):
            raise ValueError(f"Estoque valido insuficiente para [{codigo}].")
        return produto

    def _somar_no_prontuario(self, prontuario, codigo):
        """Soma quantidade ja prescrita de um produto no prontuario.

        Args:
            prontuario: Prontuario inspecionado.
            codigo: Codigo do produto.

        Returns:
            int: Quantidade ja prescrita deste codigo.
        """
        chave = normalizar_chave(codigo)
        soma = 0
        for item in prontuario.medicamentos:
            if item.chave_codigo() == chave:
                soma += item.quantidade
        return soma

    def adicionar_procedimento_prontuario(
        self, numero_prontuario, nome, valor, descricao=""
    ):
        """Adiciona um procedimento clinico a um prontuario aberto.

        Args:
            numero_prontuario: Numero do prontuario aberto.
            nome: Nome do procedimento.
            valor: Valor cobrado (>= 0).
            descricao: Detalhe opcional.

        Returns:
            Procedimento: Procedimento adicionado.
        """
        proc = Procedimento(nome, valor, descricao)
        self.prontuarios.adicionar_procedimento(numero_prontuario, proc)
        return proc

    def fechar_atendimento(self, numero, dados_pagamento, data_ref=None):
        """Conclui fechamento, baixa estoque, paga, audita e libera sala.

        Args:
            numero: Numero do prontuario com alta concedida.
            dados_pagamento: DadosPagamento validados.
            data_ref: Data opcional para validar vencimentos.

        Returns:
            RegistroConsumo: Registro completo gerado no encerramento.
        """
        # Executa fechamento atomico e libera o consultorio ocupado
        pront = self.prontuarios.exigir_aberto(numero)
        reg = self.consumo.fechar_e_consumir(numero, dados_pagamento, data_ref)
        self.atendimento.liberar_consultorio(pront.numero_consultorio)
        return reg

    def remover_tutor_seguro(self, cpf):
        """Remove tutor somente se nenhum de seus animais estiver ativo.

        Args:
            cpf: CPF do tutor a remover.

        Returns:
            Tutor: Tutor removido.

        Raises:
            ValueError: Se algum animal do tutor estiver em fila ou sala.
        """
        # Protege integridade de atendimentos em andamento
        tutor = self.tutores.buscar_tutor_por_cpf(cpf)
        if tutor is None:
            raise ValueError("Tutor nao encontrado para remocao.")
        self._garantir_tutor_inativo(tutor)
        return self.tutores.remover_tutor(cpf)

    def _garantir_tutor_inativo(self, tutor):
        """Verifica se algum animal do tutor esta ativo na clinica.

        Args:
            tutor: Tutor cuja lista de animais sera conferida.

        Raises:
            ValueError: Se houver animal em fila ou prontuario aberto.
        """
        for animal in tutor.animais:
            self._garantir_animal_inativo(tutor.cpf, animal.nome)

    def remover_animal_seguro(self, cpf, nome_animal):
        """Remove animal somente se nao estiver em espera ou atendimento.

        Args:
            cpf: CPF do tutor.
            nome_animal: Nome do animal a remover.

        Returns:
            Animal: Animal removido.
        """
        self._garantir_animal_inativo(cpf, nome_animal)
        return self.tutores.remover_animal(cpf, nome_animal)

    def _garantir_animal_inativo(self, cpf, nome_animal):
        """Bloqueia remocao de animal com fila ou prontuario em aberto.

        Args:
            cpf: CPF do tutor.
            nome_animal: Nome do animal.

        Raises:
            ValueError: Se o animal estiver em espera ou atendimento.
        """
        em_fila = self.atendimento.animal_ativo(cpf, nome_animal)
        em_pront = self.prontuarios.animal_com_prontuario_aberto(
            cpf, nome_animal
        )
        if em_fila or em_pront:
            raise ValueError("Nao e possivel remover animal em atendimento.")
