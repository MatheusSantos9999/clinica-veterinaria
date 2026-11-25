"""Modulo que simula o ciclo completo de um atendimento veterinario."""

from clinica.fachada.clinica_veterinaria import ClinicaVeterinaria
from modelos.estoque.dados_lote.dados_lote import DadosLote
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento


class SimuladorAtendimento:
    """Executa uma simulacao ponta a ponta dos 5 passos exigidos."""

    def __init__(self, escritor=print):
        """Inicializa o simulador com funcao de saida configuravel.

        Args:
            escritor: Funcao utilizada para exibir mensagens (padrao print).
        """
        self._escrever = escritor
        self.clinica = ClinicaVeterinaria(quantidade_consultorios=2)

    def executar(self):
        """Executa todos os passos da simulacao completa da clinica.

        Returns:
            ClinicaVeterinaria: Instancia da clinica apos a simulacao.
        """
        # Prepara cadastros base e executa os 5 passos sequenciais
        self._preparar_cadastros_e_estoque()
        self._passo_1_chegada_e_espera()
        prontuario = self._passo_2_chamada_e_abertura()
        self._passo_3_diagnostico_arvore(prontuario)
        self._passo_4_medicamentos_e_procedimentos(prontuario)
        self._passo_5_alta_fechamento_pagamento(prontuario)
        return self.clinica

    def _preparar_cadastros_e_estoque(self):
        """Cadastra tutores, animais e lotes (incluindo um lote vencido)."""
        # Demonstra Lista + Lista (tutores -> animais) e Lista + Fila (lotes)
        self._escrever("=== PREPARACAO: TUTORES, ANIMAIS E ESTOQUE ===")
        self._cadastrar_tutor_ana()
        self._cadastrar_tutor_carlos()
        self._cadastrar_lotes_amoxicilina()
        self._adicionar_vacina_demo()

    def _cadastrar_tutor_ana(self):
        """Cadastra tutora Ana Silva com dois animais na sua lista."""
        t = self.clinica.tutores
        t.cadastrar_tutor("Ana Silva", "111.222.333-44", "(11) 99999-1111")
        t.cadastrar_animal("11122233344", "Thor", "Cao", "Labrador", 5)
        t.cadastrar_animal("11122233344", "Luna", "Gato", "Siames", 3)

    def _cadastrar_tutor_carlos(self):
        """Cadastra tutor Carlos Souza e o cao Rex."""
        t = self.clinica.tutores
        t.cadastrar_tutor("Carlos Souza", "555.666.777-88", "(11) 98888-2222")
        t.cadastrar_animal("55566677788", "Rex", "Cao", "SRD", 4)

    def _cadastrar_lotes_amoxicilina(self):
        """Registra um lote vencido e dois lotes validos em ordem FIFO."""
        # Lote vencido de Amoxicilina sera descartado como perda
        est = self.clinica.estoque
        l1 = DadosLote("VetFarma", 12.0, 28.0, "10/01/2025", "10/06/2025", 2)
        l2 = DadosLote("VetFarma", 15.0, 35.0, "10/01/2026", "10/12/2027", 2)
        l3 = DadosLote("BioPet", 18.0, 40.0, "15/06/2026", "15/12/2028", 4)
        est.adicionar_lote("AMX01", "Amoxicilina", l1, 5)
        est.adicionar_lote("AMX01", "Amoxicilina", l2, 5)
        est.adicionar_lote("AMX01", "Amoxicilina", l3, 5)

    def _adicionar_vacina_demo(self):
        """Adiciona lote de vacina antirrabica ao estoque da simulacao."""
        lote = DadosLote("ImunoVet", 25.0, 70.0, "01/05/2026", "01/05/2028", 6)
        self.clinica.estoque.adicionar_lote(
            "VAC01", "Vacina Antirrabica", lote, 3
        )

    def _passo_1_chegada_e_espera(self):
        """Simula chegada normal seguida por emergencia prioritaria."""
        # Fila + Fila: Rex (emergencia) deve passar a frente de Thor (normal)
        self._escrever("\n=== PASSO 1: CHEGADA E FILAS (NORMAL/EMERG) ===")
        f1 = self.clinica.registrar_chegada_animal(
            "11122233344", "Thor", "Falta de apetite e vomito", False
        )
        f2 = self.clinica.registrar_chegada_animal(
            "55566677788", "Rex", "Atropelamento na pata", True
        )
        self._exibir_chegadas(f1, f2)

    def _exibir_chegadas(self, ficha_1, ficha_2):
        """Imprime as fichas registradas e o proximo paciente indicado.

        Args:
            ficha_1: Primeira ficha registrada (normal).
            ficha_2: Segunda ficha registrada (emergencia).
        """
        self._escrever(f"Chegada 1: {ficha_1}")
        self._escrever(f"Chegada 2: {ficha_2}")
        prox = self.clinica.atendimento.indicar_proximo()
        self._escrever(f"Proximo indicado automaticamente: {prox.nome_animal}")

    def _passo_2_chamada_e_abertura(self):
        """Chama o proximo animal prioritario e abre o prontuario."""
        self._escrever("\n=== PASSO 2: CHAMADA E ABERTURA DO PRONTUARIO ===")
        prontuario = self.clinica.chamar_proximo_atendimento("Dra. Marina")
        self._escrever(f"Aberto: {prontuario}")
        self._escrever(f"Consultorio ocupado: {prontuario.numero_consultorio}")
        return prontuario

    def _passo_3_diagnostico_arvore(self, prontuario):
        """Marca estruturas alteradas e exibe a arvore em pre-ordem."""
        # Marca Coxins (LOC-01) e Estomago (DIG-01), depois desfaz Estomago
        self._escrever("\n=== PASSO 3: DIAGNOSTICO (ARVORE PRE-ORDEM) ===")
        num = prontuario.numero
        self.clinica.marcar_diagnostico_alterado(num, "LOC-01")
        self.clinica.marcar_diagnostico_alterado(num, "DIG-01")
        acao = self.clinica.prontuarios.desfazer_ultima_acao(num)
        self._escrever(f"Undo via Pilha realizado: {acao}")
        self._finalizar_exibicao_arvore(prontuario)

    def _finalizar_exibicao_arvore(self, prontuario):
        """Marca Pelos como alterado e imprime a arvore indentada.

        Args:
            prontuario: Prontuario em diagnostico.
        """
        self.clinica.marcar_diagnostico_alterado(prontuario.numero, "Pelos")
        arvore = prontuario.arvore_diagnostico
        self._escrever(self.clinica.diagnostico.gerar_arvore_indentada(arvore))

    def _passo_4_medicamentos_e_procedimentos(self, prontuario):
        """Inclui medicamentos, procedimentos e remove item nao autorizado."""
        self._escrever("\n=== PASSO 4: MEDICAMENTOS E PROCEDIMENTOS ===")
        self._descartar_vencidos_demo()
        num = prontuario.numero
        self.clinica.adicionar_medicamento_prontuario(num, "AMX01", 3)
        self._aplicar_procedimentos_demo(num)
        self._escrever("AMX01 (x3) e Consulta mantidos no prontuario.")

    def _aplicar_procedimentos_demo(self, numero):
        """Adiciona dois procedimentos e remove o nao autorizado pelo tutor.

        Args:
            numero: Numero do prontuario aberto.
        """
        cli = self.clinica
        cli.adicionar_procedimento_prontuario(
            numero, "Consulta de Emergencia", 150.0, "Triagem"
        )
        cli.adicionar_procedimento_prontuario(
            numero, "Raio-X Extra", 120.0, "Nao autorizado"
        )
        cli.prontuarios.remover_procedimento(numero, "Raio-X Extra")

    def _descartar_vencidos_demo(self):
        """Executa descarte preventivo de lotes vencidos exibindo perdas."""
        perdas = self.clinica.estoque.descartar_vencidos()
        for perda in perdas:
            self._escrever(str(perda))

    def _passo_5_alta_fechamento_pagamento(self, prontuario):
        """Concede alta, fecha prontuario com baixa FIFO e paga."""
        self._escrever("\n=== PASSO 5: ALTA, FECHAMENTO E PAGAMENTO ===")
        self.clinica.prontuarios.dar_alta(prontuario.numero)
        dados = DadosPagamento("Carlos Souza", "CARTAO_PARCELADO", 2)
        reg = self.clinica.fechar_atendimento(prontuario.numero, dados)
        self._exibir_resumo_fechamento(reg)

    def _exibir_resumo_fechamento(self, registro):
        """Exibe consumo, pagamento, alertas e proximo paciente da fila."""
        self._escrever(str(registro))
        self._escrever(str(registro.pagamento))
        for item in registro.itens_consumidos:
            self._escrever(f"  Baixa FIFO: {item}")
        for alerta in self.clinica.estoque.alertas:
            self._escrever(f"  {alerta}")
        prox = self.clinica.atendimento.indicar_proximo()
        self._escrever(f"Proximo na espera apos liberar sala: {prox}")
