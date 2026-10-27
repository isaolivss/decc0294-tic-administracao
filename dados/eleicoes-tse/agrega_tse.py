#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agrega a votacao por secao do TSE (Presidente 2026) em um JSON pequeno
que o HTML consome embutido.

Fonte: https://dadosabertos.tse.jus.br/api/3/action/package_show?id=resultados-2026
Arquivo: votacao_secao_2026_BR.zip (votacao_secao_2026_BR.csv)

Regras de contagem (explicitas de proposito):
  - voto nominal  = NR_VOTAVEL diferente de 95 (branco) e 96 (nulo)
  - voto valido   = soma dos nominais
  - secao         = combinacao unica de UF + municipio + zona + secao
Nada e estimado, nada e digitado a mao.
"""
import csv
import io
import json
import os
import sys
import zipfile
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(BASE, "bruto", "votacao_secao_2026_BR.zip")
SAIDA = os.path.join(BASE, "agregado-presidente-2026.json")

COD_BRANCO = "95"
COD_NULO = "96"


def abre_csv(caminho_zip):
    z = zipfile.ZipFile(caminho_zip)
    nome = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    bruto = z.open(nome)
    texto = io.TextIOWrapper(bruto, encoding="latin-1", newline="")
    return nome, csv.DictReader(texto, delimiter=";")


def main():
    nome_arq, leitor = abre_csv(ZIP)
    print("arquivo:", nome_arq)

    nominais = defaultdict(lambda: defaultdict(Counter))   # [turno][uf][nr]
    brancos = defaultdict(lambda: defaultdict(int))        # [turno][uf]
    nulos = defaultdict(lambda: defaultdict(int))
    codigos = Counter()
    nomes = {}
    secoes = defaultdict(set)                               # [turno][uf] -> set
    municipios = defaultdict(set)                           # [uf] -> set
    cargos = Counter()
    linhas = 0

    for linha in leitor:
        cargo = linha.get("DS_CARGO", "").strip()
        cargos[cargo] += 1
        if cargo != "Presidente":
            continue
        linhas += 1
        turno = linha.get("NR_TURNO", "").strip()
        uf = linha.get("SG_UF", "").strip()
        nr = linha.get("NR_VOTAVEL", "").strip()
        codigos[nr] += 1
        nomes.setdefault(nr, linha.get("NM_VOTAVEL", "").strip())
        q = linha.get("QT_VOTOS", "").strip()
        q = int(q) if q.isdigit() else 0

        secoes[turno].add((uf, linha.get("CD_MUNICIPIO", ""), linha.get("NR_ZONA", ""),
                           linha.get("NR_SECAO", "")))
        if uf:
            municipios[uf].add(linha.get("CD_MUNICIPIO", ""))

        if nr == COD_BRANCO:
            brancos[turno][uf] += q
        elif nr == COD_NULO:
            nulos[turno][uf] += q
        else:
            nominais[turno][uf][nr] += q

    print("linhas de presidente:", linhas)
    print("outros cargos no arquivo:", [c for c in cargos if c != "Presidente"][:10])
    print("codigos de voto vistos:", sorted(codigos))

    # secoes por (turno, uf)
    sec_por_uf = defaultdict(dict)
    for turno, chaves in secoes.items():
        cont = Counter(c[0] for c in chaves)
        sec_por_uf[turno] = dict(cont)

    saida = {"fonte_arquivo": nome_arq, "linhas_presidente": linhas, "turnos": {}}

    for turno in sorted(nominais):
        por_uf = {}
        total_nominal = 0
        total_branco = 0
        total_nulo = 0
        acumulado = Counter()
        for uf in sorted(nominais[turno]):
            votos = dict(nominais[turno][uf])
            nom = sum(votos.values())
            acumulado.update(votos)
            total_nominal += nom
            total_branco += brancos[turno].get(uf, 0)
            total_nulo += nulos[turno].get(uf, 0)
            por_uf[uf] = {
                "validos": nom,
                "brancos": brancos[turno].get(uf, 0),
                "nulos": nulos[turno].get(uf, 0),
                "total": nom + brancos[turno].get(uf, 0) + nulos[turno].get(uf, 0),
                "secoes": sec_por_uf[turno].get(uf, 0),
                "municipios": len([m for m in municipios[uf] if m]),
                "votos": votos,
            }
        saida["turnos"][turno] = {
            "validos": total_nominal,
            "brancos": total_branco,
            "nulos": total_nulo,
            "total": total_nominal + total_branco + total_nulo,
            "secoes": len(secoes[turno]),
            "votos": dict(acumulado),
            "ufs": por_uf,
        }

    saida["candidatos"] = {nr: nomes[nr] for nr in nomes}

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)

    print("gravado:", SAIDA)
    for turno, d in saida["turnos"].items():
        print("\n== turno %s == secoes %d | validos %d | brancos %d | nulos %d | total %d"
              % (turno, d["secoes"], d["validos"], d["brancos"], d["nulos"], d["total"]))
        for nr, q in sorted(d["votos"].items(), key=lambda x: -x[1]):
            print("   %-3s %-40s %10d  %5.2f%%" % (
                nr, nomes[nr], q, 100.0 * q / max(d["validos"], 1)))


if __name__ == "__main__":
    sys.exit(main())
