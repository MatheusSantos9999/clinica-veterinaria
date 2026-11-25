"""Testes de integracao ponta a ponta e estresse na ClinicaVeterinaria."""

import unittest

from clinica.fachada.clinica_veterinaria import ClinicaVeterinaria
from clinica.simulacao.simulador_atendimento import SimuladorAtendimento
from modelos.estoque.dados_lote.dados_lote import DadosLote
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento


class TestFluxoCompleto(unittest.TestCase):
    """Valida integracao total, concorrencia de estoque e protecoes."""

    def test_simulacao_completa_5_passos_gera_estado_consistente(self):
        """Executa SimuladorAtendimento e valida todos os efeitos finais."""
        linhas = []
        cli = SimuladorAtendimento(escritor=linhas.append).executar()
        self.assertEqual(len(cli.estoque.perdas), 1)
        self.assertEqual(len(cli.estoque.alertas), 1)
        self.assertEqual(len(cli.prontuarios.prontuarios_fechados), 1)
        self.assertEqual(cli.pagamentos.calcular_total_recebido(), 260.0)
        prox = cli.atendimento.indicar_proximo()
        self.assertEqual(prox.nome_animal, "Thor")

    def test_dois_prontuarios_concorrentes_disputando_mesmo_estoque(self):
        """Garante protecao quando paciente 1 esgota estoque antes do 2."""
        cli = self._montar_clinica_dois_pacientes()
        p1 = self._preparar_paciente_med(cli, "Dr. A", 3)
        p2 = self._preparar_paciente_med(cli, "Dr. B", 3)
        pag1 = DadosPagamento("Ana", "PIX")
        pag2 = DadosPagamento("Beto", "PIX")
        cli.fechar_atendimento(p1.numero, pag1, "01/06/2026")
        with self.assertRaises(ValueError):
            cli.fechar_atendimento(p2.numero, pag2, "01/06/2026")

    def _preparar_paciente_med(self, cli, vet, qtd):
        """Chama proximo animal, prescreve MED e concede alta."""
        pront = cli.chamar_proximo_atendimento(vet)
        cli.adicionar_medicamento_prontuario(
            pront.numero, "MED", qtd, "01/06/2026"
        )
        cli.prontuarios.dar_alta(pront.numero)
        return pront

    def test_remocao_bloqueada_ativo_e_liberada_apos_fechamento(self):
        """Bloqueia remocao de tutor/animal na fila ou sala e libera depois."""
        cli = self._montar_clinica_dois_pacientes()
        with self.assertRaises(ValueError):
            cli.remover_tutor_seguro("111.222.333-44")
        p1 = cli.chamar_proximo_atendimento("Dr. A")
        with self.assertRaises(ValueError):
            cli.remover_animal_seguro("111.222.333-44", "Thor")
        self._fechar_e_remover_thor(cli, p1.numero)

    def _fechar_e_remover_thor(self, cli, num):
        """Concede alta, fecha prontuario e valida remocao liberada."""
        cli.prontuarios.dar_alta(num)
        pag = DadosPagamento("Ana", "PIX")
        cli.fechar_atendimento(num, pag, "01/06/2026")
        removido = cli.remover_animal_seguro("111.222.333-44", "Thor")
        self.assertEqual(removido.nome, "Thor")

    def test_veterinario_vazio_nao_desenfileira_nem_ocupa_sala(self):
        """Garante estado intacto se veterinario for invalido na chamada."""
        cli = self._montar_clinica_dois_pacientes()
        with self.assertRaises(ValueError):
            cli.chamar_proximo_atendimento("   ")
        self.assertEqual(cli.atendimento.total_em_espera(), 2)
        self.assertIsNotNone(cli.atendimento.obter_consultorio_livre())

    def _montar_clinica_dois_pacientes(self):
        """Cria clinica com 2 salas, 2 animais na espera e 4 unidades."""
        cli = ClinicaVeterinaria(quantidade_consultorios=2)
        self._popular_tutores_e_fila(cli)
        lote = DadosLote("Forn", 10.0, 25.0, "01/01/2026", "01/12/2028", 4)
        cli.estoque.adicionar_lote("MED", "Antibiotico", lote, 2)
        return cli

    def _popular_tutores_e_fila(self, cli):
        """Cadastra dois tutores/animais e registra ambos na fila normal."""
        cli.tutores.cadastrar_tutor("Ana", "11122233344", "1191")
        cli.tutores.cadastrar_animal("11122233344", "Thor", "Cao", "Pug", 3)
        cli.tutores.cadastrar_tutor("Beto", "55566677788", "1192")
        cli.tutores.cadastrar_animal("55566677788", "Rex", "Cao", "SRD", 4)
        cli.registrar_chegada_animal("11122233344", "Thor", "Febre", False)
        cli.registrar_chegada_animal("55566677788", "Rex", "Tosse", False)
