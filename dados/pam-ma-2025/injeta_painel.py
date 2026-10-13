"""
injeta_painel.py
Cola o payload (saida/painel.json) dentro do HTML do painel, no marcador
/*__PAINEL__*/. Assim o painel abre offline, sem depender de servidor nem de CDN.

Como rodar:
  python dados/pam-ma-2025/injeta_painel.py
"""

import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
HTML = os.path.join(RAIZ, "pam-ma-2025.html")
PAINEL = os.path.join(AQUI, "saida", "painel.json")


def principal():
    with open(PAINEL, encoding="utf-8") as fh:
        dados = fh.read()
    json.loads(dados)  # valida antes de colar no HTML
    with open(HTML, encoding="utf-8") as fh:
        html = fh.read()

    # o payload mora no primeiro bloco <script> do arquivo; qualquer que seja o
    # conteudo atual dele, e substituido. assim da pra re-injetar sem passos extras
    inicio = html.index("<script>")
    fim = html.index("</script>", inicio)
    html = html[:inicio] + "<script>\nvar D = " + dados + "\n" + html[fim:]

    with open(HTML, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("painel injetado -> %s (%.0f KB)" % (HTML, os.path.getsize(HTML) / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())