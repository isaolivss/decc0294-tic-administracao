---
name: Criativo de Anúncio
description: Escreve variações de texto de anúncio para Meta Ads, Instagram e LinkedIn a partir de um briefing, checando oferta, formato e contagem de caracteres. Use quando pedirem anúncio, criativo, copy de campanha, texto de Facebook ou Instagram Ads, ou legenda promocional.
---

# Criativo de Anúncio

Transforma um briefing de campanha em variações de texto publicitário prontas para
as plataformas, sem inventar oferta e sem quebrar os limites de cada canal.

## Quando usar

- "Faz um anúncio para...", "cria um criativo de...", "escreve o texto da campanha".
- Variações de texto para Meta Ads (texto principal, título, descrição).
- Legenda promocional de Instagram ou texto de LinkedIn.

## Quando não usar

- Post orgânico de marca sem objetivo de conversão → escrever o texto direto.
- Copy juridicamente sensível (claim de saúde, financeiro, comparativo com concorrente
  nomeado) → entregar o rascunho e sinalizar que precisa de revisão jurídica.
- Pedido sem briefing → **não inventar**. Pedir os dados do bloco seguinte.

## Entrada obrigatória

Antes de escrever, confirmar com quem pediu:

1. Produto ou serviço exato.
2. Público-alvo.
3. Canal e formato do anúncio.
4. **A oferta real**: desconto, frete, prazo, brinde, valor, condição de pagamento.
5. Tom da marca (uma frase).
6. Chamada para ação desejada.
7. O que **não** pode aparecer (concorrente, palavra vetada, promessa vedada).

Faltando o item 4, o criativo **não sai**. Anúncio com oferta inventada é
publicidade enganosa (CDC, art. 37). Escrever `NÃO SEI` e devolver o que falta.

## Procedimento

1. Listar em uma linha cada fato disponível do briefing e a origem de cada um.
2. Marcar com `[CONFERIR]` tudo que é afirmação sem comprovação no briefing.
3. Escrever **3 variações** por campo, com ângulo diferente entre elas:
   - V1 — benefício direto, benefit-led.
   - V2 — problema em primeiro plano, pain-led.
   - V3 — prova ou credibilidade, proof-led.
4. Contar os caracteres de cada campo e mostrar a contagem.
5. Conferir se nenhuma regra da seção seguinte foi quebrada.
6. Salvar em `saidas/` com o nome da campanha e a data.

## Regras

Cada regra existe porque pode ser violada. Se nenhuma delas pode ser quebrada,
apague a regra e escreva outra.

1. **A oferta é dado, não criação.** Preço, desconto, prazo, estoque, frete e
   condição só entram se estiverem no briefing. Vazio significa `[CONFERIR]`,
   nunca um número plausível.
2. **Nenhum número sem origem.** Cada número do texto aponta a linha do briefing
   de onde saiu. "Até 50% OFF" sem linha de origem não é escrito.
3. **Sem superlativo sem fonte.** "O melhor", "nº 1", "o mais barato" exigem
   fonte verificável no briefing. Sem fonte, trocar por descrição concreta.
4. **Nada de dado pessoal.** CPF, RG, endereço residencial, telefone e nome de
   cliente não entram, nem em exemplo. Vale para a LGPD e para a lei de
   publicidade de cada canal.
5. **Contagem à mostra.** Todo campo sai com `n caracteres`. Se estourar o
   recomendado, entregar versão curta e a longa, e avisar qual usar.
6. **Dúvida marcada, não omitida.** Ponto não confirmado vira `[CONFERIR]` no
   corpo do texto. Silêncio parece concordância.

## Formato de saída

```markdown
# Criativos — {campanha}
Data: {data} | Canal: {canal} | Briefing usado: {caminho do arquivo}

## Fatos disponíveis e origem
- {fato} — origem: {linha/seção do briefing}

## Texto principal
| Versão | Ângulo | Texto | Caracteres |
|---|---|---|---|
| V1 | benefício | ... | {n} |

## Título
| Versão | Texto | Caracteres |
|---|---|---|
| V1 | ... | {n} |

## Antes de publicar
- [ ] Oferta conferida com quem responde pela campanha: {nome}
- [ ] {outros itens do checklist}
```

## Teste de violação

Responda antes de entregar. Se não souber responder, a regra está vaga.

| Regra | Como pode ser violada |
|---|---|
| Oferta é dado | Escrever "50% OFF" porque é promoção de outra campanha |
| Número com origem | Usar "3 em 1" sem a linha do briefing que diz isso |
| Superlativo com fonte | Escrever "o melhor preço da cidade" sem pesquisa |
| Sem dado pessoal | Colocar "Ana, cliente desde 2019" no exemplo do anúncio |
| Contagem à mostra | Entregar o texto sem a contagem de caracteres |
| Dúvida marcada | Apagar o `[CONFERIR]` para o texto "ficar mais bonito" |

## Limitações

- A skill organiza o texto. Ela não substitui a aprovação de quem responde pela
  campanha, e não confere se a oferta anunciada é a oferta real.
- Os limites de caracteres da referência são **recomendações** da Meta para a
  maioria dos posicionamentos, não corte técnico. Conferir a página oficial
  quando o posicionamento for específico.
- Anúncio de produto com efeito colateral (saúde, financeiário, alimentação
  infantil) sai como rascunho marcado para revisão jurídica.