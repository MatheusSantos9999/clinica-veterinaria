"""Testes unitarios intensivos da arvore N-aria propria."""

import unittest

from estruturas.arvore.arvore_n_aria.arvore_n_aria import ArvoreNAria
from estruturas.arvore.no_arvore.no_arvore import NoArvore


class TestArvoreNAria(unittest.TestCase):
    """Valida multiplicidade 0..N filhos, pre-ordem e busca na arvore."""

    def test_rejeita_raiz_e_filho_invalidos(self):
        """Garante protecao de tipo na raiz e ao acoplar filhos."""
        with self.assertRaises(TypeError):
            ArvoreNAria("nao_eh_no")
        raiz = NoArvore("raiz")
        with self.assertRaises(TypeError):
            raiz.adicionar_filho("invalido")

    def test_suporta_mais_de_dois_filhos_nao_binaria(self):
        """Comprova que um no aceita 0 a N filhos (exemplo com 5 filhos)."""
        raiz = NoArvore("Animal")
        for idx in range(5):
            raiz.adicionar_filho(NoArvore(f"Sistema_{idx}"))
        self.assertFalse(raiz.eh_folha())
        self.assertEqual(raiz.quantidade_filhos(), 5)
        arvore = ArvoreNAria(raiz)
        self.assertEqual(arvore.contar_nos(), 6)

    def test_percurso_pre_ordem_exato(self):
        """Valida ordem de visita raiz -> filho 1 -> subfilhos -> filho 2."""
        arvore = self._montar_arvore_exemplo()
        ordem = []
        arvore.percorrer_pre_ordem(
            lambda no, niv: ordem.append(f"{niv}:{no.dado}")
        )
        self.assertEqual(
            ordem, ["0:R", "1:A", "2:A1", "2:A2", "1:B", "1:C"]
        )

    def test_buscar_e_filtrar_em_pre_ordem(self):
        """Valida busca de no existente, ausente e filtragem por criterio."""
        arvore = self._montar_arvore_exemplo()
        achado = arvore.buscar_no(lambda d: d == "A2")
        self.assertIsNotNone(achado)
        self.assertTrue(achado.eh_folha())
        self.assertIsNone(arvore.buscar_no(lambda d: d == "ZZ"))
        filtrados = arvore.filtrar_dados(lambda d: d.startswith("A"))
        self.assertEqual(len(filtrados), 3)

    def _montar_arvore_exemplo(self):
        """Cria arvore N-aria pequena para testes de travessia.

        Returns:
            ArvoreNAria: Arvore com 3 filhos na raiz e 2 subfilhos em A.
        """
        raiz = NoArvore("R")
        no_a = raiz.adicionar_filho(NoArvore("A"))
        no_a.adicionar_filho(NoArvore("A1"))
        no_a.adicionar_filho(NoArvore("A2"))
        raiz.adicionar_filho(NoArvore("B"))
        raiz.adicionar_filho(NoArvore("C"))
        return ArvoreNAria(raiz)
