"""Modulo utilitario para manipulacao e validacao de datas e horarios."""

from datetime import date, datetime


def obter_data_hora_atual():
    """Retorna a data e hora atual formatada no padrao brasileiro.

    Returns:
        str: Carimbo no formato DD/MM/AAAA HH:MM:SS.
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def obter_data_atual():
    """Retorna a data atual do sistema como objeto date.

    Returns:
        date: Data corrente sem componente de horario.
    """
    return date.today()


def resolver_data(data_referencia=None):
    """Converte data opcional ou devolve a data corrente do sistema.

    Args:
        data_referencia: Data opcional como string, date ou None.

    Returns:
        date: Data de referencia pronta para comparacoes.
    """
    if data_referencia is None:
        return obter_data_atual()
    return converter_data(data_referencia)


def converter_data(valor):
    """Converte string DD/MM/AAAA, AAAA-MM-DD ou date para date.

    Args:
        valor: String de data ou instancia de date/datetime.

    Returns:
        date: Objeto date correspondente ao valor informado.

    Raises:
        ValueError: Se o formato da data for invalido.
    """
    # Aceita objetos date ou datetime diretamente
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return _analisar_texto_data(valor)


def _analisar_texto_data(texto):
    """Interpreta texto de data nos formatos BR ou ISO.

    Args:
        texto: String contendo a data.

    Returns:
        date: Data convertida.

    Raises:
        ValueError: Quando o texto nao representa data valida.
    """
    # Tenta formato brasileiro primeiro e depois ISO
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Data deve ser informada como texto ou date.")
    limpo = texto.strip()
    try:
        return datetime.strptime(limpo, "%d/%m/%Y").date()
    except ValueError:
        return _analisar_iso(limpo)


def _analisar_iso(texto):
    """Converte string no formato ISO AAAA-MM-DD para date.

    Args:
        texto: String no formato AAAA-MM-DD.

    Returns:
        date: Data convertida.

    Raises:
        ValueError: Se a data for invalida em ambos os formatos.
    """
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError as erro:
        msg = "Data invalida. Use DD/MM/AAAA ou AAAA-MM-DD."
        raise ValueError(msg) from erro


def formatar_data(valor):
    """Formata uma data para exibicao em DD/MM/AAAA.

    Args:
        valor: Data em string ou objeto date.

    Returns:
        str: Data formatada como DD/MM/AAAA.
    """
    return converter_data(valor).strftime("%d/%m/%Y")


def esta_vencido(data_validade, data_referencia=None):
    """Verifica se uma data de validade ja expirou.

    Args:
        data_validade: Data limite de validade do produto.
        data_referencia: Data usada na comparacao (padrao hoje).

    Returns:
        bool: True se data_validade for anterior a referencia.
    """
    # Produto e considerado vencido quando validade < referencia
    ref = obter_data_atual() if data_referencia is None else data_referencia
    return converter_data(data_validade) < converter_data(ref)
