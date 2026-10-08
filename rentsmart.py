"""RentSmart - orçamento de locação da R.M. Imóveis.

Aplicação de linha de comando para calcular aluguel, taxa contratual e
projeção dos pagamentos do primeiro ano em CSV.
"""

from dataclasses import dataclass
import csv
from decimal import Decimal
from pathlib import Path

DINHEIRO = Decimal
TAXA_CONTRATUAL = DINHEIRO("2000.00")


def moeda(valor: Decimal) -> str:
    """Formata um valor em reais no padrão brasileiro."""
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def perguntar_opcao(pergunta: str, opcoes: set[str]) -> str:
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in opcoes:
            return resposta
        print(f"Opção inválida. Escolha: {', '.join(sorted(opcoes))}.")


def perguntar_inteiro(pergunta: str, minimo: int, maximo: int) -> int:
    while True:
        try:
            valor = int(input(pergunta).strip())
            if minimo <= valor <= maximo:
                return valor
        except ValueError:
            pass
        print(f"Informe um número inteiro entre {minimo} e {maximo}.")


@dataclass
class Imovel:
    tipo: str
    quartos: int = 0
    garagem: bool = False
    pacote_estudio: bool = False
    vagas_estudio: int = 0
    possui_criancas: bool = True

    def __post_init__(self) -> None:
        if self.tipo not in {"apartamento", "casa", "estudio"}:
            raise ValueError("Tipo de imóvel inválido.")
        if self.tipo in {"apartamento", "casa"} and self.quartos not in {1, 2}:
            raise ValueError("Casas e apartamentos devem ter um ou dois quartos.")
        if self.tipo == "estudio" and self.vagas_estudio < 0:
            raise ValueError("A quantidade de vagas adicionais não pode ser negativa.")
        if self.tipo != "estudio" and self.vagas_estudio:
            raise ValueError("Vagas adicionais de estúdio não se aplicam a este imóvel.")
        if self.tipo == "estudio" and self.garagem:
            raise ValueError("Estúdio usa a opção de pacote de vagas.")

    def aluguel_base(self) -> Decimal:
        return {
            "apartamento": DINHEIRO("700.00"),
            "casa": DINHEIRO("900.00"),
            "estudio": DINHEIRO("1200.00"),
        }[self.tipo]

    def adicional_quartos(self) -> Decimal:
        if self.quartos == 2 and self.tipo == "apartamento":
            return DINHEIRO("200.00")
        if self.quartos == 2 and self.tipo == "casa":
            return DINHEIRO("250.00")
        return DINHEIRO("0.00")

    def adicional_vagas(self) -> Decimal:
        if self.tipo == "estudio":
            if self.pacote_estudio:
                return DINHEIRO("250.00") + DINHEIRO("60.00") * self.vagas_estudio
            return DINHEIRO("0.00")
        return DINHEIRO("300.00") if self.garagem else DINHEIRO("0.00")

    def desconto(self, subtotal: Decimal) -> Decimal:
        if self.tipo == "apartamento" and not self.possui_criancas:
            return (subtotal * DINHEIRO("0.05")).quantize(DINHEIRO("0.01"))
        return DINHEIRO("0.00")


@dataclass
class Orcamento:
    imovel: Imovel
    parcelas_contrato: int

    def __post_init__(self) -> None:
        if not 1 <= self.parcelas_contrato <= 5:
            raise ValueError("A taxa contratual deve ser paga em uma a cinco parcelas.")

    @property
    def aluguel_base(self) -> Decimal:
        return self.imovel.aluguel_base()

    @property
    def adicional_quartos(self) -> Decimal:
        return self.imovel.adicional_quartos()

    @property
    def adicional_vagas(self) -> Decimal:
        return self.imovel.adicional_vagas()

    @property
    def desconto(self) -> Decimal:
        return self.imovel.desconto(self.aluguel_base + self.adicional_quartos + self.adicional_vagas)

    @property
    def aluguel_mensal(self) -> Decimal:
        return self.aluguel_base + self.adicional_quartos + self.adicional_vagas - self.desconto

    @property
    def parcela_contrato(self) -> Decimal:
        return (TAXA_CONTRATUAL / self.parcelas_contrato).quantize(DINHEIRO("0.01"))

    def gerar_csv(self, caminho: Path) -> None:
        with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mês", "Aluguel mensal (R$)", "Taxa contratual (R$)", "Total previsto (R$)"])
            for mes in range(1, 13):
                contrato = self.parcela_contrato if mes <= self.parcelas_contrato else DINHEIRO("0.00")
                total = self.aluguel_mensal + contrato
                escritor.writerow([mes, f"{self.aluguel_mensal:.2f}", f"{contrato:.2f}", f"{total:.2f}"])

    def exibir_resumo(self) -> None:
        print("\n===== ORÇAMENTO RENTSMART =====")
        print(f"Imóvel: {self.imovel.tipo.capitalize()}")
        if self.imovel.tipo in {"apartamento", "casa"}:
            print(f"Quartos: {self.imovel.quartos}")
        elif self.imovel.pacote_estudio:
            print(f"Pacote de estacionamento: 2 vagas + {self.imovel.vagas_estudio} adicional(is)")
        print(f"Aluguel base:                {moeda(self.aluguel_base)}")
        print(f"Adicional de quartos:        {moeda(self.adicional_quartos)}")
        print(f"Adicional de estacionamento:{' ' if self.adicional_vagas >= 0 else ''} {moeda(self.adicional_vagas)}")
        print(f"Desconto:                    -{moeda(self.desconto)}")
        print(f"Aluguel mensal:              {moeda(self.aluguel_mensal)}")
        print(f"Taxa contratual:             {moeda(TAXA_CONTRATUAL)}")
        print(f"Parcelamento:                {self.parcelas_contrato}x de {moeda(self.parcela_contrato)}")
        print("A taxa contratual é separada do aluguel mensal.")


def coletar_imovel() -> Imovel:
    tipo = perguntar_opcao("Tipo (apartamento/casa/estudio): ", {"apartamento", "casa", "estudio"})
    if tipo in {"apartamento", "casa"}:
        quartos = perguntar_inteiro("Quantidade de quartos (1 ou 2): ", 1, 2)
        garagem = perguntar_opcao("Adicionar uma vaga de garagem? (s/n): ", {"s", "n"}) == "s"
        criancas = True
        if tipo == "apartamento":
            criancas = perguntar_opcao("O cliente possui crianças? (s/n): ", {"s", "n"}) == "s"
        return Imovel(tipo=tipo, quartos=quartos, garagem=garagem, possui_criancas=criancas)

    pacote = perguntar_opcao("Adicionar pacote inicial de duas vagas por R$ 250,00? (s/n): ", {"s", "n"})
    adicionais = 0
    if pacote == "s":
        adicionais = perguntar_inteiro("Vagas adicionais (0 a 20): ", 0, 20)
        return Imovel(tipo=tipo, pacote_estudio=True, vagas_estudio=adicionais)
    return Imovel(tipo=tipo, pacote_estudio=False)


def main() -> None:
    imovel = coletar_imovel()
    parcelas = perguntar_inteiro("Número de parcelas da taxa contratual (1 a 5): ", 1, 5)
    orcamento = Orcamento(imovel=imovel, parcelas_contrato=parcelas)
    orcamento.exibir_resumo()
    caminho = Path("rentsmart_projecao.csv")
    orcamento.gerar_csv(caminho)
    print(f"\nProjeção de 12 meses salva em: {caminho.resolve()}")


if __name__ == "__main__":
    main()
