"""Modulo que define a entidade Prontuario de Atendimento veterinario."""

from estruturas.lista.lista_encadeada import ListaEncadeada
from estruturas.pilha.pilha_encadeada import PilhaEncadeada
from modelos.diagnostico.fabrica_arvore.fabrica_arvore_animal import (
    FabricaArvoreAnimal,
)
from modelos.prontuario.acao_historico.acao_historico import AcaoHistorico
from utilitarios.data_hora.validador_data import obter_data_hora_atual
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    normalizar_cpf,
    validar_inteiro_positivo,
    validar_texto_obrigatorio,
)


class Prontuario:
    """Gerencia os dados e o ciclo de vida de um atendimento clinico.

    Attributes:
        numero: Numero sequencial unico do prontuario.
        nome_animal: Nome do animal atendido.
        nome_tutor: Nome do tutor responsavel.
        cpf_tutor: CPF normalizado do tutor.
        veterinario: Nome do veterinario responsavel.
        numero_consultorio: Consultorio em que ocorre o atendimento.
        data_hora_abertura: Carimbo de abertura do prontuario.
        arvore_diagnostico: ArvoreNAria propria do diagnostico.
        medicamentos: ListaEncadeada de ItemMedicamento.
        procedimentos: ListaEncadeada de Procedimento.
        historico_acoes: PilhaEncadeada para desfazer alteracoes.
        alta_concedida: True quando o animal recebeu alta.
        fechado: True quando o prontuario foi encerrado.
        data_hora_fechamento: Carimbo do fechamento ou None.
    """

    def __init__(
        self, numero, ficha_espera, veterinario, numero_consultorio
    ):
        """Inicializa um prontuario aberto para o animal chamado.

        Args:
            numero: Numero inteiro unico do prontuario.
            ficha_espera: FichaEspera que originou o atendimento.
            veterinario: Nome do veterinario responsavel.
            numero_consultorio: Numero do consultorio ocupado.
        """
        # Separa inicializacao de metadados e estruturas proprias
        self._definir_cabecalho(
            numero, ficha_espera, veterinario, numero_consultorio
        )
        self._inicializar_estruturas()

    def _definir_cabecalho(
        self, numero, ficha, veterinario, numero_consultorio
    ):
        """Valida e registra cabecalho de identificacao do prontuario.

        Args:
            numero: Numero do prontuario.
            ficha: FichaEspera do animal.
            veterinario: Nome do veterinario responsavel.
            numero_consultorio: Numero do consultorio.
        """
        self._definir_paciente(ficha)
        self._definir_atendimento(numero, veterinario, numero_consultorio)

    def _definir_paciente(self, ficha):
        """Extrai e valida nome do animal, tutor e CPF da ficha.

        Args:
            ficha: FichaEspera de origem.
        """
        self.nome_animal = validar_texto_obrigatorio(
            ficha.nome_animal, "Nome do animal"
        )
        self.nome_tutor = validar_texto_obrigatorio(
            ficha.nome_tutor, "Nome do tutor"
        )
        self.cpf_tutor = normalizar_cpf(ficha.cpf_tutor)

    def _definir_atendimento(self, numero, veterinario, numero_consultorio):
        """Valida numero do prontuario, veterinario e sala ocupada.

        Args:
            numero: Numero do prontuario.
            veterinario: Nome do veterinario responsavel.
            numero_consultorio: Numero da sala ocupada.
        """
        self.numero = validar_inteiro_positivo(numero, "Numero prontuario")
        self.veterinario = validar_texto_obrigatorio(
            veterinario, "Veterinario"
        )
        self.numero_consultorio = validar_inteiro_positivo(
            numero_consultorio, "Consultorio"
        )

    def _inicializar_estruturas(self):
        """Instancia arvore, listas, pilha de desfazer e estados iniciais."""
        # Cada prontuario possui arvore, listas e pilha independentes
        self.data_hora_abertura = obter_data_hora_atual()
        self.arvore_diagnostico = FabricaArvoreAnimal.criar_padrao()
        self.medicamentos = ListaEncadeada()
        self.procedimentos = ListaEncadeada()
        self.historico_acoes = PilhaEncadeada()
        self.alta_concedida = False
        self.fechado = False
        self.data_hora_fechamento = None

    def exigir_aberto(self):
        """Garante que o prontuario ainda pode sofrer alteracoes.

        Raises:
            ValueError: Se o prontuario ja estiver fechado.
        """
        if self.fechado:
            raise ValueError("Prontuario fechado nao permite alteracoes.")

    def adicionar_medicamento(self, item_medicamento):
        """Adiciona um medicamento ao prontuario e empilha no historico.

        Args:
            item_medicamento: Instancia de ItemMedicamento.
        """
        self.exigir_aberto()
        self.medicamentos.adicionar(item_medicamento)
        self.historico_acoes.empilhar(
            AcaoHistorico("MEDICAMENTO", item_medicamento)
        )

    def remover_medicamento(self, codigo_produto):
        """Remove a primeira prescricao correspondente ao codigo informado.

        Args:
            codigo_produto: Codigo do produto a remover.

        Returns:
            ItemMedicamento: Item removido ou None se nao encontrado.
        """
        self.exigir_aberto()
        chave = normalizar_chave(codigo_produto)
        return self.medicamentos.remover_por_criterio(
            lambda item: item.chave_codigo() == chave
        )

    def adicionar_procedimento(self, procedimento):
        """Adiciona um procedimento ao prontuario e empilha no historico.

        Args:
            procedimento: Instancia de Procedimento.
        """
        self.exigir_aberto()
        self.procedimentos.adicionar(procedimento)
        self.historico_acoes.empilhar(
            AcaoHistorico("PROCEDIMENTO", procedimento)
        )

    def remover_procedimento(self, nome_procedimento):
        """Remove o primeiro procedimento com o nome informado.

        Args:
            nome_procedimento: Nome do procedimento a retirar.

        Returns:
            Procedimento: Procedimento removido ou None.
        """
        self.exigir_aberto()
        chave = normalizar_chave(nome_procedimento)
        return self.procedimentos.remover_por_criterio(
            lambda proc: proc.chave_nome() == chave
        )

    def registrar_diagnostico_alterado(self, item_diagnostico):
        """Empilha a marcacao de um no de diagnostico para eventual undo.

        Args:
            item_diagnostico: ItemDiagnostico marcado como alterado.
        """
        self.exigir_aberto()
        self.historico_acoes.empilhar(
            AcaoHistorico("DIAGNOSTICO", item_diagnostico)
        )

    def desfazer_ultima_acao(self):
        """Reverte a ultima inclusao ou marcacao usando a pilha LIFO.

        Returns:
            AcaoHistorico: Acao desfeita ou None se historico vazio.
        """
        # Retira o topo da pilha e aplica reversao conforme o tipo
        self.exigir_aberto()
        if self.historico_acoes.esta_vazia():
            return None
        acao = self.historico_acoes.desempilhar()
        self._reverter_acao(acao)
        return acao

    def _reverter_acao(self, acao):
        """Aplica a operacao inversa correspondente ao tipo da acao.

        Args:
            acao: AcaoHistorico desempilhada.
        """
        if acao.tipo == "MEDICAMENTO":
            self.medicamentos.remover_elemento(acao.alvo)
        elif acao.tipo == "PROCEDIMENTO":
            self.procedimentos.remover_elemento(acao.alvo)
        elif acao.tipo == "DIAGNOSTICO":
            acao.alvo.marcar_saudavel()

    def calcular_total_procedimentos(self):
        """Soma os valores de todos os procedimentos no prontuario.

        Returns:
            float: Valor total dos procedimentos realizados.
        """
        total = 0.0
        for proc in self.procedimentos:
            total += proc.valor
        return round(total, 2)

    def calcular_total_medicamentos_estimado(self):
        """Soma os valores estimados dos medicamentos prescritos.

        Returns:
            float: Valor total estimado dos medicamentos.
        """
        total = 0.0
        for item in self.medicamentos:
            total += item.valor_estimado()
        return round(total, 2)

    def conceder_alta(self):
        """Marca que o animal recebeu alta veterinaria.

        Raises:
            ValueError: Se o prontuario ja estiver fechado ou ja tiver alta.
        """
        # Exige prontuario aberto e evita alta duplicada
        self.exigir_aberto()
        if self.alta_concedida:
            raise ValueError("Animal ja recebeu alta neste prontuario.")
        self.alta_concedida = True

    def validar_para_fechamento(self):
        """Verifica pre-condicoes obrigatorias antes de encerrar.

        Raises:
            ValueError: Se ja fechado ou se o animal nao recebeu alta.
        """
        self.exigir_aberto()
        if not self.alta_concedida:
            raise ValueError("Prontuario so pode fechar apos alta do animal.")

    def marcar_fechado(self):
        """Finaliza o prontuario registrando data e hora de fechamento."""
        self.validar_para_fechamento()
        self.fechado = True
        self.data_hora_fechamento = obter_data_hora_atual()

    def __str__(self):
        """Retorna resumo legivel do estado atual do prontuario.

        Returns:
            str: Numero, animal, tutor, vet, alta e status.
        """
        status = "FECHADO" if self.fechado else "ABERTO"
        alta = "SIM" if self.alta_concedida else "NAO"
        return (
            f"Prontuario #{self.numero} [{status}] | Animal: "
            f"{self.nome_animal} | Tutor: {self.nome_tutor} | "
            f"Vet: {self.veterinario} | Alta: {alta}"
        )
