"""Modulo de servico para gestao de prontuarios abertos e historico."""

from estruturas.lista.lista_encadeada import ListaEncadeada
from estruturas.pilha.pilha_encadeada import PilhaEncadeada
from modelos.prontuario.prontuario.prontuario import Prontuario
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    normalizar_cpf,
)


class ControleProntuarios:
    """Gerencia prontuarios abertos em Lista e encerrados em Pilha LIFO.

    Attributes:
        prontuarios_abertos: ListaEncadeada de prontuarios em andamento.
        prontuarios_fechados: PilhaEncadeada de prontuarios encerrados.
    """

    def __init__(self):
        """Inicializa lista de abertos, pilha de fechados e contador."""
        # Abertos exigem busca aleatoria; fechados privilegiam mais recente
        self.prontuarios_abertos = ListaEncadeada()
        self.prontuarios_fechados = PilhaEncadeada()
        self._proximo_numero = 1

    def proximo_numero(self):
        """Consulta o proximo numero sequencial disponivel sem consumi-lo.

        Returns:
            int: Proximo numero que sera atribuido na abertura.
        """
        return self._proximo_numero

    def abrir_prontuario(self, ficha_espera, veterinario, numero_consultorio):
        """Abre um novo prontuario e o registra na lista de abertos.

        Args:
            ficha_espera: FichaEspera que originou o atendimento.
            veterinario: Nome do veterinario responsavel.
            numero_consultorio: Numero do consultorio ocupado.

        Returns:
            Prontuario: Nova instancia aberta e cadastrada.
        """
        # Atribui numero sequencial unico e insere nos abertos
        prontuario = Prontuario(
            self._proximo_numero, ficha_espera, veterinario, numero_consultorio
        )
        self._proximo_numero += 1
        self.prontuarios_abertos.adicionar(prontuario)
        return prontuario

    def buscar_aberto(self, numero):
        """Localiza um prontuario aberto pelo seu numero.

        Args:
            numero: Numero identificador do prontuario.

        Returns:
            Prontuario: Prontuario encontrado ou None.
        """
        return self.prontuarios_abertos.buscar(
            lambda item: item.numero == numero
        )

    def buscar_por_numero(self, numero):
        """Localiza um prontuario entre os abertos ou fechados.

        Args:
            numero: Numero do prontuario procurado.

        Returns:
            Prontuario: Instancia encontrada ou None.
        """
        # Pesquisa primeiro nos abertos e depois na pilha de fechados
        aberto = self.buscar_aberto(numero)
        if aberto is not None:
            return aberto
        return self._buscar_fechado(numero)

    def _buscar_fechado(self, numero):
        """Percorre a pilha de prontuarios fechados procurando o numero.

        Args:
            numero: Numero do prontuario desejado.

        Returns:
            Prontuario: Instancia encontrada ou None.
        """
        for prontuario in self.prontuarios_fechados:
            if prontuario.numero == numero:
                return prontuario
        return None

    def exigir_aberto(self, numero):
        """Recupera um prontuario aberto ou levanta erro se indisponivel.

        Args:
            numero: Numero do prontuario.

        Returns:
            Prontuario: Prontuario aberto encontrado.

        Raises:
            ValueError: Se o prontuario nao existir ou ja estiver fechado.
        """
        # Diferencia prontuario inexistente de prontuario ja encerrado
        prontuario = self.buscar_aberto(numero)
        if prontuario is not None:
            return prontuario
        if self._buscar_fechado(numero) is not None:
            raise ValueError(f"Prontuario #{numero} ja esta fechado.")
        raise ValueError(f"Prontuario #{numero} nao encontrado.")

    def adicionar_medicamento(self, numero, item_medicamento):
        """Inclui um medicamento em um prontuario aberto.

        Args:
            numero: Numero do prontuario.
            item_medicamento: Instancia de ItemMedicamento.
        """
        prontuario = self.exigir_aberto(numero)
        prontuario.adicionar_medicamento(item_medicamento)

    def remover_medicamento(self, numero, codigo_produto):
        """Remove um medicamento de um prontuario antes do fechamento.

        Args:
            numero: Numero do prontuario.
            codigo_produto: Codigo do medicamento a remover.

        Returns:
            ItemMedicamento: Item removido.

        Raises:
            ValueError: Se medicamento nao constar no prontuario.
        """
        prontuario = self.exigir_aberto(numero)
        removido = prontuario.remover_medicamento(codigo_produto)
        if removido is None:
            raise ValueError("Medicamento nao encontrado no prontuario.")
        return removido

    def adicionar_procedimento(self, numero, procedimento):
        """Inclui um procedimento em um prontuario aberto.

        Args:
            numero: Numero do prontuario.
            procedimento: Instancia de Procedimento.
        """
        prontuario = self.exigir_aberto(numero)
        prontuario.adicionar_procedimento(procedimento)

    def remover_procedimento(self, numero, nome_procedimento):
        """Remove um procedimento de um prontuario antes do fechamento.

        Args:
            numero: Numero do prontuario.
            nome_procedimento: Nome do procedimento nao autorizado.

        Returns:
            Procedimento: Procedimento removido.

        Raises:
            ValueError: Se procedimento nao constar no prontuario.
        """
        prontuario = self.exigir_aberto(numero)
        removido = prontuario.remover_procedimento(nome_procedimento)
        if removido is None:
            raise ValueError("Procedimento nao encontrado no prontuario.")
        return removido

    def desfazer_ultima_acao(self, numero):
        """Desfaz a ultima alteracao do prontuario via pilha de historico.

        Args:
            numero: Numero do prontuario aberto.

        Returns:
            AcaoHistorico: Acao revertida ou None se pilha vazia.
        """
        prontuario = self.exigir_aberto(numero)
        return prontuario.desfazer_ultima_acao()

    def dar_alta(self, numero):
        """Registra a alta clinica do animal no prontuario informado.

        Args:
            numero: Numero do prontuario aberto.

        Returns:
            Prontuario: Prontuario atualizado com alta concedida.
        """
        prontuario = self.exigir_aberto(numero)
        prontuario.conceder_alta()
        return prontuario

    def encerrar_prontuario(self, numero):
        """Fecha um prontuario com alta e move-o para a pilha de fechados.

        Args:
            numero: Numero do prontuario a encerrar.

        Returns:
            Prontuario: Prontuario encerrado e empilhado.
        """
        # Valida alta, marca fechado, retira dos abertos e empilha
        prontuario = self.exigir_aberto(numero)
        prontuario.marcar_fechado()
        self.prontuarios_abertos.remover_por_criterio(
            lambda item: item.numero == numero
        )
        self.prontuarios_fechados.empilhar(prontuario)
        return prontuario

    def animal_com_prontuario_aberto(self, cpf_tutor, nome_animal):
        """Verifica se determinado animal possui prontuario em aberto.

        Args:
            cpf_tutor: CPF normalizado do tutor.
            nome_animal: Nome do animal.

        Returns:
            bool: True se existir prontuario aberto para este animal.
        """
        cpf = normalizar_cpf(cpf_tutor)
        chave = normalizar_chave(nome_animal)
        achado = self.prontuarios_abertos.buscar(
            lambda p: p.cpf_tutor == cpf and p.nome_animal.lower() == chave
        )
        return achado is not None
