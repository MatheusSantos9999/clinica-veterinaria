"""Testes unitarios intensivos da estrutura propria FilaEncadeada."""

import unittest

from estruturas.fila.fila_encadeada import FilaEncadeada


class TestFilaEncadeada(unittest.TestCase):
    """Valida disciplina FIFO, ponteiros e limites da FilaEncadeada."""

    def test_fila_vazia_operacoes(self):
        """Garante erro ao desenfileirar vazia e espiar retornando None."""
        fila = FilaEncadeada()
        self.assertTrue(fila.esta_vazia())
        self.assertIsNone(fila.espiar())
        with self.assertRaises(IndexError):
            fila.desenfileirar()

    def test_ordem_estritamente_fifo(self):
        """Valida que elementos saem exatamente na ordem de entrada."""
        fila = FilaEncadeada()
        fila.enfileirar("primeiro")
        fila.enfileirar("segundo")
        fila.enfileirar("terceiro")
        self.assertEqual(fila.espiar(), "primeiro")
        self.assertEqual(fila.desenfileirar(), "primeiro")
        self.assertEqual(fila.desenfileirar(), "segundo")
        self.assertEqual(fila.desenfileirar(), "terceiro")

    def test_esvaziar_e_enfileirar_novamente(self):
        """Garante que o ponteiro de tras seja zerado ao esvaziar."""
        fila = FilaEncadeada()
        fila.enfileirar(1)
        self.assertEqual(fila.desenfileirar(), 1)
        self.assertTrue(fila.esta_vazia())
        fila.enfileirar(2)
        fila.enfileirar(3)
        self.assertEqual(len(fila), 2)
        self.assertEqual(fila.desenfileirar(), 2)

    def test_buscar_e_iterar_sem_remover(self):
        """Valida busca e iteracao sem alterar o conteudo da fila."""
        fila = FilaEncadeada()
        fila.enfileirar(10)
        fila.enfileirar(20)
        self.assertEqual(fila.buscar(lambda x: x == 20), 20)
        self.assertIsNone(fila.buscar(lambda x: x == 99))
        self.assertEqual(len(fila), 2)

    def test_estresse_fifo_500_itens(self):
        """Valida comportamento FIFO com 500 insercoes e remocoes."""
        fila = FilaEncadeada()
        for idx in range(500):
            fila.enfileirar(idx)
        for idx in range(500):
            self.assertEqual(fila.desenfileirar(), idx)
        self.assertTrue(fila.esta_vazia())
