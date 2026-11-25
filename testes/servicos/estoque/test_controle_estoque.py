"""Testes unitarios intensivos do ControleEstoque (Lista + Fila FIFO)."""

import unittest

from modelos.estoque.dados_lote.dados_lote import DadosLote
from servicos.estoque.controle_estoque import ControleEstoque


class TestControleEstoque(unittest.TestCase):
    """Valida FIFO multi-lote, validade/perdas, ajuste e alertas."""

    def setUp(self):
        """Inicializa ControleEstoque limpo para cada teste."""
        self.estoque = ControleEstoque()

    def test_baixa_fifo_consome_lote_mais_antigo_primeiro(self):
        """Valida consumo cruzando multiplos lotes com precos distintos."""
        self._add("M1", "Med", 10.0, 20.0, "01/01/2026", "01/01/2028", 2)
        self._add("M1", "Med", 12.0, 30.0, "01/02/2026", "01/02/2028", 5)
        itens = self.estoque.baixar_estoque("M1", 4, "01/06/2026")
        self.assertEqual(len(itens), 2)
        self.assertEqual(itens.obter_por_indice(0).preco_unitario_venda, 20.0)
        self.assertEqual(itens.obter_por_indice(1).preco_unitario_venda, 30.0)
        self.assertEqual(self._total("M1"), 3)

    def test_baixa_descarta_lote_vencido_como_perda(self):
        """Garante que vencido nunca seja consumido e gere perda."""
        self._add("V1", "Vac", 20.0, 50.0, "01/01/2025", "01/05/2025", 3)
        self._add("V1", "Vac", 25.0, 60.0, "01/01/2026", "01/01/2028", 4)
        itens = self.estoque.baixar_estoque("V1", 2, "01/06/2026")
        perda = self.estoque.perdas.obter_por_indice(0)
        self.assertEqual(len(self.estoque.perdas), 1)
        self.assertEqual(perda.valor_prejuizo, 60.0)
        self.assertEqual(itens.obter_por_indice(0).preco_unitario_venda, 60.0)

    def test_ajuste_inventario_zerando_remove_lote_e_alerta(self):
        """Valida edicao manual de saldo, remocao se 0 e alerta minimo."""
        l1 = self._add("A1", "Atad", 2.0, 5.0, "01/01/2026", "01/01/2028", 6)
        self.estoque.ajustar_quantidade("A1", l1.numero_lote, 3, "01/06/2026")
        self.assertEqual(len(self.estoque.alertas), 1)
        self.estoque.ajustar_quantidade("A1", l1.numero_lote, 0, "01/06/2026")
        self.assertEqual(len(self.estoque.buscar_produto("A1").lotes), 0)

    def test_baixa_insuficiente_nao_altera_lotes_validos(self):
        """Garante integridade: falha por falta de saldo preserva lotes."""
        self._add("M1", "Med", 5.0, 10.0, "01/01/2026", "01/01/2028", 3)
        with self.assertRaises(ValueError):
            self.estoque.baixar_estoque("M1", 4, "01/06/2026")
        self.assertEqual(self._total("M1"), 3)

    def test_validacoes_de_datas_precos_nan_inf_e_bool(self):
        """Ataca validacoes com validade < compra, NaN, Inf e booleanos."""
        with self.assertRaises(ValueError):
            DadosLote("F", 1.0, 2.0, "10/05/2026", "01/05/2026", 5)
        with self.assertRaises(ValueError):
            DadosLote("F", float("nan"), 2.0, "01/05/2026", "10/05/2026", 5)
        with self.assertRaises(ValueError):
            DadosLote("F", 1.0, float("inf"), "01/05/2026", "10/05/2026", 5)
        with self.assertRaises(ValueError):
            DadosLote("F", 1.0, 2.0, "01/05/2026", "10/05/2026", True)

    def test_descartar_vencidos_mantem_ordem_fifo_dos_validos(self):
        """Valida preservacao da ordem FIFO quando lote do meio vence."""
        l1 = self._add("X", "Prod", 1.0, 10.0, "01/01/2026", "01/12/2027", 1)
        self._add("X", "Prod", 1.0, 20.0, "01/02/2026", "01/03/2026", 2)
        self._add("X", "Prod", 1.0, 30.0, "01/04/2026", "01/12/2028", 1)
        perdas = self.estoque.descartar_vencidos("01/06/2026")
        prod = self.estoque.buscar_produto("X")
        self.assertEqual(len(perdas), 1)
        self.assertEqual(prod.lotes.espiar().numero_lote, l1.numero_lote)
        self.assertEqual(len(prod.lotes), 2)

    def test_data_iso_lote_inexistente_e_preco_pula_vencidos(self):
        """Valida datas ISO, ajuste inexistente e preco ignorando vencido."""
        self._add("Z", "Vac", 5.0, 15.0, "2025-01-01", "2025-02-01", 2)
        prod = self.estoque.buscar_produto("Z")
        self.assertEqual(prod.preco_venda_atual("2026-06-01"), 0.0)
        with self.assertRaises(ValueError):
            self.estoque.ajustar_quantidade("Z", 999, 5)

    def _total(self, codigo):
        """Retorna saldo total do produto informado."""
        return self.estoque.buscar_produto(codigo).quantidade_total()

    def _add(self, cod, nome, pc, pv, dc, dv, qtd):
        """Helper para enfileirar lote rapidamente com minimo padrao 5."""
        dados = DadosLote("Fornecedor", pc, pv, dc, dv, qtd)
        return self.estoque.adicionar_lote(cod, nome, dados, 5)
