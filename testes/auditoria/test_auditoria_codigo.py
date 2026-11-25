"""Auditoria AST agressiva de todas as restricoes arquiteturais e estilo."""

import ast
import os
import unittest
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
PASTAS_IGNORADAS = {".git", "__pycache__", ".venv", "venv"}
BUILTINS_PROIBIDOS = {"list", "dict", "set", "tuple"}
MODULOS_PROIBIDOS = {"collections", "heapq", "queue"}


def listar_arquivos_python(apenas_producao=False):
    """Coleta todos os arquivos .py do projeto ignorando caches.

    Args:
        apenas_producao: Se True, exclui arquivos dentro de testes/.

    Returns:
        Lista de objetos Path encontrados.
    """
    arquivos = []
    for atual, dirs, nomes in os.walk(RAIZ_PROJETO):
        dirs[:] = [d for d in dirs if d not in PASTAS_IGNORADAS]
        _coletar_py_da_pasta(Path(atual), nomes, apenas_producao, arquivos)
    return arquivos


def _coletar_py_da_pasta(pasta, nomes, apenas_producao, destino):
    """Filtra arquivos .py de uma pasta respeitando escopo de producao.

    Args:
        pasta: Path da pasta atual.
        nomes: Nomes de arquivos na pasta.
        apenas_producao: Flag para ignorar pasta testes/.
        destino: Acumulador de caminhos.
    """
    rel = pasta.relative_to(RAIZ_PROJETO)
    if apenas_producao and rel.parts and rel.parts[0] == "testes":
        return
    for nome in nomes:
        if nome.endswith(".py"):
            destino.append(pasta / nome)


def contar_linhas_funcao(no_funcao, linhas_arquivo):
    """Conta linhas nao vazias de uma funcao excluindo sua docstring.

    Args:
        no_funcao: No AST FunctionDef ou AsyncFunctionDef.
        linhas_arquivo: Lista com todas as linhas do arquivo.

    Returns:
        int: Total de linhas (cabecalho + comentarios + codigo).
    """
    # Identifica intervalo da docstring para desconsidera-lo na contagem
    ini_doc, fim_doc = _intervalo_docstring(no_funcao)
    total = 0
    for idx in range(no_funcao.lineno, no_funcao.end_lineno + 1):
        if ini_doc <= idx <= fim_doc:
            continue
        if linhas_arquivo[idx - 1].strip():
            total += 1
    return total


def _intervalo_docstring(no_funcao):
    """Retorna o par (inicio, fim) de linhas da docstring de uma funcao.

    Args:
        no_funcao: No AST da funcao avaliada.

    Returns:
        Par de inteiros (inicio, fim) ou (-1, -1) se ausente.
    """
    primeiro = no_funcao.body[0] if no_funcao.body else None
    eh_doc = (
        isinstance(primeiro, ast.Expr)
        and isinstance(primeiro.value, ast.Constant)
        and isinstance(primeiro.value.value, str)
    )
    if eh_doc:
        return primeiro.lineno, primeiro.end_lineno
    return -1, -1


def verificar_colecoes_builtin(arvore, caminho):
    """Detecta uso de colecoes built-in proibidas em codigo de producao.

    Args:
        arvore: AST parseada do arquivo.
        caminho: Caminho relativo para diagnostico.

    Returns:
        Lista de mensagens descrevendo violacoes encontradas.
    """
    erros = []
    for no in ast.walk(arvore):
        _checar_no_proibido(no, caminho, erros)
    return erros


def _checar_no_proibido(no, caminho, erros):
    """Avalia um unico no AST contra regras de proibicao de built-ins.

    Args:
        no: No AST inspecionado.
        caminho: Caminho relativo do arquivo.
        erros: Lista acumuladora de erros.
    """
    tipos = (
        ast.List, ast.Dict, ast.Set,
        ast.ListComp, ast.DictComp, ast.SetComp,
    )
    if isinstance(no, tipos):
        erros.append(f"{caminho}:{no.lineno} usa {type(no).__name__}")
    _checar_chamada_ou_import(no, caminho, erros)


def _checar_chamada_ou_import(no, caminho, erros):
    """Verifica chamadas a list/dict/set/tuple ou imports proibidos.

    Args:
        no: No AST inspecionado.
        caminho: Caminho relativo do arquivo.
        erros: Lista acumuladora de erros.
    """
    if isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
        if no.func.id in BUILTINS_PROIBIDOS:
            erros.append(f"{caminho}:{no.lineno} chama {no.func.id}()")
    _checar_imports_proibidos(no, caminho, erros)


