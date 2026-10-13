#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
turnover.py - calcula a taxa de rotatividade a partir de um CSV de movimentacoes.

Este script faz SO aritmetica. Ele nao interpreta, nao julga se o resultado e
bom ou ruim e nao compara com mercado. Essa parte e da skill e de gente.

Formulas implementadas:

  caged : TR = min(A, D) / E x 100
          Ministerio do Trabalho e Emprego, pagina "O que e CAGED".

  shrm  : TR = D / quadro medio x 100
          quadro medio = (estoque no dia 1 + estoque no ultimo dia) / 2
          Referencia de mercado da SHRM.

Uso:
  python turnover.py dados.csv --mes 2026-09
  python turnover.py dados.csv --mes 2026-09 --formula shrm
  python turnover.py dados.csv --mes 2026-09 --area Vendas
  python turnover.py dados.csv --confere

Somente biblioteca padrao. Sem pip install, sem rede.
"""

import argparse
import csv
import sys
from datetime import date

# No terminal do Windows o padrao e cp1252, e acento vira lixo. Forcar UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

COLUNAS_OBRIGATORIAS = ["id", "area", "admissao", "desligamento", "motivo"]

MOTIVO_VOLUNTARIO = {"espontaneo", "pedido de demissao", "pedido", "rescisao"}
MOTIVO_INVOLUNTARIO = {"dispensado", "demissao", "demitido", "desligamento por justa causa"}
MOTIVO_NEUTRO = {"aposentado", "morte", "transferido", "cessao"}

FORMULAS = {
    "caged": "TR = min(A, D) / E x 100   (Ministerio do Trabalho e Emprego, CAGED)",
    "shrm": "TR = D / quadro medio x 100   (SHRM)",
}


# ----------------------------------------------------------------------------- utilidades
def erro(msg):
    sys.stderr.write("ERRO: %s\n" % msg)
    sys.exit(1)


def parse_data(texto, campo, linha):
    try:
        partes = texto.strip().split("-")
        if len(partes) != 3:
            raise ValueError
        return date(int(partes[0]), int(partes[1]), int(partes[2]))
    except Exception:
        erro("linha %d: campo '%s' com data invalida: %r (use AAAA-MM-DD)"
             % (linha, campo, texto))


def parse_mes(texto):
    try:
        ano, mes = texto.strip().split("-")
        return date(int(ano), int(mes), 1)
    except Exception:
        erro("mes invalido: %r (use AAAA-MM)" % texto)


def primeiro_dia_seguinte(d):
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def fim_do_mes(d):
    return date.fromordinal(primeiro_dia_seguinte(d).toordinal() - 1)


def meses_entre(inicio, fim):
    m = (fim.year - inicio.year) * 12 + (fim.month - inicio.month)
    if fim.day < inicio.day:
        m -= 1
    return m


def pct(num, den):
    if den == 0:
        return None
    return round(num / den * 100.0, 2)


# ----------------------------------------------------------------------------- carga
def conferir_arquivo(caminho):
    """Le e valida o CSV. Sai com codigo 1 e a lista do que falta."""
    try:
        with open(caminho, newline="", encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            campos = leitor.fieldnames or []
            linhas = list(leitor)
    except FileNotFoundError:
        erro("arquivo nao encontrado: %s" % caminho)
    except UnicodeDecodeError:
        erro("o arquivo precisa estar em UTF-8")

    problemas = []

    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in campos]
    if faltando:
        problemas.append("colunas ausentes no cabecalho: %s" % ", ".join(faltando))
        problemas.append("o cabecalho minimo e: %s" % ",".join(COLUNAS_OBRIGATORIAS))

    if not linhas:
        problemas.append("o arquivo nao tem nenhuma linha de dados")

    registros = []
    for i, bruta in enumerate(linhas, start=2):
        registro = {
            "id": (bruta.get("id") or "").strip(),
            "area": (bruta.get("area") or "").strip(),
            "admissao": parse_data(bruta.get("admissao") or "", "admissao", i),
            "desligamento": None,
            "motivo": (bruta.get("motivo") or "").strip(),
        }
        if bruta.get("desligamento"):
            registro["desligamento"] = parse_data(
                bruta["desligamento"], "desligamento", i)

        if not registro["id"]:
            problemas.append("linha %d: campo 'id' vazio" % i)
        if not registro["area"]:
            problemas.append("linha %d: campo 'area' vazio" % i)

        d = registro["desligamento"]
        if d and d < registro["admissao"]:
            problemas.append("linha %d: desligamento (%s) anterior a admissao (%s)"
                             % (i, d, registro["admissao"]))
        if d and not registro["motivo"]:
            problemas.append("linha %d: tem desligamento e nao tem motivo" % i)
        if not d and registro["motivo"]:
            problemas.append("linha %d: tem motivo e nao tem desligamento" % i)
        if registro["motivo"] and registro["motivo"].lower() not in (
                MOTIVO_VOLUNTARIO | MOTIVO_INVOLUNTARIO | MOTIVO_NEUTRO):
            problemas.append("linha %d: motivo '%s' nao esta na lista conhecida %s"
                             % (i, registro["motivo"],
                                sorted(MOTIVO_VOLUNTARIO | MOTIVO_INVOLUNTARIO | MOTIVO_NEUTRO)))

        registros.append(registro)

    if problemas:
        sys.stderr.write("A base nao serve para calcular. Corrigir:\n")
        for p in problemas:
            sys.stderr.write("  - %s\n" % p)
        sys.exit(1)

    return registros


# ----------------------------------------------------------------------------- calculo
def ativos_em(registros, dia):
    """Quem estava empregado no dia informado."""
    total = 0
    for r in registros:
        if r["admissao"] <= dia:
            if r["desligamento"] is None or r["desligamento"] > dia:
                total += 1
    return total


def calcular(registros, mes, formula):
    fim = fim_do_mes(mes)
    inicial = ativos_em(registros, mes)          # E(t): estoque no 1o dia
    final = ativos_em(registros, fim)             # estoque no ultimo dia

    admitidos = [r for r in registros if mes <= r["admissao"] <= fim]
    desligados = [r for r in registros if r["desligamento"] and mes <= r["desligamento"] <= fim]

    A, D = len(admitidos), len(desligados)
    quadro_medio = (inicial + final) / 2.0

    if formula == "caged":
        numerador = min(A, D)
        denominador = inicial
        rotulo_den = "E(t) = estoque no 1o dia do mes"
    else:
        numerador = D
        denominador = quadro_medio
        rotulo_den = "quadro medio = (inicio %d + fim %d) / 2" % (inicial, final)

    tr = pct(numerador, denominador) if denominador else None

    return {
        "mes": "%04d-%02d" % (mes.year, mes.month),
        "formula": formula,
        "rotulo_den": rotulo_den,
        "admissoes": A,
        "desligamentos": D,
        "saldo": A - D,
        "estoque_inicial": inicial,
        "estoque_final": final,
        "quadro_medio": quadro_medio,
        "numerador": numerador,
        "denominador": denominador,
        "tr": tr,
        "variacao_relativa": pct(A - D, inicial),
        "admitidos": admitidos,
        "desligados": desligados,
    }


def por_area(registros, mes):
    fim = fim_do_mes(mes)
    areas = sorted(set(r["area"] for r in registros))
    linhas = []
    for area in areas:
        do_area = [r for r in registros if r["area"] == area]
        linha = calcular(do_area, mes, "caged")
        linha["area"] = area
        linhas.append(linha)
    return linhas


def classificar(motivo):
    m = motivo.lower()
    if m in MOTIVO_VOLUNTARIO:
        return "voluntario"
    if m in MOTIVO_INVOLUNTARIO:
        return "involuntario"
    return "neutro"


# ----------------------------------------------------------------------------- relatorio
def titulo(txt):
    print("")
    print(txt)
    print("-" * len(txt))


def main():
    ap = argparse.ArgumentParser(
        description="Calcula a taxa de rotatividade de um CSV de movimentacoes.")
    ap.add_argument("csv", help="caminho do CSV de movimentacoes")
    ap.add_argument("--mes", help="mes de referencia, no formato AAAA-MM")
    ap.add_argument("--formula", choices=sorted(FORMULAS), default="caged",
                    help="formula a usar (padrao: caged)")
    ap.add_argument("--area", help="calcula apenas esta area")
    ap.add_argument("--confere", action="store_true",
                    help="apenas valida o CSV e sai")
    args = ap.parse_args()

    registros = conferir_arquivo(args.csv)

    if args.confere:
        print("Conferencia OK: %d registros, colunas %s."
              % (len(registros), ", ".join(COLUNAS_OBRIGATORIAS)))
        return

    if not args.mes:
        erro("informe --mes AAAA-MM (ou use --confere so para validar a base)")

    mes = parse_mes(args.mes)
    if args.area:
        registros = [r for r in registros if r["area"] == args.area]
        if not registros:
            erro("nenhum registro na area '%s'" % args.area)

    r = calcular(registros, mes, args.formula)

    titulo("Indicadores de %s" % r["mes"])
    print("Formula usada .. %s" % FORMULAS[r["formula"]])
    print("Denominador .. %s = %s" % (r["rotulo_den"], r["denominador"]))
    print("")
    print("  A - admissoes no mes ......... %d" % r["admissoes"])
    print("  D - desligamentos no mes ..... %d" % r["desligamentos"])
    print("  E - estoque no 1o dia ........ %d" % r["estoque_inicial"])
    print("  Estoque no fim do mes ....... %d" % r["estoque_final"])
    print("  Saldo (A - D) ................ %+d" % r["saldo"])
    if r["formula"] == "caged":
        print("  Numerador = min(A, D) ........ %d" % r["numerador"])
    else:
        print("  Quadro medio ................ %.1f" % r["quadro_medio"])
    print("")
    print("  TAXA DE ROTATIVIDADE ........ %s %%" % r["tr"])
    print("  Variacao relativa do emprego . %s %%" % r["variacao_relativa"])

    if r["formula"] == "caged" and r["admissoes"] != r["desligamentos"]:
        print("")
        print("  ATENCAO: A(%d) e D(%d) sao diferentes. A taxa usa min(A, D) = %d."
              % (r["admissoes"], r["desligamentos"], r["numerador"]))
        print("  O numero maior da mesa de desligamentos abaixo NAO aparece na taxa.")

    titulo("Desligamentos por tipo")
    grupos = {}
    for d in r["desligados"]:
        grupos.setdefault(classificar(d["motivo"]), []).append(d)
    if not grupos:
        print("  nenhum desligamento no mes")
    for tipo in ("voluntario", "involuntario", "neutro"):
        itens = grupos.get(tipo, [])
        print("  %-13s %d  %s" % (tipo, len(itens),
                                 "(" + ", ".join(sorted(set(i["motivo"] for i in itens))) + ")"
                                 if itens else ""))

    titulo("Tempo de empresa de quem saiu")
    if r["desligados"]:
        print("  %-10s %-16s %-14s %-14s %s" % ("id", "area", "admissao", "saida", "meses"))
        for d in sorted(r["desligados"], key=lambda x: x["desligamento"]):
            print("  %-10s %-16s %-14s %-14s %d" % (
                d["id"], d["area"], d["admissao"], d["desligamento"],
                meses_entre(d["admissao"], d["desligamento"])))
        tempos = [meses_entre(d["admissao"], d["desligamento"]) for d in r["desligados"]]
        print("")
        print("  menor %d meses | mediana %d meses | maior %d meses"
              % (min(tempos), sorted(tempos)[len(tempos) // 2], max(tempos)))
    else:
        print("  ninguem saiu no mes")

    titulo("Por area (sempre com a formula CAGED)")
    print("  %-16s %5s %5s %5s %9s" % ("area", "A", "D", "E", "TR %"))
    for linha in por_area(registros, mes):
        print("  %-16s %5d %5d %5d %9s" % (
            linha["area"], linha["admissoes"], linha["desligamentos"],
            linha["estoque_inicial"], linha["tr"]))
    print("")
    print("  A area com D grande e TR baixo e justamente onde o indicador agregado")
    print("  esconde o problema. Compare sempre a coluna D com a coluna TR.")

    titulo("Avisos")
    print("  Este script nao diz se o resultado e alto ou baixo. Nao ha valor de")
    print("  referencia confiavel por setor nas fontes consultadas: escrever NAO SEI.")
    print("  A taxa cobre apenas o quadro da base. Confirmar a cobertura antes de")
    print("  comparar com CAGED, que cobre celetistas e cerca de 85% do universo.")


if __name__ == "__main__":
    main()