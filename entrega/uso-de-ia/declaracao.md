# Declaração de uso de IA

## Ferramenta e modelo

- **Ferramenta:** Claude (aplicativo desktop da Anthropic), com acesso de leitura e escrita à pasta local do projeto.
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`).
- **Sessões:** uma sessão de conversa, registrada em `sessao.md`.

## O que a IA fez

- Leu o código, os testes, os dados e o README do desafio.
- Reproduziu as 5 falhas do `pytest -q` numa cópia isolada do projeto, confirmando os mesmos valores do log enviado.
- Identificou a causa raiz dos 4 defeitos cobertos pelos testes (câmbio, noites, status e ranking) e de um quinto defeito que nenhum teste detectava: o limite fixo de 200 linhas na leitura do CSV.
- Propôs a correção de cada defeito e a validou na cópia: testes, amostra `exemplo-validacao.csv` e relatório completo. Os arquivos originais não foram alterados nessa etapa.
- Explicou a arquitetura e o fluxo do CLI, do início ao relatório final.
- Respondeu à minha dúvida sobre o uso de `Decimal` na correção do câmbio, com uma demonstração do tipo retornado.
- Escreveu o teste adicional `tests/test_reading_limit.py` e mostrou que ele falha com o defeito e passa com a correção.
- Redigiu a descrição do Pull Request, o `entrega/README-ENTREGA.md`, este arquivo e o log `sessao.md`.

## O que eu fiz

- Preparei o repositório Git, publiquei o código original no GitHub e configurei o ambiente virtual e as dependências.
- Rodei a suíte no estado original e fiz uma análise prévia das falhas antes de pedir a revisão da IA.
- Criei a branch `fix/correcao-relatorio` e apliquei as correções manualmente, **uma por commit**, rodando `pytest -q` depois de cada uma para confirmar o efeito isolado (5 → 3 → 2 → 1 → 0 falhas, depois 6 testes passando com o teste novo).
- Revisei criticamente as propostas. Por exemplo, questionei se a troca para `amount * rate` mantinha o uso de `Decimal` exigido pelo README antes de aceitá-la.
- Abri o Pull Request, fiz o merge na `main` e repeti a validação final na minha máquina: `pytest -q` com 6 testes passando, amostra conferida campo a campo com o README e relatório completo gerado sem erro.
- Forneci os logs das minhas sessões de terminal para compor o histórico do `README-ENTREGA.md` e revisei os documentos da entrega.
