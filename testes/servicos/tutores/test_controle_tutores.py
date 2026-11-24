"""Testes unitarios intensivos do ControleTutores (Lista + Lista)."""

import unittest

from servicos.tutores.controle_tutores import ControleTutores


class TestControleTutores(unittest.TestCase):
    """Valida cadastro, busca, remocao e limites de tutores e animais."""

    def setUp(self):
        """Prepara instancia limpa de ControleTutores para cada teste."""
        self.controle = ControleTutores()

    def test_cadastrar_e_buscar_tutor_com_mascaras_diferentes(self):
        """Valida busca por CPF ignorando formatacao de pontos e traco."""
        self.controle.cadastrar_tutor(
            "Maria Clara", "123.456.789-01", "11999990000"
        )
        achado = self.controle.buscar_tutor_por_cpf("12345678901")
        self.assertIsNotNone(achado)
        self.assertEqual(achado.nome, "Maria Clara")

    def test_rejeitar_cpf_duplicado_e_invalido(self):
        """Garante bloqueio de CPF duplicado e CPFs fora do padrao."""
        self.controle.cadastrar_tutor("Joao", "11122233344", "11900000000")
        with self.assertRaises(ValueError):
            self.controle.cadastrar_tutor("Outro", "111.222.333-44", "119")
        with self.assertRaises(ValueError):
            self.controle.cadastrar_tutor("Ruim", "12345", "119")
        with self.assertRaises(ValueError):
            self.controle.cadastrar_tutor("Ruim", "123456789012", "119")

    def test_tutor_cadastra_muitos_animais_sem_limite(self):
        """Comprova que um tutor pode acumular animais sem teto fixo."""
        self.controle.cadastrar_tutor("Ana", "22233344455", "11988887777")
        for idx in range(15):
            self.controle.cadastrar_animal(
                "22233344455", f"Pet_{idx}", "Cao", "SRD", idx
            )
        tutor = self.controle.buscar_tutor_por_cpf("22233344455")
        self.assertEqual(len(tutor.animais), 15)

    def test_buscar_animal_por_nome_e_cpf_sem_diferenciar_caixa(self):
        """Valida combinacao Lista + Lista na busca case-insensitive."""
        self.controle.cadastrar_tutor("Ana", "22233344455", "11988887777")
        self.controle.cadastrar_animal(
            "22233344455", "Bolinha", "Gato", "Persa", 4
        )
        pet = self.controle.buscar_animal("222.333.444-55", "  bolinha ")
        self.assertIsNotNone(pet)
        self.assertEqual(pet.raca, "Persa")
        self.assertIsNone(self.controle.buscar_animal("22233344455", "Rex"))

    def test_mesmo_nome_em_tutores_distintos_e_duplicado_no_mesmo(self):
        """Permite nomes iguais em tutores diferentes e bloqueia no mesmo."""
        self.controle.cadastrar_tutor("Ana", "11111111111", "1191")
        self.controle.cadastrar_tutor("Beto", "22222222222", "1192")
        self.controle.cadastrar_animal("11111111111", "Rex", "Cao", "Pug", 2)
        self.controle.cadastrar_animal("22222222222", "Rex", "Cao", "Boxer", 3)
        with self.assertRaises(ValueError):
            self.controle.cadastrar_animal("11111111111", "rex", "Cao", "X", 1)

    def test_rejeitar_idade_negativa_ou_booleana(self):
        """Garante que idade booleana ou negativa seja recusada."""
        self.controle.cadastrar_tutor("Ana", "11111111111", "1191")
        with self.assertRaises(ValueError):
            self.controle.cadastrar_animal("11111111111", "R", "Cao", "A", -1)
        with self.assertRaises(ValueError):
            self.controle.cadastrar_animal(
                "11111111111", "Mel", "Cao", "A", True
            )

    def test_remover_animal_e_remover_tutor(self):
        """Valida remocao de animal e remocao integral do tutor."""
        self.controle.cadastrar_tutor("Ana", "11111111111", "1191")
        self.controle.cadastrar_animal("11111111111", "Rex", "Cao", "Pug", 2)
        rem_pet = self.controle.remover_animal("11111111111", "Rex")
        self.assertEqual(rem_pet.nome, "Rex")
        self.assertIsNone(self.controle.buscar_animal("11111111111", "Rex"))
        rem_tut = self.controle.remover_tutor("11111111111")
        self.assertEqual(rem_tut.nome, "Ana")
        self.assertIsNone(self.controle.buscar_tutor_por_cpf("11111111111"))

    def test_remover_inexistentes_gera_erro(self):
        """Garante erro ao tentar remover tutor ou animal ausente."""
        with self.assertRaises(ValueError):
            self.controle.remover_tutor("99999999999")
        self.controle.cadastrar_tutor("Ana", "11111111111", "1191")
        with self.assertRaises(ValueError):
            self.controle.remover_animal("11111111111", "Fantasma")
