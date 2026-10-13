#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera uma base de movimentacoes de RH **SIMULADA** de uma companhia de danca
**ficticia**, no formato aceito pela skill `analise-turnover`.

Saida: dados/turnover-companhia-danca.csv
        colunas: id, area, admissao, desligamento, motivo

--------------------------------------------------------------------------
AVISO IMPORTANTE
--------------------------------------------------------------------------
Esta base NAO e dado real. Nao existe essa companhia, essas pessoas nao
existem e nenhum numero aqui descreve turnover de verdade. A base existe
para exercitar a skill e para servir de exemplo didatico. Ela **nao serve**
como benchmark, como parametro de mercado e como evidencia em trabalho
academico sobre o setor de danca.

Todo numero do CSV sai das PREMISSAS escritas no dicionario AREAS abaixo.
Com a semente fixa, a base e reproduzivel: rodar de novo gera o mesmo
arquivo, e qualquer duvida sobre um numero pode ser respondida relendo
este arquivo.

Rodar:
    python dados/gerador-companhia-danca.py
"""

import csv
import random
from datetime import date, timedelta

# --------------------------------------------------------------------------
# PREMISSAS DA SIMULACAO
# --------------------------------------------------------------------------
# Estes nao sao dados de mercado. Nao sao pesquisa. Sao hipoteses de trabalho
# inventadas para a simulacao e escolhidas para produzir uma base com
# personalidade (uma companhia com elenco, uma escola e uma producao).
#
# Pelo texto do CAGED (ver references/caged-e-limitacoes.md), a saida e
# segmentada em espontaneo / dispensado / aposentado / morto / transferido.
# Aqui aparecem espontaneo, pedido demissao, dispensado, aposentado e
# transferido. "Morto" foi deixado de fora de proposito.

SEMENTE = 20260913

INICIO = date(2015, 1, 1)   # antes disso nao ha registro: a companhia
                            # comeca a ter controle de folha aqui
FIM = date(2026, 10, 13)    # data de hoje no material do curso

AREAS = {
    # nome           quadro alvo por ano 2026   chance mensal base de saida
    #                      (companha + escola + producao)
    "Corpo de Baile":   {"alvo": {2015: 8, 2016: 9, 2017: 10, 2018: 11, 2019: 12,
                                   2020: 8, 2021: 11, 2022: 16, 2023: 19,
                                   2024: 21, 2025: 23, 2026: 24},
                        "saida_mes": 0.090},
    "Instrucao":        {"alvo": {2015: 5, 2016: 5, 2017: 6, 2018: 6, 2019: 6,
                                   2020: 6, 2021: 7, 2022: 8, 2023: 9,
                                   2024: 10, 2025: 10, 2026: 11},
                        "saida_mes": 0.030},
    "Producao":         {"alvo": {2015: 4, 2016: 4, 2017: 4, 2018: 5, 2019: 5,
                                   2020: 4, 2021: 5, 2022: 6, 2023: 7,
                                   2024: 8, 2025: 9, 2026: 9},
                        "saida_mes": 0.032},
    "Figurino":         {"alvo": {2015: 2, 2016: 2, 2017: 2, 2018: 2, 2019: 2,
                                   2020: 2, 2021: 3, 2022: 3, 2023: 4,
                                   2024: 4, 2025: 5, 2026: 5},
                        "saida_mes": 0.055},
    "Marketing":        {"alvo": {2015: 2, 2016: 2, 2017: 2, 2018: 2, 2019: 2,
                                   2020: 3, 2021: 3, 2022: 3, 2023: 4,
                                   2024: 4, 2025: 5, 2026: 5},
                        "saida_mes": 0.040},
    "Administrativo":   {"alvo": {2015: 3, 2016: 3, 2017: 3, 2018: 4, 2019: 4,
                                   2020: 4, 2021: 4, 2022: 5, 2023: 5,
                                   2024: 5, 2025: 5, 2026: 5},
                        "saida_mes": 0.008},
    "Manutencao":       {"alvo": {2015: 3, 2016: 3, 2017: 3, 2018: 4, 2019: 4,
                                   2020: 4, 2021: 5, 2022: 5, 2023: 6,
                                   2024: 6, 2025: 7, 2026: 7},
                        "saida_mes": 0.065},
    "Recepcao":         {"alvo": {2015: 2, 2016: 2, 2017: 2, 2018: 2, 2019: 2,
                                   2020: 2, 2021: 3, 2022: 3, 2023: 4,
                                   2024: 4, 2025: 4, 2026: 4},
                        "saida_mes": 0.030},
}

# Sazonalidade escolhida para a companhia: temporada de festival de junho a
# agosto e show de fim de ano em novembro/dezembro, matricula de escola em
# janeiro. Multiplica a chance de saida do mes.
SAZONALIDADE_SAIDA = {1: 0.8, 2: 0.7, 3: 1.0, 4: 1.0, 5: 0.9,
                      6: 1.2, 7: 1.5, 8: 1.7, 9: 1.4, 10: 1.0,
                      11: 0.7, 12: 0.6}

# Multiplicador do quadro alvo por mes (contratacao acompanha a agenda).
SAZONALIDADE_QUADRO = {1: 1.04, 2: 0.96, 3: 1.0, 4: 1.0, 5: 1.0,
                       6: 1.06, 7: 1.08, 8: 1.08, 9: 1.0, 10: 1.0,
                       11: 0.98, 12: 0.95}

# Risco por tempo de casa: saido cedo pesa mais (integracao), e apos 4 anos
# a saida fica mais rara (pessoa dificil de substituir, ja conhece o
# repertorio).
def multiplicador_tempo(meses_de_casa):
    if meses_de_casa < 6:
        return 1.6
    if meses_de_casa < 12:
        return 1.25
    if meses_de_casa < 48:
        return 1.0
    return 0.6


# Peso de cada motivo de desligamento, por area. Somando 1.
MOTIVOS = {
    "Corpo de Baile":   {"espontaneo": 0.72, "pedido de demissao": 0.08,
                         "dispensado": 0.18, "transferido": 0.02},
    "Instrucao":        {"espontaneo": 0.80, "pedido de demissao": 0.06,
                         "dispensado": 0.08, "aposentado": 0.06},
    "Producao":         {"espontaneo": 0.55, "pedido de demissao": 0.05,
                         "dispensado": 0.25, "transferido": 0.15},
    "Figurino":         {"espontaneo": 0.65, "pedido de demissao": 0.05,
                         "dispensado": 0.20, "transferido": 0.10},
    "Marketing":        {"espontaneo": 0.45, "pedido de demissao": 0.05,
                         "dispensado": 0.35, "transferido": 0.15},
    "Administrativo":   {"espontaneo": 0.45, "pedido de demissao": 0.05,
                         "dispensado": 0.20, "aposentado": 0.30},
    "Manutencao":       {"espontaneo": 0.80, "pedido de demissao": 0.05,
                         "dispensado": 0.10, "aposentado": 0.05},
    "Recepcao":         {"espontaneo": 0.85, "pedido de demissao": 0.05,
                         "dispensado": 0.10},
}

# Ajuste pontual de setembro/2026, so no Corpo de Baile. Escolhido para
# produzir um cenario didatico: lots de saida em uma area que tem admissao
# suficiente para a taxa CAGED ficar baixa. Nao e tese sobre o setor, e so
# o cenario plantado para o indicador agregado esconder o volume.
AJUSTE_PONTUAL = {("Corpo de Baile", 2026, 9): 2.4}


def meses_entre(d1, d2):
    m = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    if d2.day < d1.day:
        m -= 1
    return max(m, 0)


def dias_no_mes(ano, mes):
    if mes == 12:
        return 31
    return (date(ano, mes + 1, 1) - date(ano, mes, 1)).days


def sorteia_motivo(rng, area):
    pesos = MOTIVOS[area]
    lista = list(pesos.keys())
    valores = [pesos[k] for k in lista]
    return rng.choices(lista, weights=valores, k=1)[0]


def main():
    rng = random.Random(SEMENTE)
    pessoas = []
    contador = [0]

    def nova_pessoa(area, admissao):
        contador[0] += 1
        p = {"id": "CD%04d" % contador[0], "area": area,
             "admissao": admissao, "desligamento": None, "motivo": ""}
        pessoas.append(p)
        return p

    def ativos_da_area(area):
        return [p for p in pessoas
                if p["area"] == area and p["desligamento"] is None]

    # Quadro fundacional: gente admitida antes de 2015, que a saga da
    # simulacao nao alcanca. Entra antes do laco, entao o quadro alvo de cada
    # ano ja sai descontando essas pessoas -- o alvo e o quadro total, nao o
    # elenco mais o fundacional.
    for area, qtd, ano_ini in [("Corpo de Baile", 2, 2011), ("Producao", 2, 2010),
                               ("Administrativo", 2, 2009), ("Instrucao", 2, 2012),
                               ("Figurino", 1, 2013), ("Marketing", 1, 2014)]:
        for _ in range(qtd):
            adm = date(rng.randint(ano_ini, ano_ini + 2), rng.randint(1, 12),
                       rng.randint(1, 28))
            nova_pessoa(area, adm)

    ano, mes = INICIO.year, INICIO.month
    while date(ano, mes, 1) <= FIM:
        ultimo = min(dias_no_mes(ano, mes), (FIM - date(ano, mes, 1)).days + 1)

        for area, cfg in AREAS.items():
            # ---- saidas do mes
            for p in ativos_da_area(area):
                meses_casa = meses_entre(p["admissao"], date(ano, mes, 1))
                if meses_casa < 1:
                    continue  # ninguem sai no mes em que foi admitido
                prob = (cfg["saida_mes"]
                        * SAZONALIDADE_SAIDA[mes]
                        * multiplicador_tempo(meses_casa))
                prob *= AJUSTE_PONTUAL.get((area, ano, mes), 1.0)
                if rng.random() < prob:
                    dia = rng.randint(1, ultimo)
                    p["desligamento"] = date(ano, mes, dia)
                    p["motivo"] = sorteia_motivo(rng, area)

            # ---- contratacao para chegar na agenda do mes
            base = cfg["alvo"].get(ano)
            if base is None:
                continue
            alvo = int(round(base * SAZONALIDADE_QUADRO[mes]))
            faltam = alvo - len(ativos_da_area(area))
            for _ in range(max(0, faltam)):
                dia = rng.randint(1, ultimo)
                nova_pessoa(area, date(ano, mes, dia))

        mes += 1
        if mes == 13:
            ano, mes = ano + 1, 1

    pessoas.sort(key=lambda p: (p["admissao"], p["id"]))

    caminho = "dados/turnover-companhia-danca.csv"
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "area", "admissao", "desligamento", "motivo"])
        for p in pessoas:
            w.writerow([p["id"], p["area"], p["admissao"].isoformat(),
                        p["desligamento"].isoformat() if p["desligamento"] else "",
                        p["motivo"]])

    ativos = sum(1 for p in pessoas if p["desligamento"] is None)
    print("Base simulada escrita em: %s" % caminho)
    print("registros: %d | ativos hoje: %d | saidas no periodo: %d"
          % (len(pessoas), ativos, len(pessoas) - ativos))
    print("semente: %d (reproduce a base)" % SEMENTE)
    print("ATENCAO: base ficticia. Nao usar como benchmark nem como dado real.")


if __name__ == "__main__":
    main()