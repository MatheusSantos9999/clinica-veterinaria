"""Modulo com funcoes seguras para leitura de entradas no console."""


def ler_texto(mensagem):
    """Le um texto nao vazio do console removendo espacos externos.

    Args:
        mensagem: Texto de orientacao exibido ao usuario.

    Returns:
        str: Texto digitado pelo usuario.
    """
    return input(mensagem).strip()


def ler_inteiro(mensagem):
    """Le e converte uma entrada do console para numero inteiro.

    Args:
        mensagem: Texto exibido ao usuario.

    Returns:
        int: Numero inteiro informado.

    Raises:
        ValueError: Se o texto digitado nao representar um inteiro.
    """
    bruto = input(mensagem).strip()
    try:
        return int(bruto)
    except ValueError as erro:
        raise ValueError("Digite um numero inteiro valido.") from erro


def ler_float(mensagem):
    """Le e converte um valor monetario ou decimal (aceita virgula).

    Args:
        mensagem: Texto exibido ao usuario.

    Returns:
        float: Valor decimal convertido.

    Raises:
        ValueError: Se o valor informado nao for numerico.
    """
    # Aceita virgula ou ponto como separador decimal
    bruto = input(mensagem).strip().replace(",", ".")
    try:
        return float(bruto)
    except ValueError as erro:
        raise ValueError("Digite um valor numerico valido.") from erro


def ler_confirmacao(mensagem):
    """Interpreta resposta S/N do usuario retornando booleano.

    Args:
        mensagem: Pergunta exibida ao usuario.

    Returns:
        bool: True se iniciar com 's', False caso contrario.
    """
    resposta = input(mensagem).strip().lower()
    return resposta == "s" or resposta == "sim"
