"""Modulo com funcoes auxiliares para formatacao de saida no console."""


def imprimir_titulo(texto):
    """Imprime um cabecalho visual destacado para secoes do menu.

    Args:
        texto: Titulo da secao a exibir.
    """
    linha = "=" * 56
    print(f"\n{linha}\n{texto}\n{linha}")


def imprimir_lista(itens, mensagem_vazia="Nenhum registro encontrado."):
    """Imprime todos os elementos de uma estrutura iteravel propria.

    Args:
        itens: Estrutura iteravel propria (Lista, Fila ou Pilha).
        mensagem_vazia: Mensagem exibida quando nao ha elementos.
    """
    # Percorre a estrutura propria sem converter para list built-in
    if len(itens) == 0:
        print(mensagem_vazia)
        return
    for elemento in itens:
        print(f"  - {elemento}")


def imprimir_sucesso(mensagem):
    """Imprime uma mensagem de confirmacao formatada.

    Args:
        mensagem: Texto de sucesso.
    """
    print(f"[OK] {mensagem}")


def imprimir_erro(erro):
    """Imprime uma mensagem de erro amigavel sem encerrar o sistema.

    Args:
        erro: Excecao ou texto descritivo da falha.
    """
    print(f"[ERRO] {erro}")
