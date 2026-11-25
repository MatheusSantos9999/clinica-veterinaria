"""Testes QA agressivos de atomicidade e integracao no ControleConsumo."""

import unittest

from modelos.atendimento.ficha_espera.ficha_espera import FichaEspera
from modelos.estoque.dados_lote.dados_lote import DadosLote
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento
from modelos.prontuario.item_medicamento.item_medicamento import (
    ItemMedicamento,
)
from modelos.prontuario.procedimento.procedimento import Procedimento
from servicos.consumo.controle_consumo import ControleConsumo
from servicos.estoque.controle_estoque import ControleEstoque
from servicos.pagamento.controle_pagamentos import ControlePagamentos
from servicos.prontuario.controle_prontuarios import ControleProntuarios


class TestControleConsumo(unittest.TestCase):
    """Ataca atomicidade, duplicatas, vencimento tardio e faturamento."""

    def setUp(self):
        """Monta estoque, prontuarios, pagamentos e controle de consumo."""
        self.estoque = ControleEstoque()
        self.pronts = ControleProntuarios()
        self.pags = ControlePagamentos()
        self.consumo = ControleConsumo(self.estoque, self.pronts, self.pags)

    def test_atomicidade_falha_no_segundo_item_nao_baixa_o_primeiro(self):
        """Garante zero baixa parcial quando segundo medicamento falta."""
        self._add("A", "MedA", 5, 20.0, "01/01/2028")
        self._add("B", "MedB", 2, 30.0, "01/01/2028")
        p = self._abrir_com_alta("Rex", "11122233344")
        p.adicionar_medicamento(ItemMedicamento("A", "MedA", 3, 20.0))
        p.adicionar_medicamento(ItemMedicamento("B", "MedB", 4, 30.0))
        with self.assertRaises(ValueError):
            self._fechar_pix(p.numero)
        self.assertEqual((self._saldo("A"), p.fechado), (5, False))

    def _fechar_pix(self, numero):
        """Helper para fechar prontuario pagando via PIX."""
        return self.consumo.fechar_e_consumir(
            numero, DadosPagamento("T", "PIX")
        )

    def test_atomicidade_item_repetido_excedendo_saldo_total(self):
        """Bloqueia fechamento se mesma droga somada exceder saldo valido."""
        self._add("A", "MedA", 5, 20.0, "01/01/2028")
        p = self._abrir_com_alta("Rex", "11122233344")
        p.adicionar_medicamento(ItemMedicamento("A", "MedA", 3, 20.0))
        p.adicionar_medicamento(ItemMedicamento("A", "MedA", 3, 20.0))
        pag = DadosPagamento("T", "PIX")
        with self.assertRaises(ValueError):
            self.consumo.fechar_e_consumir(p.numero, pag)
        self.assertEqual(self._saldo("A"), 5)

    def test_lote_vence_entre_prescricao_e_fechamento(self):
        """Descarta lote expirado no fechamento e usa o proximo lote valido."""
        self._add("A", "MedA", 2, 10.0, "01/05/2026")
        self._add("A", "MedA", 4, 25.0, "01/12/2027")
        p = self._abrir_com_alta("Mel", "11122233344")
        p.adicionar_medicamento(ItemMedicamento("A", "MedA", 2, 10.0))
        reg = self.consumo.fechar_e_consumir(
            p.numero, DadosPagamento("Ana", "DINHEIRO"), "01/06/2026"
        )
        self.assertEqual(len(self.estoque.perdas), 1)
        self.assertEqual(reg.pagamento.valor_medicamentos, 50.0)

    def test_prontuario_somente_procedimentos_sem_medicamentos(self):
        """Valida fechamento limpo quando atendimento nao usa medicamentos."""
        p = self._abrir_com_alta("Bidu", "11122233344")
        p.adicionar_procedimento(Procedimento("Consulta", 80.0))
        pag = DadosPagamento("Ana", "PIX")
        reg = self.consumo.fechar_e_consumir(p.numero, pag, "01/06/2026")
        self.assertEqual(reg.pagamento.valor_medicamentos, 0.0)
        self.assertEqual(reg.pagamento.valor_total, 80.0)
        por_tut = self.consumo.consultar_por_tutor("11122233344")
        por_pet = self.consumo.consultar_por_animal("11122233344", "bidu")
        self.assertEqual(len(por_tut) + len(por_pet), 2)

    def _saldo(self, codigo):
        """Retorna quantidade total atual de um produto no estoque."""
        return self.estoque.buscar_produto(codigo).quantidade_total()

    def _add(self, cod, nome, qtd, preco_venda, validade):
        """Helper para adicionar lote valido de teste ao estoque."""
        dados = DadosLote(
            "Forn", 5.0, preco_venda, "01/01/2026", validade, qtd
        )
        self.estoque.adicionar_lote(cod, nome, dados, 2)

    def _abrir_com_alta(self, animal, cpf):
        """Abre prontuario de teste e ja concede alta para fechar."""
        ficha = FichaEspera(animal, "Tutor", cpf, "Rotina", False)
        pront = self.pronts.abrir_prontuario(ficha, "Dra. Eva", 1)
        self.pronts.dar_alta(pront.numero)
        return pront
