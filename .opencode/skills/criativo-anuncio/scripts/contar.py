# -*- coding: utf-8 -*-
"""Conta caracteres de cada campo de um criativo e compara com o recomendado.

Uso:  python contar.py  (os textos sao lidos de um arquivo JSON)

Formato do JSON de entrada:
    {"primary_text": ["...", "..."], "headline": ["...", "..."],
     "description": ["...", "..."]}

Recomendacoes da Meta (ver references/normas-e-limites.md, lido em 13/10/2026):
texto principal 125, titulo 40, descricao 25 caracteres. Sao recomendacoes
de exibicao, nao limites tecnicos.
"""

import json
import sys

RECOMENDADO = {
    "primary_text": 125,
    "headline": 40,
    "description": 25,
}

ROTULO = {
    "primary_text": "Texto principal",
    "headline": "Titulo",
    "description": "Descricao",
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Uso: python contar.py criativos.json")
        return

    with open(sys.argv[1], encoding="utf-8") as f:
        dados = json.load(f)

    for campo, textos in dados.items():
        limite = RECOMENDADO.get(campo)
        print("\n%s%s" % (ROTULO.get(campo, campo),
                          "" if limite is None else "  (recomendado: %d)" % limite))
        for i, txt in enumerate(textos, 1):
            n = len(txt)
            if limite is None:
                marca = "  sem valor confirmado"
            elif n <= limite:
                marca = "  ok"
            else:
                marca = "  ACIMA do recomendado, entrega tambem a versao curta"
            print("  V%d  %4d caracteres%s" % (i, n, marca))
            print("      %s" % txt)


if __name__ == "__main__":
    main()