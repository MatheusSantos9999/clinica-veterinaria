"""Modulo utilitario para validacoes de texto, CPF e valores numericos."""

from math import isfinite


def validar_texto_obrigatorio(valor, nome_campo):
    """Valida que um campo textual e string nao vazia.

    Args:
        valor: Valor a ser validado.
        nome_campo: Nome legivel do campo para mensagens de erro.

    Returns:
        str: Texto limpo de espacos externos.

    Raises:
        ValueError: Se nao for string ou estiver em branco.
    """
    # Garante tipo textual e conteudo significativo
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{nome_campo} nao pode ser vazio.")
    return valor.strip()


def normalizar_chave(texto):
    """Normaliza um texto para comparacoes sem diferenciar maiusculas.

    Args:
        texto: String de entrada.

    Returns:
        str: Texto sem espacos extras e em minusculas.
    """
    return validar_texto_obrigatorio(texto, "Chave").lower()


def normalizar_cpf(cpf):
    """Remove pontuacao e valida se o CPF possui exatamente 11 digitos.

    Args:
        cpf: Texto representando o CPF com ou sem mascara.

    Returns:
        str: CPF contendo exatamente 11 digitos numericos.

    Raises:
        ValueError: Se o CPF nao possuir 11 digitos validos.
    """
    # Extrai somente digitos sem recorrer a listas built-in
    texto = validar_texto_obrigatorio(cpf, "CPF")
    digitos = _extrair_digitos(texto)
    if len(digitos) != 11:
        raise ValueError("CPF deve conter exatamente 11 digitos.")
    return digitos


def _extrair_digitos(texto):
    """Extrai caracteres numericos de uma string mantendo a ordem.

    Args:
        texto: String original a ser filtrada.

    Returns:
        str: Sequencia contendo apenas digitos de 0 a 9.
    """
    digitos = ""
    for caractere in texto:
        if caractere.isdigit():
            digitos += caractere
    return digitos


def validar_inteiro_nao_negativo(valor, nome_campo):
    """Valida se o valor e um inteiro maior ou igual a zero.

    Args:
        valor: Valor numerico a validar.
        nome_campo: Nome do campo para diagnostico de erro.

    Returns:
        int: Valor inteiro validado.

    Raises:
        ValueError: Se for booleano, nao inteiro ou negativo.
    """
    # Rejeita bool explicitamente pois bool herda de int em Python
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"{nome_campo} deve ser um numero inteiro.")
    if valor < 0:
        raise ValueError(f"{nome_campo} nao pode ser negativo.")
    return valor


def validar_inteiro_positivo(valor, nome_campo):
    """Valida se o valor e um inteiro estritamente positivo (> 0).

    Args:
        valor: Valor numerico a validar.
        nome_campo: Nome do campo para mensagem de erro.

    Returns:
        int: Valor inteiro positivo.

    Raises:
        ValueError: Se nao for inteiro ou for menor que 1.
    """
    inteiro = validar_inteiro_nao_negativo(valor, nome_campo)
    if inteiro <= 0:
        raise ValueError(f"{nome_campo} deve ser maior que zero.")
    return inteiro


def validar_valor_nao_negativo(valor, nome_campo):
    """Valida se um numero real (int ou float) e >= 0.

    Args:
        valor: Valor numerico a validar.
        nome_campo: Nome do campo para mensagem de erro.

    Returns:
        float: Valor convertido para float.

    Raises:
        ValueError: Se nao for numerico ou for negativo.
    """
    # Rejeita booleanos, nao numericos e valores nao finitos
    eh_numero = isinstance(valor, int) or isinstance(valor, float)
    if isinstance(valor, bool) or not eh_numero or not isfinite(valor):
        raise ValueError(f"{nome_campo} deve ser um numero finito.")
    if valor < 0:
        raise ValueError(f"{nome_campo} nao pode ser negativo.")
    return float(valor)
