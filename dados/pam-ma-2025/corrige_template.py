"""Aplica as correcoes de texto e de logica no template do painel.

Uso: python dados/pam-ma-2025/corrige_template.py
Roda uma vez, depois re-injete o payload com injeta_painel.py
"""
import io
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
HTML = os.path.join(RAIZ, "pam-ma-2025.html")

TROCAS = [
    # --- caracteres corrompidos que apareceram na digitacao
    ("A芬 redação final", "A redação final"),
    ("não cobre敖 pecuária", "não cobre a pecuária"),
    ("não纯洁 divulgado", "não divulgado"),
    ("produ\ufffd\ufffdão", "produção"),
    ("cruzar com<CENSO AGROPECUÁRIO</C> e com o <b>IBGE Cidades</b>",
     "cruzar com o <b>Censo Agropecuário</b> e com o <b>IBGE Cidades</b>"),
    # --- erros de português
    ("totais recalculados", "totais recalculados"),
    ("debuffers anuais", "de buffers anuais"),
    ("de agriculture precisa", "de agricultura precisa"),
    ("não como fechou.", "não como fechamento."),
    ("muitaTON por hectare", "muita TON por hectare"),
    ("release de \" + M.publicado_em", "liberada em \" + M.publicado_em"),
    ("<span style='font-size:22px'> mil</span>", "<span style='font-size:22px'> mil</span>"),
]


def principal():
    with io.open(HTML, encoding="utf-8") as fh:
        s = fh.read()

    for velho, novo in TROCAS:
        if velho not in s:
            print("AVISO: nao achei -> %r" % velho[:60])
            continue
        s = s.replace(velho, novo)

    with io.open(HTML, "w", encoding="utf-8") as fh:
        fh.write(s)
    print("template corrigido -> %s" % HTML)
    return 0


if __name__ == "__main__":
    sys.exit(principal())