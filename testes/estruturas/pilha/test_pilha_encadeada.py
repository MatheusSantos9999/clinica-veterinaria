"""Testes unitarios intensivos da estrutura propria PilhaEncadeada."""

import unittest

from estruturas.pilha.pilha_encadeada import PilhaEncadeada


class TestPilhaEncadeada(unittest.TestCase):
    """Valida disciplina LIFO, ponteiro de topo e limites da pilha."""

    def test_pilha_vazia_operacoes(self):
        """Garante erro ao desempilhar vazia e topo retornando None."""
        pilha = PilhaEncadeada()
        self.assertTrue(pilha.esta_vazia())
        self.assertIsNone(pilha.topo())
        with self.assertRaises(IndexError):
            pilha.desempilhar()

    def test_ordem_estritamente_lifo(self):
        """Valida que o ultimo elemento empilhado e o primeiro a sair."""
        pilha = PilhaEncadeada()
        pilha.empilhar("A")
        pilha.empilhar("B")
        pilha.empilhar("C")
        self.assertEqual(pilha.topo(), "C")
        self.assertEqual(pilha.desempilhar(), "C")
        self.assertEqual(pilha.desempilhar(), "B")
        self.assertEqual(pilha.desempilhar(), "A")

    def test_iteracao_do_topo_para_base(self):
        """Valida que a iteracao percorre do topo ate a base sem alterar."""
        pilha = PilhaEncadeada()
        pilha.empilhar(1)
        pilha.empilhar(2)
        pilha.empilhar(3)
        coletado = ""
        for item in pilha:
            coletado += str(item)
        self.assertEqual(coletado, "321")
        self.assertEqual(len(pilha), 3)

    def test_estresse_lifo_500_itens(self):
        """Valida disciplina LIFO sob 500 operacoes consecutivas."""
        pilha = PilhaEncadeada()
        for idx in range(500):
            pilha.empilhar(idx)
        for idx in range(499, -1, -1):
            self.assertEqual(pilha.desempilhar(), idx)
        self.assertTrue(pilha.esta_vazia())
