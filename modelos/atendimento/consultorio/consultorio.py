"""Modulo que define a entidade Consultorio da clinica veterinaria."""

from utilitarios.validacao.validador_entrada import validar_inteiro_positivo


class Consultorio:
    """Representa uma sala de atendimento veterinario com estado proprio.

    Attributes:
        numero: Identificador numerico do consultorio.
        ocupado: True quando ha um animal em atendimento.
        ficha_atual: FichaEspera em atendimento ou None.
        numero_prontuario: Numero do prontuario ativo ou None.
    """

    def __init__(self, numero):
        """Inicializa um consultorio disponivel.

        Args:
            numero: Numero inteiro positivo do consultorio.
        """
        # Inicia o consultorio livre e sem prontuario associado
        self.numero = validar_inteiro_positivo(numero, "Numero consultorio")
        self.ocupado = False
        self.ficha_atual = None
        self.numero_prontuario = None

    def ocupar(self, ficha, numero_prontuario):
        """Ocupa o consultorio com uma ficha e prontuario ativo.

        Args:
            ficha: FichaEspera do animal chamado.
            numero_prontuario: Numero do prontuario aberto.

        Raises:
            ValueError: Se o consultorio ja estiver ocupado.
        """
        # Impede sobreposicao de atendimentos na mesma sala
        if self.ocupado:
            raise ValueError(f"Consultorio {self.numero} ja esta ocupado.")
        self.ocupado = True
        self.ficha_atual = ficha
        self.numero_prontuario = numero_prontuario

    def liberar(self):
        """Libera o consultorio encerrando a ocupacao corrente.

        Raises:
            ValueError: Se o consultorio ja estiver livre.
        """
        if not self.ocupado:
            raise ValueError(f"Consultorio {self.numero} ja esta livre.")
        self.ocupado = False
        self.ficha_atual = None
        self.numero_prontuario = None

    def __str__(self):
        """Retorna o estado formatado do consultorio.

        Returns:
            str: Descricao indicando se esta livre ou qual animal atende.
        """
        if not self.ocupado:
            return f"Consultorio {self.numero}: LIVRE"
        animal = self.ficha_atual.nome_animal
        return (
            f"Consultorio {self.numero}: OCUPADO "
            f"(Animal: {animal} | Prontuario #{self.numero_prontuario})"
        )
