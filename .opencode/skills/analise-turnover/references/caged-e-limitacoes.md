# CAGED, fórmulas e o que elas não fazem

Consultado em **13/10/2026**. O que foi lido por inteiro está marcado. O que não
foi está marcado como não lido, para não ser citado como se tivesse sido.

---

## 1. A fórmula oficial brasileira

> **Taxa de rotatividade** — Mede o percentual dos trabalhadores substituídos
> mensalmente em relação ao estoque vigente no primeiro dia do mês, em nível
> geográfico e setorial, mas **não em nível ocupacional**. Assim, esse indicador,
> em virtude da forma agregada como é calculado, **não permite quantificar a
> substituição dos trabalhadores com o mesmo perfil ocupacional**.
>
> **TR (t) = [menor ( A(t) , D(t) ) ÷ E(t)] × 100**
>
> TR = taxa de rotatividade do mês t
> A(t) = total de admissões no mês t
> D(t) = total de desligamentos no mês t
> E(t) = total de empregos no 1º dia do mês

Origem: Ministério do Trabalho e Emprego, "O que é CAGED", `gov.br`.
Página lida **por inteiro** em 13/10/2026.

### Duas consequências que o texto deixa explícitas

1. **O numerador é o menor**, não a soma. Empresa que admite 100 e demite 50 tem
   taxa sobre 50, não sobre 150.
2. **É agregado.** Não diz que saiu um vendedor para entrar um vendedor. Por isso
   o relatório precisa mostrar D separado da taxa.

---

## 2. Os outros três indicadores do mesmo caderno

```
Saldo (A - D)              = diferenca entre admissoes e desligamentos
Variacao relativa          = variacao absoluta / estoque do 1o dia do mes x 100
Indice de emprego (t, t-1) = [# empregos no ultimo dia do mes t
                              / # empregos no 1o dia do mes t] x 100
```

Mesma pagina do MTE, lida por inteiro em 13/10/2026.

---

## 3. A fórmula de mercado internacional

```
Turnover = saidas / quadro medio x 100
quadro medio = (quadro no inicio + quadro no fim) / 2
```

Origem: SHRM. **NÃO lida por inteiro** — a guia completa
(*How to Determine Your Turnover Rate*) está atrás de login. A definição
"separations during the measurement period divided by the average number of
employees" veio do resumo da página da SHRM, consultado em 13/10/2026. O detalhe
do quadro médio como média das pontas **não foi conferido na fonte**.

---

## 4. Estrutura do CAGED (o que dá para segmentar)

| Item | Detalhe |
|---|---|
| Criado por | Lei nº 4.923, de 23/12/1965 |
| População | Trabalhadores regidos pela CLT |
| Periodicidade | Mensal |
| Prazo de declaração | Até o dia 7 do mês subsequente |
| Estabelecimentos informantes | Cerca de 900 mil por mês |
| Cobertura | Em torno de 85% do universo de empregados celetistas |
| Natureza | Registro administrativo |

**Tipos de movimentação**

- Admissões: 1º emprego, reemprego, reintegração, contrato por prazo
  determinado, transferência.
- Desligamentos: dispensado, espontâneo, aposentado, morto, transferido.

**Variáveis dos empregados**: nome, PIS, gênero, idade, raça/cor, grau de
instrução, ocupação (CBO 2002), horas contratuais semanais e remuneração mensal.

**Desagregação**: geográfica, setorial (CNAE) e ocupacional.

⚠️ **Servidor público não entra.** O CAGED cobre CLT. Se a análise for de órgão
público, o CAGED não serve de referência nem de base.

---

## 5. O que as fontes consultadas NÃO dizem

| Assunto | Situação |
|---|---|
| Qual o turnover saudável de um setor | **NÃO SEI.** Nenhuma fonte lida define valor de referência por setor. |
| Quanto custa o turnover | **NÃO SEI.** Nenhuma fonte oficial lida traz o custo. |
| Série histórica do turnover brasileiro | Existe no CAGED, **não foi consultada** aqui. |
| Subnotificação do CAGED | Existe discussão acadêmica (FGV, blog do IBRE); **não foi lida** aqui. |

Blog de RH cita "turnover médio de 30% a 45% ao ano". Sem metodologia publicada
e sem autoria identificável: **não usar**.

---

## 6. Limitações técnicas que a skill herda

- **CAGED é registro administrativo.** A empresa declara; erro de declaração
  entra no número.
- **O indicador agregado não identifica o posto.** Troca de vendedor por
  vendedor é invisível na taxa.
- **Taxa mensal não é taxa anual.** Multiplicar por 12 distorce. Se projetar o
  ano, mostrar a fórmula da projeção ao lado do número.
- **Comparação honesta é com o mesmo mês do ano anterior.** Comparar setembro
  com outubro mistura sazonalidade com problema.