"""Testes unitarios intensivos do ControlePagamentos e DadosPagamento."""

import unittest

from modelos.atendimento.ficha_espera.ficha_espera import FichaEspera
from modelos.pagamento.dados_pagamento.dados_pagamento import DadosPagamento
from modelos.prontuario.prontuario.prontuario import Prontuario
from servicos.pagamento.controle_pagamentos import ControlePagamentos


class TestControlePagamentos(unittest.TestCase):
    """Valida PIX, dinheiro, cartao a vista/parcelado e protecao duplicata."""

    def setUp(self):
        """Inicializa ControlePagamentos e um prontuario de exemplo."""
        self.controle = ControlePagamentos()
        ficha = FichaEspera("Luna", "Ana", "11122233344", "Vacina", False)
        self.pront = Prontuario(1, ficha, "Dr. Pedro", 1)

    def test_todas_as_formas_de_pagamento_validas(self):
        """Valida PIX, DINHEIRO, CARTAO_AVISTA e CARTAO_PARCELADO."""
        d1 = DadosPagamento("Ana", "pix", 1)
        d2 = DadosPagamento("Ana", "dinheiro", 1)
        d3 = DadosPagamento("Ana", "cartao_avista", 1)
        d4 = DadosPagamento("Ana", "cartao_parcelado", 4)
        self.assertEqual(d1.forma_pagamento, "PIX")
        self.assertEqual(d2.forma_pagamento, "DINHEIRO")
        self.assertEqual(d3.forma_pagamento, "CARTAO_AVISTA")
        self.assertEqual(d4.numero_parcelas, 4)

    def test_rejeitar_formas_e_parcelas_nao_parcelado(self):
        """Bloqueia forma desconhecida e >1 parcela fora do parcelado."""
        with self.assertRaises(ValueError):
            DadosPagamento("Ana", "BOLETO", 1)
        with self.assertRaises(ValueError):
            DadosPagamento("Ana", "PIX", 2)
        with self.assertRaises(ValueError):
            DadosPagamento("Ana", "CARTAO_AVISTA", 3)

    def test_rejeitar_faixa_invalida_cartao_parcelado(self):
        """Bloqueia cartao parcelado com menos de 2 ou mais de 12 parcelas."""
        with self.assertRaises(ValueError):
            DadosPagamento("Ana", "CARTAO_PARCELADO", 1)
        with self.assertRaises(ValueError):
            DadosPagamento("Ana", "CARTAO_PARCELADO", 13)

    def test_registrar_pagamento_e_bloquear_duplicata(self):
        """Calcula total, valor por parcela e impede cobranca duplicada."""
        dados = DadosPagamento("Ana", "CARTAO_PARCELADO", 3)
        pag = self.controle.registrar_pagamento(
            self.pront, dados, 100.0, 200.0
        )
        self.assertEqual(pag.valor_total, 300.0)
        self.assertEqual(pag.valor_por_parcela(), 100.0)
        self.assertEqual(self.controle.calcular_total_recebido(), 300.0)
        with self.assertRaises(ValueError):
            self.controle.registrar_pagamento(self.pront, dados, 10.0, 10.0)

    def test_rejeitar_tipo_incorreto_em_dados_pagamento(self):
        """Garante TypeError se objeto diferente de DadosPagamento."""
        with self.assertRaises(TypeError):
            self.controle.registrar_pagamento(self.pront, "PIX", 10.0, 20.0)
