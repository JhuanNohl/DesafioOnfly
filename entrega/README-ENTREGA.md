# README da entrega — Consolidador de reservas de hotel

## Defeitos corrigidos

| # | Arquivo | Defeito | Causa raiz |
|---|---------|---------|------------|
| 1 | `src/onfly_report/services/currency_converter.py` | Valores em moeda estrangeira convertidos errado para BRL. | A conversão dividia o valor pela taxa em vez de multiplicar e passava por `float`, perdendo a precisão exigida para dinheiro. |
| 2 | `src/onfly_report/services/stay_calculator.py` | Noites negativas ou erradas em estadias que viram o mês ou o ano. | O cálculo subtraía o dia do mês (`checkout.day - checkin.day`) em vez da diferença entre as datas. |
| 3 | `src/onfly_report/services/status_policy.py` | Reservas `NO_SHOW` entravam em noites, valores, `by_month` e `top_hotels`. | A regra de faturamento excluía só `CANCELLED`, em vez de aceitar só `CONFIRMED`. |
| 4 | `src/onfly_report/services/report_builder.py` | `top_hotels` mostrava os hotéis de menor valor primeiro. | A ordenação era crescente por valor, e não decrescente com empate por `hotel_id` crescente. |
| 5 | `src/onfly_report/repositories/csv_reservation_repository.py` | Relatório incompleto em arquivos com mais de 200 reservas. | Um `break` dentro do loop de leitura parava silenciosamente na 200ª linha, e o arquivo real tem 300. |

### Correções aplicadas

```python
# 1. currency_converter.py — aritmética exata em Decimal
return amount * rate

# 2. stay_calculator.py — diferença real entre as datas, não inclusiva
return (checkout - checkin).days * rooms

# 3. status_policy.py — só CONFIRMED é faturável
return status == "CONFIRMED"

# 4. report_builder.py — valor decrescente, empate por hotel_id crescente
ranked_hotels = sorted(hotels.items(), key=lambda item: (-item[1]["amount"], item[0]))

# 5. csv_reservation_repository.py — removido o limite fixo de 200 linhas
#    (if len(rows) == 200: break)
```

`amount` e `rate` já chegam como `Decimal` (convertidos em `row_parser.py` e em `csv_rate_repository.py`), então o resultado da multiplicação também é `Decimal`. Nenhum valor é arredondado durante o cálculo: o arredondamento half-up para 2 casas acontece só na serialização (`format_money`), como manda o README.

## Como investiguei

1. Rodei `pytest -q` no estado original: os 5 testes falhavam. Anotei o valor obtido e o esperado de cada falha.
2. Segui o fluxo do CLI (`cli.py` → `ReportBuilder` → repositórios → serviços) e cruzei cada falha com a regra de negócio correspondente do README:
   * `118.45` em vez de `642.00` → câmbio (100 USD ÷ 5,42 + 100 BRL).
   * `-28` em vez de `3` → noites (2 − 30, usando o dia do mês).
   * `120.00` em vez de `100.00` → status (o `NO_SHOW` estava sendo somado).
   * `H04, H03, H02` → ordenação invertida.
   * O teste de regressão falhava pela combinação dos defeitos 1 e 3.
3. Como o README avisa que os testes cobrem só parte dos cenários, revisei também o código que nenhum teste exercitava. Na leitura do CSV encontrei o limite fixo de 200 linhas, enquanto `data/reservas_hoteis.csv` tem 300 reservas.
4. Fiz cada correção com mudança mínima, isolada no módulo responsável, sem alterar a estrutura, o contrato do CLI ou o schema do relatório.
5. Adicionei um teste para o defeito 5, que a suíte fornecida não detectava.

## Teste adicionado

`tests/test_reading_limit.py` gera um CSV com 300 reservas confirmadas (BRL 100,00, 1 noite cada) e verifica `total_reservations`, `confirmed_reservations`, `total_room_nights` e `total_amount_brl`. Com o limite antigo, ele falha com `assert 200 == 300`. Com a correção, ele passa.

Os testes fornecidos não foram alterados.

## Como validar

```bash
pip install -r requirements-dev.txt

# testes
pytest -q

# amostra de validação (comparar com a tabela do README)
PYTHONPATH=src python -m onfly_report \
  --input data/exemplo-validacao.csv \
  --rates data/taxas_cambio.csv \
  --output output/exemplo.json

# relatório completo
PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
```

### Amostra de validação (`data/exemplo-validacao.csv`)

Todos os valores conferem com a tabela do README:

| Campo | Esperado | Obtido |
|-------|----------|--------|
| `total_reservations` | 12 | 12 |
| `confirmed_reservations` | 9 | 9 |
| `cancelled_reservations` | 2 | 2 |
| `no_show_reservations` | 1 | 1 |
| `total_room_nights` | 28 | 28 |
| `total_amount_brl` | 7566.00 | 7566.00 |
| `average_nightly_rate_brl` | 270.21 | 270.21 |

`by_month` (2025-01: 8 / 25 / 6684.00; 2025-02: 1 / 3 / 882.00) e `top_hotels` (H01, H02, H12, H10, H09) também conferem.

### Relatório completo (`data/reservas_hoteis.csv`)

```
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

Código de saída `0`, com o relatório gravado em `output/report.json`.

## Resultado do `pytest`

```
$ pytest -q
......                                                                   [100%]
6 passed
```

5 testes fornecidos + 1 teste adicional.

## Uso de IA

Usei assistente de IA durante a investigação. A sessão exportada e a declaração estão em `entrega/uso-de-ia/`.
