"""Testes unitarios intensivos do ControleAtendimento (Fila + Fila)."""

import unittest

from modelos.atendimento.ficha_espera.ficha_espera import FichaEspera
from servicos.atendimento.controle_atendimento import ControleAtendimento


class TestControleAtendimento(unittest.TestCase):
    """Valida prioridade de emergencia, FIFO e consultorios limitados."""

    def setUp(self):
        """Cria ControleAtendimento com 2 consultorios para cada teste."""
        self.controle = ControleAtendimento(quantidade_consultorios=2)

    def test_rejeitar_quantidade_invalida_de_consultorios(self):
        """Impede criar clinica com 0, negativo ou booleano consultorios."""
        with self.assertRaises(ValueError):
            ControleAtendimento(0)
        with self.assertRaises(ValueError):
            ControleAtendimento(-2)
        with self.assertRaises(ValueError):
            ControleAtendimento(True)

    def test_emergencias_passam_frente_respeitando_fifo_entre_si(self):
        """Valida ordem: emergencias em FIFO primeiro, depois normais FIFO."""
        self._enfileirar("Normal1", "11111111111", False)
        self._enfileirar("Normal2", "22222222222", False)
        self._enfileirar("Emerg1", "33333333333", True)
        self._enfileirar("Emerg2", "44444444444", True)
        self.assertEqual(self.controle.indicar_proximo().nome_animal, "Emerg1")
        sala1 = self.controle.chamar_proximo(1)
        sala2 = self.controle.chamar_proximo(2)
        self.assertEqual(sala1.ficha_atual.nome_animal, "Emerg1")
        self.assertEqual(sala2.ficha_atual.nome_animal, "Emerg2")

    def test_consultorios_esgotados_e_liberacao_indica_proximo(self):
        """Valida bloqueio com salas cheias e indicacao ao liberar."""
        self._enfileirar("A", "11111111111", False)
        self._enfileirar("B", "22222222222", False)
        self._enfileirar("C", "33333333333", False)
        self.controle.chamar_proximo(1)
        self.controle.chamar_proximo(2)
        with self.assertRaises(ValueError):
            self.controle.chamar_proximo(3)
        proximo = self.controle.liberar_consultorio(1)
        self.assertEqual(proximo.nome_animal, "C")

    def test_bloqueia_duplicidade_na_fila_e_em_consultorio(self):
        """Impede que o mesmo animal entre duas vezes na fila ou ja em sala."""
        self._enfileirar("Rex", "11111111111", False)
        with self.assertRaises(ValueError):
            self._enfileirar("rex", "111.111.111-11", True)
        self.controle.chamar_proximo(1)
        with self.assertRaises(ValueError):
            self._enfileirar("Rex", "11111111111", False)

    def test_chamar_fila_vazia_e_liberar_sala_invalida(self):
        """Valida erros ao chamar com filas vazias ou liberar sala livre."""
        with self.assertRaises(ValueError):
            self.controle.chamar_proximo(1)
        with self.assertRaises(ValueError):
            self.controle.liberar_consultorio(1)
        with self.assertRaises(ValueError):
            self.controle.liberar_consultorio(99)

    def test_liberar_com_fila_vazia_e_emergencia_invalida(self):
        """Valida retorno None sem espera e bloqueio de emergencia nao bool."""
        self._enfileirar("Rex", "11111111111", False)
        self.controle.chamar_proximo(1)
        self.assertIsNone(self.controle.liberar_consultorio(1))
        with self.assertRaises(ValueError):
            FichaEspera("A", "T", "11111111111", "Q", "sim")

    def _enfileirar(self, animal, cpf, emergencia):
        """Cria e registra uma FichaEspera auxiliar para o teste.

        Args:
            animal: Nome do animal.
            cpf: CPF do tutor.
            emergencia: True para emergencia, False para normal.
        """
        ficha = FichaEspera(animal, "Tutor", cpf, "Queixa", emergencia)
        self.controle.registrar_chegada(ficha)
