"""Testes unitarios intensivos do ControleProntuarios e pilha de undo."""

import unittest

from modelos.atendimento.ficha_espera.ficha_espera import FichaEspera
from modelos.prontuario.item_medicamento.item_medicamento import (
    ItemMedicamento,
)
from modelos.prontuario.procedimento.procedimento import Procedimento
from servicos.diagnostico.controle_diagnostico import ControleDiagnostico
from servicos.prontuario.controle_prontuarios import ControleProntuarios


class TestControleProntuarios(unittest.TestCase):
    """Valida abertura, prescricoes, remocao, undo LIFO, alta e fechamento."""

    def setUp(self):
        """Inicializa ControleProntuarios e abre um prontuario base."""
        self.controle = ControleProntuarios()
        self.diag = ControleDiagnostico()
        ficha = FichaEspera("Rex", "Carlos", "11122233344", "Tosse", False)
        self.pront = self.controle.abrir_prontuario(ficha, "Dra. Luz", 1)

    def test_adicionar_e_remover_antes_do_fechamento(self):
        """Permite incluir e retirar medicamentos e procedimentos em aberto."""
        num = self.pront.numero
        self.controle.adicionar_medicamento(num, ItemMedicamento("M1", "M", 2))
        self.controle.adicionar_procedimento(num, Procedimento("RX", 120.0))
        self.controle.remover_medicamento(num, "m1")
        self.controle.remover_procedimento(num, "rx")
        self.assertEqual(len(self.pront.medicamentos), 0)
        self.assertEqual(len(self.pront.procedimentos), 0)

    def test_pilha_undo_reverte_em_ordem_lifo(self):
        """Valida desfazer diagnostico, procedimento e medicamento em LIFO."""
        num = self.pront.numero
        self.controle.adicionar_medicamento(num, ItemMedicamento("M1", "M", 1))
        self.controle.adicionar_procedimento(num, Procedimento("Cons", 90.0))
        self.diag.marcar_alterado(self.pront, "DIG-01")
        a1 = self.controle.desfazer_ultima_acao(num)
        a2 = self.controle.desfazer_ultima_acao(num)
        a3 = self.controle.desfazer_ultima_acao(num)
        tipos = (a1.tipo, a2.tipo, a3.tipo)
        self.assertEqual(tipos, ("DIAGNOSTICO", "PROCEDIMENTO", "MEDICAMENTO"))

    def test_undo_apos_remocao_manual_preserva_itens_anteriores(self):
        """Garante seguranca ao desfazer depois de remover item manualmente."""
        num = self.pront.numero
        self.controle.adicionar_medicamento(num, ItemMedicamento("M1", "A", 1))
        self.controle.adicionar_medicamento(num, ItemMedicamento("M2", "B", 1))
        self.controle.remover_medicamento(num, "M2")
        self.controle.desfazer_ultima_acao(num)
        restante = self.pront.medicamentos.obter_por_indice(0)
        self.assertEqual(len(self.pront.medicamentos), 1)
        self.assertEqual(restante.codigo_produto, "M1")

    def test_bloqueia_fechamento_antes_da_alta_e_alta_duplicada(self):
        """Garante que o prontuario so fecha apos alta concedida uma vez."""
        num = self.pront.numero
        with self.assertRaises(ValueError):
            self.controle.encerrar_prontuario(num)
        self.controle.dar_alta(num)
        with self.assertRaises(ValueError):
            self.controle.dar_alta(num)

    def test_bloqueia_alteracoes_apos_fechamento_e_empilha(self):
        """Impede edicao pos-fechamento e coloca encerrado no topo."""
        num = self.pront.numero
        self.controle.dar_alta(num)
        self.controle.encerrar_prontuario(num)
        self.assertEqual(len(self.controle.prontuarios_abertos), 0)
        self.assertEqual(self.controle.prontuarios_fechados.topo().numero, num)
        with self.assertRaises(ValueError):
            self.controle.adicionar_procedimento(num, Procedimento("Ex", 50.0))
        with self.assertRaises(ValueError):
            self.controle.remover_medicamento(num, "M1")

    def test_buscar_prontuario_aberto_e_fechado(self):
        """Valida busca unificada entre abertos e pilha de fechados."""
        num = self.pront.numero
        self.assertIsNotNone(self.controle.buscar_por_numero(num))
        self.controle.dar_alta(num)
        self.controle.encerrar_prontuario(num)
        achado = self.controle.buscar_por_numero(num)
        self.assertIsNotNone(achado)
        self.assertTrue(achado.fechado)
        self.assertIsNone(self.controle.buscar_por_numero(999))
