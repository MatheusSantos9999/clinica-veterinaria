"""Modulo de servico para filas de espera (Fila + Fila) e consultorios."""

from estruturas.fila.fila_encadeada import FilaEncadeada
from estruturas.lista.lista_encadeada import ListaEncadeada
from modelos.atendimento.consultorio.consultorio import Consultorio
from utilitarios.validacao.validador_entrada import (
    normalizar_chave,
    normalizar_cpf,
    validar_inteiro_positivo,
)


class ControleAtendimento:
    """Gerencia espera prioritaria (Fila + Fila) e salas limitadas.

    Attributes:
        fila_emergencia: FilaEncadeada prioritaria para emergencias.
        fila_normal: FilaEncadeada padrao por ordem de chegada.
        consultorios: ListaEncadeada com os consultorios disponiveis.
    """

    def __init__(self, quantidade_consultorios=2):
        """Inicializa as duas filas FIFO e cria os consultorios limitados.

        Args:
            quantidade_consultorios: Numero de salas da clinica (> 0).
        """
        # Combinacao Fila + Fila somada a lista limitada de consultorios
        total = validar_inteiro_positivo(
            quantidade_consultorios, "Quantidade de consultorios"
        )
        self.fila_emergencia = FilaEncadeada()
        self.fila_normal = FilaEncadeada()
        self.consultorios = ListaEncadeada()
        self._criar_consultorios(total)

    def _criar_consultorios(self, total):
        """Popula a lista de consultorios numerados de 1 ate total.

        Args:
            total: Quantidade de consultorios a instanciar.
        """
        numero = 1
        while numero <= total:
            self.consultorios.adicionar(Consultorio(numero))
            numero += 1

    def registrar_chegada(self, ficha_espera):
        """Insere um animal na fila de emergencia ou na fila normal.

        Args:
            ficha_espera: FichaEspera do animal recem-chegado.

        Raises:
            ValueError: Se o animal ja estiver na espera ou em sala.
        """
        # Evita duplicacao do mesmo animal em espera ou atendimento
        chave = ficha_espera.chave_animal()
        if self._chave_ativa(chave):
            raise ValueError("Animal ja esta em espera ou em consultorio.")
        if ficha_espera.emergencia:
            self.fila_emergencia.enfileirar(ficha_espera)
        else:
            self.fila_normal.enfileirar(ficha_espera)

    def indicar_proximo(self):
        """Indica automaticamente o proximo animal sem remove-lo da fila.

        Returns:
            FichaEspera: Proxima ficha prioritaria ou None se sem espera.
        """
        # Prioriza emergencia; se vazia, consulta a fila normal
        if not self.fila_emergencia.esta_vazia():
            return self.fila_emergencia.espiar()
        return self.fila_normal.espiar()

    def obter_consultorio_livre(self):
        """Busca o primeiro consultorio disponivel na clinica.

        Returns:
            Consultorio: Consultorio livre ou None se todos ocupados.
        """
        return self.consultorios.buscar(lambda sala: not sala.ocupado)

    def chamar_proximo(self, numero_prontuario):
        """Chama o proximo animal da fila para um consultorio livre.

        Args:
            numero_prontuario: Numero do prontuario a vincular a sala.

        Returns:
            Consultorio: Sala agora ocupada pelo animal chamado.

        Raises:
            ValueError: Se nao houver consultorio livre ou fila estiver vazia.
        """
        # Verifica vaga de consultorio e retira proximo respeitando prioridade
        sala = self.obter_consultorio_livre()
        if sala is None:
            raise ValueError("Nao ha consultorios livres no momento.")
        ficha = self._desenfileirar_proximo()
        sala.ocupar(ficha, numero_prontuario)
        return sala

    def _desenfileirar_proximo(self):
        """Retira a proxima ficha dando prioridade a fila de emergencia.

        Returns:
            FichaEspera: Ficha removida da fila correspondente.

        Raises:
            ValueError: Quando ambas as filas estiverem vazias.
        """
        if not self.fila_emergencia.esta_vazia():
            return self.fila_emergencia.desenfileirar()
        if not self.fila_normal.esta_vazia():
            return self.fila_normal.desenfileirar()
        raise ValueError("Nao ha animais aguardando atendimento.")

    def liberar_consultorio(self, numero_consultorio):
        """Libera um consultorio e indica automaticamente o proximo animal.

        Args:
            numero_consultorio: Numero da sala a ser liberada.

        Returns:
            FichaEspera: Proximo animal aguardando na espera ou None.

        Raises:
            ValueError: Se o consultorio nao existir ou ja estiver livre.
        """
        # Libera a sala e devolve indicacao automatica do proximo
        sala = self.buscar_consultorio(numero_consultorio)
        if sala is None:
            raise ValueError("Consultorio informado nao existe.")
        sala.liberar()
        return self.indicar_proximo()

    def buscar_consultorio(self, numero_consultorio):
        """Localiza um consultorio pelo seu numero.

        Args:
            numero_consultorio: Numero da sala procurada.

        Returns:
            Consultorio: Instancia localizada ou None.
        """
        return self.consultorios.buscar(
            lambda sala: sala.numero == numero_consultorio
        )

    def total_em_espera(self):
        """Retorna a soma de animais nas filas de emergencia e normal.

        Returns:
            int: Quantidade total de animais aguardando vaga.
        """
        return len(self.fila_emergencia) + len(self.fila_normal)

    def animal_ativo(self, cpf_tutor, nome_animal):
        """Verifica se o animal esta em espera ou ocupando consultorio.

        Args:
            cpf_tutor: CPF do tutor.
            nome_animal: Nome do animal.

        Returns:
            bool: True se estiver em fila ou em atendimento ativo.
        """
        chave = f"{normalizar_cpf(cpf_tutor)}:{normalizar_chave(nome_animal)}"
        return self._chave_ativa(chave)

    def _chave_ativa(self, chave):
        """Verifica presenca da chave nas duas filas e nos consultorios.

        Args:
            chave: Chave composta cpf:nome_normalizado.

        Returns:
            bool: True se ja existir registro ativo para a chave.
        """
        em_fila = self._chave_em_fila(chave)
        em_sala = self.consultorios.buscar(
            lambda s: s.ocupado and s.ficha_atual.chave_animal() == chave
        )
        return em_fila or em_sala is not None

    def _chave_em_fila(self, chave):
        """Verifica se a chave esta aguardando na emergencia ou normal.

        Args:
            chave: Chave composta cpf:nome_normalizado.

        Returns:
            bool: True se encontrada em qualquer uma das duas filas.
        """
        em_e = self.fila_emergencia.buscar(lambda f: f.chave_animal() == chave)
        em_n = self.fila_normal.buscar(lambda f: f.chave_animal() == chave)
        return em_e is not None or em_n is not None
