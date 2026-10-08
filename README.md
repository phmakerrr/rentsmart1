# RentSmart

Aplicação de linha de comando para montar orçamentos de locação da R.M. Imóveis. O programa calcula o aluguel, os adicionais e o desconto, mantém a taxa contratual separada e gera uma projeção de pagamentos por 12 meses em CSV.

## Requisitos

- Python 3.10 ou superior
- Nenhuma biblioteca externa

## Como executar

1. Abra um terminal na pasta do projeto.
2. Execute `python rentsmart.py` (no Windows, também pode usar `py rentsmart.py`).
3. Responda às perguntas. As opções são validadas pelo programa.
4. O resumo aparece no terminal e o arquivo `rentsmart_projecao.csv` é criado na pasta atual.

## Regras implementadas

- Apartamento: aluguel base de R$ 700,00; dois quartos adicionam R$ 200,00.
- Casa: aluguel base de R$ 900,00; dois quartos adicionam R$ 250,00.
- Estúdio: aluguel base de R$ 1.200,00; pacote opcional de duas vagas por R$ 250,00 e R$ 60,00 por vaga adicional.
- Casas e apartamentos podem incluir uma vaga por R$ 300,00 ao mês.
- Apartamentos sem crianças recebem desconto de 5% sobre o aluguel e os adicionais.
- A taxa contratual de R$ 2.000,00 pode ser paga em uma a cinco parcelas, separadas do aluguel.

O CSV tem 12 meses, separador ponto e vírgula e colunas separadas para aluguel, taxa contratual e total previsto.

## Organização do programa

- `Imovel` guarda as características da locação e calcula base, adicionais e desconto.
- `Orcamento` reúne os cálculos, apresenta o resumo e gera o CSV.
- `main()` conduz as perguntas e conecta as partes.

O fluxograma da lógica está no arquivo `fluxograma.md`.
