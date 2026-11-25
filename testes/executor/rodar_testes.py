"""Modulo executor que descobre e roda toda a suite de testes."""

import io
import os
import sys
import unittest
from pathlib import Path


def executar_resumo_testes():
    """Executa toda a suite em modo silencioso e devolve linha de resumo.

    Returns:
        str: Resumo com total de testes, falhas e erros.
    """
    raiz = Path(__file__).resolve().parents[2]
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))
    suite = _carregar_suite(raiz)
    res = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    falhas = len(res.failures) + len(res.errors)
    status = "OK" if res.wasSuccessful() else "FALHOU"
    return f"{res.testsRun} testes | {falhas} falhas/erros ({status})"


def executar_todos_os_testes():
    """Localiza e executa todos os modulos test_*.py sem exigir __init__.py.

    Returns:
        int: Codigo 0 em sucesso total, 1 se qualquer teste falhar.
    """
    # Garante a raiz do projeto no sys.path para pacotes PEP 420
    raiz = Path(__file__).resolve().parents[2]
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))
    suite = _carregar_suite(raiz)
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if resultado.wasSuccessful() else 1


def _carregar_suite(raiz):
    """Monta a TestSuite carregando cada arquivo test_*.py pelo nome.

    Args:
        raiz: Caminho Path da raiz do repositorio.

    Returns:
        unittest.TestSuite: Suite agregada com todos os testes.
    """
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for modulo in _listar_modulos_teste(raiz):
        suite.addTests(loader.loadTestsFromName(modulo))
    return suite


def _listar_modulos_teste(raiz):
    """Converte cada arquivo test_*.py em nome pontilhado de modulo Python.

    Args:
        raiz: Path da raiz do projeto.

    Returns:
        Lista ordenada de nomes pontilhados de modulos de teste.
    """
    modulos = []
    for atual, _dirs, nomes in os.walk(raiz / "testes"):
        for nome in sorted(nomes):
            if nome.startswith("test_") and nome.endswith(".py"):
                rel = Path(atual, nome).relative_to(raiz).with_suffix("")
                modulos.append(".".join(rel.parts))
    return sorted(modulos)


if __name__ == "__main__":
    sys.exit(executar_todos_os_testes())
