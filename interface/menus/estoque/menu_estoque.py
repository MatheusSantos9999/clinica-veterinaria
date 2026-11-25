"""Modulo de menu interativo para controle de estoque em lotes FIFO."""

from interface.entrada.leitor_console import (
    ler_float,
    ler_inteiro,
    ler_texto,
)
from interface.exibicao.formatador_saida import (
    imprimir_erro,
    imprimir_lista,
    imprimir_sucesso,
    imprimir_titulo,
)
from modelos.estoque.dados_lote.dados_lote import DadosLote


class MenuEstoque:
    """Fornece interface de console para produtos, lotes, perdas e alertas."""

    def __init__(self, clinica):
        """Inicializa o submenu de estoque com referencia a clinica.

        Args:
            clinica: Instancia de ClinicaVeterinaria.
        """
        self._clinica = clinica

    def executar(self):
        """Executa o laco do submenu de estoque ate voltar."""
        while True:
            self._exibir_opcoes()
            opcao = ler_texto("Opcao: ")
            if opcao == "0":
                return
            self._processar_opcao(opcao)

    def _exibir_opcoes(self):
        """Exibe opcoes de gestao do estoque de medicamentos e vacinas."""
        imprimir_titulo("CONTROLE DE ESTOQUE (LISTA + FILA DE LOTES)")
        print("1 - Adicionar lote       | 2 - Listar produtos e lotes")
        print("3 - Descartar vencidos   | 4 - Ajustar inventario")
        print("5 - Ver perdas e alertas | 0 - Voltar")

    def _processar_opcao(self, opcao):
        """Despacha a acao selecionada tratando erros de validacao.

        Args:
            opcao: Codigo da opcao digitada.
        """
        try:
            self._despachar(opcao)
        except (ValueError, TypeError) as erro:
            imprimir_erro(erro)

    def _despachar(self, opcao):
        """Seleciona a operacao correspondente no controle de estoque.

        Args:
            opcao: Codigo da acao no submenu.
        """
        if opcao == "1":
            self._adicionar_lote()
        elif opcao == "2":
            self._listar_produtos()
        elif opcao == "3":
            self._descartar_vencidos()
        else:
            self._despachar_restante(opcao)

    def _despachar_restante(self, opcao):
        """Seleciona opcoes 4 e 5 ou reporta opcao invalida.

        Args:
            opcao: Codigo da acao no submenu.
        """
        if opcao == "4":
            self._ajustar_inventario()
        elif opcao == "5":
            self._ver_perdas_e_alertas()
        else:
            imprimir_erro("Opcao invalida.")

    def _adicionar_lote(self):
        """Le dados do produto e do lote e enfileira no estoque."""
        codigo = ler_texto("Codigo do produto: ")
        nome = ler_texto("Nome do produto: ")
        minimo = ler_inteiro("Quantidade minima para alerta: ")
        dados = self._ler_dados_lote()
        lote = self._clinica.estoque.adicionar_lote(
            codigo, nome, dados, minimo
        )
        imprimir_sucesso(f"Lote adicionado: {lote}")

    def _ler_dados_lote(self):
        """Coleta dados comerciais e datas para compor DadosLote.

        Returns:
            DadosLote: Instancia validada pronta para insercao.
        """
        fornecedor = ler_texto("Fornecedor: ")
        p_compra = ler_float("Preco de compra: ")
        p_venda = ler_float("Preco de venda: ")
        d_compra = ler_texto("Data compra (DD/MM/AAAA): ")
        d_val = ler_texto("Data validade (DD/MM/AAAA): ")
        qtd = ler_inteiro("Quantidade: ")
        return DadosLote(fornecedor, p_compra, p_venda, d_compra, d_val, qtd)

    def _listar_produtos(self):
        """Lista todos os produtos cadastrados com seus respectivos lotes."""
        if self._clinica.estoque.produtos.esta_vazia():
            print("Estoque vazio.")
            return
        for produto in self._clinica.estoque.produtos:
            print(f"\n{produto}")
            imprimir_lista(produto.lotes, "  Sem lotes disponiveis.")

    def _descartar_vencidos(self):
        """Descarta lotes expirados e exibe as perdas geradas."""
        perdas = self._clinica.estoque.descartar_vencidos()
        imprimir_lista(perdas, "Nenhum lote vencido encontrado.")

    def _ajustar_inventario(self):
        """Permite editar manualmente o saldo de um lote especifico."""
        codigo = ler_texto("Codigo do produto: ")
        num_lote = ler_inteiro("Numero do lote: ")
        nova_qtd = ler_inteiro("Nova quantidade (>= 0): ")
        lote = self._clinica.estoque.ajustar_quantidade(
            codigo, num_lote, nova_qtd
        )
        imprimir_sucesso(f"Inventario ajustado: {lote}")

    def _ver_perdas_e_alertas(self):
        """Exibe perdas por vencimento e alertas de estoque baixo."""
        print("\nPerdas registradas:")
        imprimir_lista(self._clinica.estoque.perdas, "  Nenhuma perda.")
        print("\nAlertas de estoque baixo:")
        imprimir_lista(self._clinica.estoque.alertas, "  Nenhum alerta.")