def _checar_imports_proibidos(no, caminho, erros):
    """Detecta importacoes de colecoes padrao como collections ou queue.

    Args:
        no: No AST inspecionado.
        caminho: Caminho relativo do arquivo.
        erros: Lista acumuladora de erros.
    """
    if isinstance(no, ast.Import):
        for alias in no.names:
            if alias.name.split(".")[0] in MODULOS_PROIBIDOS:
                erros.append(f"{caminho}:{no.lineno} importa {alias.name}")
    if isinstance(no, ast.ImportFrom) and no.module:
        if no.module.split(".")[0] in MODULOS_PROIBIDOS:
            erros.append(f"{caminho}:{no.lineno} importa {no.module}")


class TestAuditoriaCodigo(unittest.TestCase):
    """Suite de auditoria rigorosa dos requisitos estruturais e de estilo."""

    def test_main_obrigatorio_na_raiz(self):
        """Garante que o arquivo main.py exista na raiz do projeto."""
        self.assertTrue((RAIZ_PROJETO / "main.py").is_file())

    def test_no_maximo_um_arquivo_py_por_pasta(self):
        """Garante que nenhuma pasta possua mais de um arquivo .py."""
        violacoes = []
        for atual, dirs, nomes in os.walk(RAIZ_PROJETO):
            dirs[:] = [d for d in dirs if d not in PASTAS_IGNORADAS]
            pys = [n for n in nomes if n.endswith(".py")]
            if len(pys) > 1:
                violacoes.append(f"{atual}: {pys}")
        self.assertEqual(violacoes, [], f"Pastas com >1 .py: {violacoes}")

    def test_funcoes_ate_dez_linhas_em_todo_projeto(self):
        """Garante que toda funcao/metodo tenha no maximo 10 linhas uteis."""
        violacoes = []
        for arq in listar_arquivos_python(apenas_producao=False):
            self._auditar_linhas_arquivo(arq, violacoes)
        self.assertEqual(violacoes, [], "\n".join(violacoes))

    def _auditar_linhas_arquivo(self, arq, violacoes):
        """Inspeciona todas as funcoes de um arquivo quanto ao limite de 10."""
        texto = arq.read_text(encoding="utf-8")
        linhas = texto.splitlines()
        arvore = ast.parse(texto)
        rel = arq.relative_to(RAIZ_PROJETO)
        for no in ast.walk(arvore):
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qtd = contar_linhas_funcao(no, linhas)
                if qtd > 10:
                    violacoes.append(f"{rel}:{no.lineno} {no.name}={qtd}")

    def test_docstrings_em_modulos_classes_e_funcoes(self):
        """Garante docstrings obrigatorias em modulos, classes e metodos."""
        violacoes = []
        for arq in listar_arquivos_python(apenas_producao=False):
            self._auditar_docstrings_arquivo(arq, violacoes)
        self.assertEqual(violacoes, [], "\n".join(violacoes))

    def _auditar_docstrings_arquivo(self, arq, violacoes):
        """Verifica presenca de docstring em todos os nos documentaveis."""
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
        rel = arq.relative_to(RAIZ_PROJETO)
        if not ast.get_docstring(arvore):
            violacoes.append(f"{rel}: modulo sem docstring")
        tipos = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        for no in ast.walk(arvore):
            if isinstance(no, tipos) and not ast.get_docstring(no):
                violacoes.append(f"{rel}:{no.lineno} {no.name} sem docstring")

    def test_sem_colecoes_builtin_em_producao(self):
        """Garante ausencia de list/dict/set/tuple no codigo de producao."""
        violacoes = []
        for arq in listar_arquivos_python(apenas_producao=True):
            arvore = ast.parse(arq.read_text(encoding="utf-8"))
            rel = str(arq.relative_to(RAIZ_PROJETO))
            violacoes.extend(verificar_colecoes_builtin(arvore, rel))
        self.assertEqual(violacoes, [], "\n".join(violacoes))

    def test_largura_maxima_de_linha_79_caracteres(self):
        """Garante comentarios e codigo curtos cabendo na tela."""
        violacoes = []
        for arq in listar_arquivos_python(apenas_producao=False):
            self._auditar_largura_arquivo(arq, violacoes)
        self.assertEqual(violacoes, [], "\n".join(violacoes))

    def test_nenhum_init_py_presente(self):
        """Confirma uso limpo de pacotes PEP 420 sem __init__.py."""
        inits = [
            str(arq.relative_to(RAIZ_PROJETO))
            for arq in listar_arquivos_python(apenas_producao=False)
            if arq.name == "__init__.py"
        ]
        self.assertEqual(inits, [])

    def _auditar_largura_arquivo(self, arq, violacoes):
        """Verifica se alguma linha excede 79 caracteres."""
        rel = arq.relative_to(RAIZ_PROJETO)
        for num, linha in enumerate(
            arq.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if len(linha) > 79:
                violacoes.append(f"{rel}:{num} ({len(linha)} chars)")
