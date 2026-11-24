"""Testes unitarios intensivos da estrutura propria ListaEncadeada."""

import unittest

from estruturas.lista.lista_encadeada import ListaEncadeada


class TestListaEncadeada(unittest.TestCase):
    """Valida invariantes, ponteiros e limites da ListaEncadeada."""

    def test_lista_inicial_vazia(self):
        """Garante estado inicial vazio e indice invalido protegido."""
        lista = ListaEncadeada()
        self.assertTrue(lista.esta_vazia())
        self.assertEqual(len(lista), 0)
        with self.assertRaises(IndexError):
            lista.obter_por_indice(0)

    def test_adicionar_e_obter_por_indice(self):
        """Valida insercao no fim, no inicio e leitura por indice."""
        lista = ListaEncadeada()
        lista.adicionar("B")
        lista.adicionar("C")
        lista.adicionar_inicio("A")
        self.assertEqual(len(lista), 3)
        self.assertEqual(lista.obter_por_indice(0), "A")
        self.assertEqual(lista.obter_por_indice(2), "C")

    def test_indices_negativos_e_fora_do_limite(self):
        """Garante erro em indices negativos ou maiores que o tamanho."""
        lista = ListaEncadeada()
        lista.adicionar(10)
        with self.assertRaises(IndexError):
            lista.obter_por_indice(-1)
        with self.assertRaises(IndexError):
            lista.obter_por_indice(1)

    def test_remover_inicio_meio_fim_e_reutilizar(self):
        """Valida atualizacao dos ponteiros inicio e fim nas remocoes."""
        lista = ListaEncadeada()
        for num in range(1, 5):
            lista.adicionar(num)
        self.assertTrue(lista.remover_elemento(1))
        self.assertTrue(lista.remover_elemento(3))
        self.assertTrue(lista.remover_elemento(4))
        self.assertEqual(lista.obter_por_indice(0), 2)
        lista.adicionar(99)
        self.assertEqual(lista.obter_por_indice(1), 99)

    def test_remover_unico_elemento_e_reinserir(self):
        """Garante integridade ao esvaziar completamente e reinserir."""
        lista = ListaEncadeada()
        lista.adicionar("unico")
        self.assertTrue(lista.remover_elemento("unico"))
        self.assertTrue(lista.esta_vazia())
        lista.adicionar("novo")
        self.assertEqual(lista.obter_por_indice(0), "novo")

    def test_buscar_filtrar_e_limpar(self):
        """Valida busca, filtragem em lista propria e limpeza total."""
        lista = ListaEncadeada()
        for num in range(6):
            lista.adicionar(num)
        self.assertEqual(lista.buscar(lambda x: x > 3), 4)
        pares = lista.filtrar(lambda x: x % 2 == 0)
        self.assertIsInstance(pares, ListaEncadeada)
        self.assertEqual(len(pares), 3)
        lista.limpar()
        self.assertTrue(lista.esta_vazia())

    def test_estresse_insercao_e_iteracao(self):
        """Valida integridade em carga com 500 elementos encadeados."""
        lista = ListaEncadeada()
        for idx in range(500):
            lista.adicionar(idx)
        self.assertEqual(len(lista), 500)
        esperado = 0
        for item in lista:
            self.assertEqual(item, esperado)
            esperado += 1
