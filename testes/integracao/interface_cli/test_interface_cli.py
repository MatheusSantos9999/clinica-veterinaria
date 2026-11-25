"""Testes de integracao do ponto de entrada main.py e da interface CLI."""

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from interface.menus.principal.menu_principal import MenuPrincipal

RAIZ_PROJETO = Path(__file__).resolve().parents[3]


class TestInterfaceCli(unittest.TestCase):
    """Valida execucao de main.py e fluxos reais nos menus de console."""

    def test_main_flag_simulacao_executa_com_sucesso(self):
        """Roda 'python main.py --simulacao' verificando codigo 0 e saida."""
        proc = subprocess.run(
            [sys.executable, str(RAIZ_PROJETO / "main.py"), "--simulacao"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("PASSO 5: ALTA, FECHAMENTO", proc.stdout)
        self.assertIn("Total: R$ 260.00", proc.stdout)

    def test_main_flag_demo_executa_regras_e_suite(self):
        """Roda 'python main.py --demo' verificando simulacao e regras."""
        env = dict(os.environ, CLINICA_EM_TESTE="1")
        proc = subprocess.run(
            [sys.executable, str(RAIZ_PROJETO / "main.py"), "--demo"],
            capture_output=True, text=True, check=False, env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Regra validada (bloqueio)", proc.stdout)
        self.assertIn("Ajuste de inventario VAC01", proc.stdout)

    def test_menu_principal_executa_simulacao_resumo_e_sai(self):
        """Simula interacao no MenuPrincipal com opcao invalida, 1, 6 e 0."""
        texto = self._executar_menu(["99", "1", "6", "0"])[0]
        self.assertIn("Opcao invalida", texto)
        self.assertIn("RESUMO GERAL DA CLINICA", texto)
        self.assertIn("Encerrando sistema", texto)

    def test_fluxo_interativo_submenu_tutores_e_atendimento(self):
        """Exercita cadastro de tutor/animal e fila via menus de console."""
        respostas = [
            "2", "1", "Joana", "11122233344", "1199", "4", "11122233344",
            "Bidu", "Cao", "Poodle", "5", "0", "3", "1", "11122233344",
            "Bidu", "Vomito", "s", "2", "0", "0",
        ]
        _, menu = self._executar_menu(respostas)
        prox = menu.clinica.atendimento.indicar_proximo()
        self.assertEqual(len(menu.clinica.tutores.tutores), 1)
        self.assertEqual(prox.nome_animal, "Bidu")

    def test_fluxo_interativo_estoque_e_prontuario_completo(self):
        """Exercita estoque, prontuario, diagnostico e pagamento."""
        respostas = self._respostas_cadastro() + self._respostas_atendimento()
        texto, menu = self._executar_menu(respostas)
        self.assertIn("Consumo Prontuario #1", texto)
        total = menu.clinica.pagamentos.calcular_total_recebido()
        self.assertEqual(total, 110.0)

    def _respostas_cadastro(self):
        """Entradas para cadastrar tutor, animal e lote de medicamento."""
        return [
            "2", "1", "Ana", "11122233344", "1199", "4", "11122233344",
            "Rex", "Cao", "SRD", "3", "0", "4", "1", "M1", "Med", "2",
            "Forn", "10", "30", "01/01/2026", "01/01/2028", "5", "0",
        ]

    def _respostas_atendimento(self):
        """Entradas para fila, prontuario, diagnostico, alta e pagamento."""
        return [
            "3", "1", "11122233344", "Rex", "Dor", "n", "3", "Dra. Ana", "0",
            "5", "3", "1", "DIG-01", "4", "1", "M1", "1", "6", "1",
            "Consulta", "80", "OK", "9", "1", "10", "1", "Ana", "PIX",
            "1", "11", "0", "0",
        ]

    def _executar_menu(self, respostas):
        """Executa MenuPrincipal com entradas simuladas e captura stdout.

        Args:
            respostas: Lista de strings simulando digitacao no console.

        Returns:
            Par (texto_saida, menu) apos encerrar o laco.
        """
        menu = MenuPrincipal()
        saida = io.StringIO()
        with patch("builtins.input", side_effect=iter(respostas)):
            with redirect_stdout(saida):
                menu.executar()
        return saida.getvalue(), menu
