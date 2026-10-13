"""
monta_painel.py
Le a base consolidada (saida/pam-ma-2025.json) e monta o payload enxuto que o
painel HTML consome: numeros-chave, series, rankings, mapa e os avisos de
qualidade de dados.

Como rodar:
  python dados/pam-ma-2025/monta_painel.py

Saida:
  dados/pam-ma-2025/saida/painel.json
"""

import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
ANO = 2025
ANO_ANT = 2024

# produtos que entram na tabela detalhada do painel (top por valor no estado)
TOP_N = 14

ROT_VARIAVEL = {
    "214": "producao_t",
    "112": "rendimento_kg_ha",
    "8331": "area_plantada_ha",
    "216": "area_colhida_ha",
    "215": "valor_mil_reais",
}


def arred(v, casas=0):
    if v is None:
        return None
    return round(v, casas) if casas else round(v)


def pct(a, b):
    if a is None or not b:
        return None
    return round(100.0 * (a - b) / b, 1)


def principal():
    base = json.load(open(os.path.join(SAIDA, "pam-ma-%d.json" % ANO), encoding="utf-8"))

    rec = base["serie_estado"]["recalculado"]
    prods = base["produtos"]
    brasil = base["brasil"]
    muns = base["municipios"]
    ano = str(ANO)
    ant = str(ANO_ANT)
    agora = rec[ano]
    antes = rec[ant]

    # ---------------- serie historica
    anos = sorted(rec, key=int)
    serie = [
        {
            "ano": int(a),
            "producao": arred(rec[a]["producao_t"]),
            "area": arred(rec[a]["area_colhida_ha"]),
            "valor": arred(rec[a]["valor_mil_reais"]),
            "rendimento": arred(rec[a]["rendimento_kg_ha"], 1),
        }
        for a in anos
    ]

    # ---------------- produtos
    linhas = []
    for nome, dados in prods.items():
        a = dados.get(ano, {})
        v = a.get("215", {}).get("v")
        if not v:
            continue
        q = a.get("214", {}).get("v")
        area = a.get("216", {}).get("v")
        ap = a.get("8331", {}).get("v")
        ant_d = dados.get(ant, {})
        linhas.append(
            {
                "produto": nome,
                "codigo": dados.get("codigo"),
                "valor": arred(v),
                "producao": arred(q),
                "area": arred(area),
                "area_plantada": arred(ap),
                "rendimento": arred(1000 * q / area, 0) if q and area else None,
                "valor_por_t": arred(v * 1000 / q) if q else None,
                "valor_por_ha": arred(v * 1000 / area) if area else None,
                "part_valor": arred(100.0 * v / agora["valor_mil_reais"], 1),
                "part_producao": arred(100.0 * q / agora["producao_t"], 1) if q else None,
                "part_area": arred(100.0 * area / agora["area_colhida_ha"], 1) if area else None,
                "br_producao": arred(brasil.get(nome, {}).get("214")),
                "part_nacional": (
                    arred(100.0 * q / brasil[nome]["214"], 2)
                    if q and brasil.get(nome, {}).get("214")
                    else None
                ),
                "valor_ant": arred(ant_d.get("215", {}).get("v")),
                "producao_ant": arred(ant_d.get("214", {}).get("v")),
            }
        )
    linhas.sort(key=lambda x: -x["valor"])
    total_top = sum(x["valor"] for x in linhas)
    for x in linhas:
        x["delta_valor"] = pct(x["valor"], x["valor_ant"]) if x["valor_ant"] else None
        x["delta_producao"] = pct(x["producao"], x["producao_ant"]) if x["producao_ant"] else None

    # ---------------- municipios
    def linha_mun(m, chave="valor_mil_reais"):
        d = m[ano]
        return {
            "codigo": m["codigo"],
            "nome": m["nome"],
            "valor": arred(d[chave]),
            "producao": arred(d["producao_t"]),
            "area": arred(d["area_colhida_ha"]),
            "rendimento": arred(d["rendimento_kg_ha"], 0),
            "n_produtos": d["n_produtos"],
            "valor_ant": arred(m[ant][chave]),
        }

    ranking = {
        "valor": sorted((linha_mun(m) for m in muns), key=lambda x: -x["valor"]),
        "producao": sorted((linha_mun(m, "producao_t") for m in muns), key=lambda x: -(x["valor"] or 0)),
        "area": sorted((linha_mun(m, "area_colhida_ha") for m in muns), key=lambda x: -(x["valor"] or 0)),
    }
    for chave in ranking:
        for i, x in enumerate(ranking[chave], 1):
            x["pos"] = i
            x["share"] = arred(100.0 * x["valor"] / agora["valor_mil_reais"], 2)

    # ---- curva de pareto: participação ACUMULADA (o share individual não serve)
    total_valor = agora["valor_mil_reais"]
    acumulado = 0.0
    acumulado_lista = []
    for x in ranking["valor"]:
        acumulado += x["valor"]
        acumulado_lista.append(arred(100.0 * acumulado / total_valor, 2))
    for i, x in enumerate(ranking["valor"]):
        x["share_acum"] = acumulado_lista[i]

    def share_em(n):
        return acumulado_lista[n - 1] if n <= len(acumulado_lista) else 100.0

    ordered = sorted((m[ano]["valor_mil_reais"] or 0) for m in muns)
    mediana = ordered[len(ordered) // 2]

    pareto = {
        "share_1": share_em(1),
        "share_5": share_em(5),
        "share_10": share_em(10),
        "share_20": share_em(20),
        "share_30": share_em(30),
        "share_50": share_em(50),
        "share_100": share_em(100),
        "mediana_valor": arred(mediana),
        "razao_top1_mediana": arred(ranking["valor"][0]["valor"] / mediana, 0) if mediana else None,
        "acumulado": acumulado_lista[:40],
        "picos": {
            "valor": max(rec, key=lambda a: rec[a]["valor_mil_reais"]),
            "producao": max(rec, key=lambda a: rec[a]["producao_t"]),
        },
        "minimo": {
            "valor": min(rec, key=lambda a: rec[a]["valor_mil_reais"]),
            "producao": min(rec, key=lambda a: rec[a]["producao_t"]),
        },
    }

    # detalhe por produto nos municipios (so os produtos do top)
    nomes_top = [x["produto"] for x in linhas[:TOP_N]]
    detalhe = {}
    for m in muns:
        linha = {
            "c": m["codigo"],
            "v": arred(m[ano]["valor_mil_reais"]),
            "q": arred(m[ano]["producao_t"]),
            "a": arred(m[ano]["area_colhida_ha"]),
            "r": arred(m[ano]["rendimento_kg_ha"], 0),
        }
        prods_mun = {}
        for p in nomes_top:
            d = m["produtos"].get(p, {}).get(ano)
            if d and d.get("215"):
                prods_mun[p] = [
                    arred(d.get("214")),
                    arred(d.get("216")),
                    arred(d.get("215")),
                ]
        linha["p"] = prods_mun
        detalhe[m["codigo"]] = linha

    # ---------------- mapa: bounding box + geometria enxuta
    mapa = base["mapa"]
    lons, lats = [], []
    feats = []
    for f in mapa["features"]:
        geometrias = []
        aneis = f["geometry"]["coordinates"]
        if f["geometry"]["type"] == "Polygon":
            aneis = [aneis]
        for poli in aneis:
            anel = []
            for x, y in poli[0]:
                anel.append([round(x, 4), round(y, 4)])
                lons.append(x)
                lats.append(y)
            geometrias.append(anel)
        feats.append(
            {"codigo": f["properties"]["codigo"],
             "nome": f["properties"]["nome"],
             "g": geometrias}
        )
    bbox = [round(min(lons), 4), round(min(lats), 4), round(max(lons), 4), round(max(lats), 4)]

    # ---------------- qualidade dos dados
    z = sum(m[ano]["celulas_zero"] for m in muns)
    ind = sum(m[ano]["celulas_indisponivel"] for m in muns)
    total_cel = 217 * 85 * 5
    qualidade = {
        "celulas_total": total_cel,
        "celulas_zero": z,
        "celulas_indisponivel": ind,
        "celulas_completas": total_cel - z - ind,
        "pct_completas": arred(100.0 * (total_cel - z - ind) / total_cel, 1),
        "pct_indisponivel": arred(100.0 * ind / total_cel, 1),
        "media_produtos_mun": arred(sum(m[ano]["n_produtos"] for m in muns) / len(muns), 1),
        "municipios_com_dado": sum(1 for m in muns if m[ano]["valor_mil_reais"]),
        "reconciliacao_valor": arred(
            100.0 * (sum(m[ano]["valor_mil_reais"] for m in muns) - agora["valor_mil_reais"])
            / agora["valor_mil_reais"], 4),
    }

    # ---------------- numeros-chave
    kpis = [
        {"rot": "Produção agrícola", "valor": arred(agora["producao_t"]), "un": "t",
         "delta": pct(agora["producao_t"], antes["producao_t"]), "nota": "soma dos 85 produtos"},
        {"rot": "Área colhida", "valor": arred(agora["area_colhida_ha"]), "un": "ha",
         "delta": pct(agora["area_colhida_ha"], antes["area_colhida_ha"]), "nota": "área efetivamente colhida"},
        {"rot": "Valor da produção", "valor": arred(agora["valor_mil_reais"]), "un": "mil R$",
         "delta": pct(agora["valor_mil_reais"], antes["valor_mil_reais"]), "nota": "a preços correntes"},
        {"rot": "Rendimento médio", "valor": arred(agora["rendimento_kg_ha"]), "un": "kg/ha",
         "delta": pct(agora["rendimento_kg_ha"], antes["rendimento_kg_ha"]),
         "nota": "calculado (IBGE não publica o total)"},
    ]
    derivados = [
        {"rot": "Valor por hectare", "valor": arred(agora["valor_mil_reais"] * 1000 / agora["area_colhida_ha"]),
         "un": "R$/ha"},
        {"rot": "Soja no valor do estado", "valor": linhas[0]["part_valor"], "un": "%",
         "rot2": linhas[0]["produto"]},
        {"rot": "Top 10 municípios", "valor": share_em(10), "un": "%",
         "rot2": "do valor do estado"},
        {"rot": "Municípios com dado", "valor": qualidade["municipios_com_dado"], "un": "de 217"},
    ]

    painel = {
        "meta": {
            "titulo": "Produção agrícola do Maranhão em 2025",
            "orgao": "IBGE",
            "pesquisa": "PAM - Pesquisa Agropecuária Municipal",
            "tabela_sidra": 5457,
            "ano": ANO,
            "ano_ant": ANO_ANT,
            "publicado_em": base["fonte"]["publicado_em"],
            "gerado_em": base["fonte"]["gerado_em"],
            "url_sidra": base["fonte"]["url_sidra"],
            "url_mapa": base["fonte"]["url_mapa"],
            "variaveis": {
                "214": "Quantidade produzida (t)",
                "112": "Rendimento médio (kg/ha)",
                "8331": "Área plantada ou destinada à colheita (ha)",
                "216": "Área colhida (ha)",
                "215": "Valor da produção (mil R$)",
            },
            "n_municipios": len(muns),
            "n_produtos_lavoura": 85,
        },
        "kpis": kpis,
        "derivados": derivados,
        "serie": serie,
        "produtos": linhas,
        "total_produtos_valor": total_top,
        "top_n": TOP_N,
        "ranking": ranking,
        "pareto": pareto,
        "detalhe": detalhe,
        "mapa": {"bbox": bbox, "features": feats},
        "qualidade": qualidade,
        "top_nomes": nomes_top,
    }

    destino = os.path.join(SAIDA, "painel.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(painel, fh, ensure_ascii=False, separators=(",", ":"))
    print("pronto -> %s (%.0f KB)" % (destino, os.path.getsize(destino) / 1024))
    print("  kpis:", [(k["rot"], k["valor"], k["un"]) for k in kpis])
    print("  bbox:", bbox)
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())