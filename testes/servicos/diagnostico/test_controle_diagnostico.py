"""Testes unitarios intensivos do ControleDiagnostico e arvore animal."""

import unittest

from modelos.atendimento.ficha_espera.ficha_espera import FichaEspera
from modelos.prontuario.prontuario.prontuario import Prontuario
from servicos.diagnostico.controle_diagnostico import ControleDiagnostico


class TestControleDiagnostico(unittest.TestCase):
    """Valida arvore N-aria pre-definida, pre-ordem e marcacoes."""

    def setUp(self):
        """Instancia servico de diagnostico e um prontuario aberto."""
        self.servico = ControleDiagnostico()
        ficha = FichaEspera("Thor", "Ana", "11122233344", "Vomito", False)
        self.prontuario = Prontuario(1, ficha, "Dr. Joao", 1)

    def test_arvore_predefinida_contem_exemplos_do_pdf_e_n_aria(self):
        """Verifica presenca dos sistemas do PDF e grau > 2 (nao binaria)."""
        arvore = self.prontuario.arvore_diagnostico
        self.assertGreaterEqual(arvore.raiz.quantidade_filhos(), 4)
        texto = self.servico.gerar_arvore_indentada(arvore)
        self.assertIn("- Animal - Saudável", texto)
        self.assertIn("  - Sistema digestório - Saudável", texto)
        self.assertIn("    - Estômago [DIG-01] - Saudável", texto)
        self.assertIn("    - Pulmões [RES-01] - Saudável", texto)
        self.assertIn("    - Unhas [PEL-02] - Saudável", texto)

    def test_folhas_possuem_codigo_e_internos_nao(self):
        """Confirma que somente itens finais da hierarquia possuem codigo."""
        arvore = self.prontuario.arvore_diagnostico
        arvore.percorrer_pre_ordem(self._verificar_regra_codigo)

    def _verificar_regra_codigo(self, no, _nivel):
        """Assegura codigo preenchido em folhas e None em nos internos."""
        if no.eh_folha():
            self.assertIsNotNone(no.dado.codigo)
        else:
            self.assertIsNone(no.dado.codigo)

    def test_marcar_alterado_por_codigo_e_por_nome(self):
        """Valida marcacao case-insensitive por codigo folha ou por nome."""
        self.servico.marcar_alterado(self.prontuario, "dig-01")
        self.servico.marcar_alterado(self.prontuario, "Traqueia")
        alterados = self.servico.listar_alterados(
            self.prontuario.arvore_diagnostico
        )
        self.assertEqual(len(alterados), 2)

    def test_marcacao_repetida_nao_duplica_pilha_undo(self):
        """Garante idempotencia ao marcar item ja marcado como Alterado."""
        self.servico.marcar_alterado(self.prontuario, "DIG-01")
        self.servico.marcar_alterado(self.prontuario, "DIG-01")
        self.assertEqual(len(self.prontuario.historico_acoes), 1)

    def test_arvores_isoladas_entre_prontuarios_distintos(self):
        """Garante que alterar diagnostico de um animal nao afeta outro."""
        ficha2 = FichaEspera("Luna", "Ana", "11122233344", "Tosse", False)
        outro = Prontuario(2, ficha2, "Dr. Joao", 2)
        self.servico.marcar_alterado(self.prontuario, "RES-01")
        alt_outro = self.servico.listar_alterados(outro.arvore_diagnostico)
        self.assertEqual(len(alt_outro), 0)

    def test_erro_estrutura_inexistente_ou_prontuario_fechado(self):
        """Valida rejeicao de estrutura ausente e de prontuario encerrado."""
        with self.assertRaises(ValueError):
            self.servico.marcar_alterado(self.prontuario, "INEXISTENTE")
        self.prontuario.conceder_alta()
        self.prontuario.marcar_fechado()
        with self.assertRaises(ValueError):
            self.servico.marcar_alterado(self.prontuario, "DIG-01")
