---
name: Análise de Turnover
description: Calcula e interpreta a taxa de rotatividade de pessoal a partir de um CSV de movimentações, separando voluntário de involuntário e segmentando por área e tempo de empresa. Use quando pedirem análise de turnover, rotatividade, taxa de desligamentos, cálculo de saídas ou diagnóstico de por que gente está saindo.
---

# Análise de Turnover

Calcula a rotatividade com o script e transforma o resultado em leitura para
quem decide. O cálculo não é feito aqui: é feito pelo `scripts/turnover.py`.

## Quando usar

- "Calcula o turnover", "analisa a rotatividade", "por que a gente está perdendo gente".
- "Taxa de desligamentos", "turnover voluntário ou involuntário".
- Diagnóstico por área, cargo ou tempo de empresa.

## Quando não usar

- **Servidor público.** O CAGED cobre CLT. Método e denominador não são
 transferíveis sem ajuste — não reaproveitar o número.
- Ausência de dados de desligamento por pessoa. Sem a movimentação individual não
  há taxa; entregar o pedido de dados, não a análise.
- Comparação entre organizações sem saber a cobertura de cada base.

## Entrada obrigatória

Arquivo CSV com as colunas:

```
id, area, admissao, desligamento, motivo
```

- `id` — identificador. **Pode ser um código**: a análise não precisa do nome.
- `admissao` e `desligamento` — `AAAA-MM-DD`. Desligamento vazio = ativo.
- `motivo` — `espontao`, `pedido demissao`, `dispensado`, `aposentado`,
  `morte` ou `transferido`. Vazio quando a pessoa está ativa.

Antes de rodar: rodar `python turnover.py <csv> --confere`. Se recusar, o script
lista o que falta. Não contornar.

## Procedimento

1. **Declarar a fórmula no topo do relatório.** Padrão: CAGED
   (`min(A,D)/E×100`). Alternativa SHRM (`D/quadro medio×100`). Uma só, com o
   motivo da escolha em uma frase.
2. Rodar `python turnover.py <csv> --mes AAAA-MM` e usar a saída como está.
   **Não recalcular nada no texto.**
3. Conferir se A e D são diferentes. Se forem, o script já avisa que a taxa usa
   `min(A,D)` e que o número maior fica escondido.
4. Ler a tabela por área: procurar onde **D é alto e a TR é baixa**. Esse é o
   ponto cego do indicador.
5. Olhar o tempo de empresa de quem saiu. Saída concentrada nos primeiros meses
   aponta integração; saída concentrada depois de anos aponta outro problema.
6. Escrever a leitura por cima dos números. Nenhum passo anterior produz causa:
   causa exige entrevista de desligamento, e isso é humano.
7. Comparar com o **mesmo mês do ano anterior**, nunca com o mês anterior sem
   dizer o porquê.

## Leitura por tipo de saída

| O que a tabela mostra | O que aponta | O que **não** dá para concluir |
|---|---|---|
| Espontâneo alto | Salário, carga, chefia, falta de crescimento | Qual dos quatro |
| Dispensado alto | Problema de gestão ou de meta | Quem errou |
| Saída nos primeiros meses | Integração e onboarding | Que o processo de admissão é o culpado |
| Saída após muitos anos | Carreira, Pensionamento, reestruturação | Que a empresa não retém ninguém |
| TR baixa com D alto | Indicador agregado mascarando volume | Que está tudo bem |

## Regras

Cada regra pode ser violada. Se nenhuma puder, apague e escreva outra.

1. **Uma fórmula só, declarada.** Não misturar CAGED com SHRM no mesmo
   relatório. Dois denominadores, dois números incomparáveis.
2. **Denominador explícito ao lado do número.** "Estoque no 1º dia" ou "quadro
   médio". Sem isso o número não é comparável com nada.
3. **Taxa mensal não é anualizada em silêncio.** Se projetar o ano, mostrar a
   fórmula da projeção junto.
4. **Benchmark só com fonte, ano e setor.** Sem os três, escrever `NÃO SEI`.
   Blog de RH sem metodologia não é fonte.
5. **Voluntário e involuntário sempre juntos.** Taxa total sozinha não diagnostica:
   demissão em massa e pedido de demissão por salário baixo dão o mesmo número
   e causas opostas.
6. **A taxa nunca é citada sem o D ao lado.** Se a área teve 3 desligamentos e a
   taxa deu 14%, escrever os dois. O número sozinho mente.
7. **Saída agregada, sempre.** Nenhum relatório mostra nome, `id` ou caso
   individual. Vira "N casos na área X". Se o pedido for nominativo, recusar e
   dizer que o dado não circula.
8. **Askill não emite juízo de valor.** Ela calcula e organiza. "Alto" ou "baixo"
   é judgement de quem responde pela área, com o mercado da região na cabeça.
9. **Causa é hipótese até a entrevista.** Escrever "hipótese a testar", nunca
   "a causa é".

## Formato de saída

```markdown
# Rotatividade — {mês} — {escopo}

Base: {caminho do csv} · {n} registros · cobertura da base: {descrever}
Fórmula: {nome} — {fórmula} · denominador: {denominador}
Comparação: {mês/ano anterior} · base da comparação: {mesma base}

## Números
| indicador | valor |
|---|---|
| A - admissões | |
| D - desligamentos | |
| TR | |
| Saldo | |

## Saídas por tipo
voluntário / involuntário / neutro — com o total e a proporção

## Por área
| área | A | D | TR |
(além da TR, sempre as duas colunas brutas)

## Leitura
- o que os números mostram
- o que os números não mostram
- hipóteses a testar, com o método de teste de cada uma

## O que não sei
- NAO SEI: {o que ficou fora}
```

## Teste de violação

Responda antes de entregar. Se não souber responder, a regra está vaga.

| Regra | Como pode ser violada |
|---|---|
| Uma fórmula só | Colocar "CAGED" no texto e usar quadro médio no cálculo |
| Denominador explícito | Citar a taxa sem dizer se é estoque do 1º dia ou quadro médio |
| Sem anualizar calada | Pegar 18,75% de setembro e escrever "225% ao ano" |
| Benchmark com fonte | Escrever "turnover alto para o setor" sem fonte, ano e setor |
| Voluntário e involuntário juntos | Mandar só o número total de 18,75% |
| D ao lado da taxa | Mostrar "Administrativo 14,29%" e omitir que foram 3 saídas |
| Saída agregada | Colocar no relatório "P046, dispensado, 5 meses de empresa" |
| Skill não emite juízo de valor | Escrever "turnover aceitável para uma empresa de 32 pessoas" |
| Causa é hipótese | Escrever "a causa é o salário" sem entrevista de desligamento |

## Limitações

- O script só valida e calcula. Ele não decide, não compara com mercado e não
  produz conclusão.
- Base ruim entra, número ruim sai. O script recusa coluna e data quebrada; ele
  não recusa base incompleta por fora do arquivo.
- Série curta não sustenta tendência. Três meses não é série.
- O indicador é agregado por construção: não mede substituição de posto.
- **Nenhum benchmark de mercado entra aqui.** É tentador e é onde o relatório
  costuma perder credibilidade.