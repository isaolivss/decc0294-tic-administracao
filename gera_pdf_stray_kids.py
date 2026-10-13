# -*- coding: utf-8 -*-
"""
Gera 'stray-kids.pdf': um dossiê visual sobre o grupo Stray Kids (SKZ).

Identidade visual do arquivo:
  - preto e vermelho  -> cores mais associadas ao grupo (ver seção de fontes)
  - dourado           -> referência ao álbum "5-Star"
  - creme/cinza       -> base de leitura

Rode:  python gera_pdf_stray_kids.py
"""

import os
import math

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----------------------------------------------------------------------------- setup
W, H = A4
MARGIN = 48
CW = W - 2 * MARGIN          # largura útil da página
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "stray-kids.pdf")

pdfmetrics.registerFont(TTFont("Black", r"C:\Windows\Fonts\ariblk.ttf"))
pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))

F_BLACK = "Black"      # display (latino básico)
F_KOR = "Malgun"        # hangul e hanja
F_BL = "Helvetica-Bold"
F_REG = "Helvetica"
F_IT = "Helvetica-Oblique"

# ----------------------------------------------------------------------------- paleta
PRETO = HexColor("#0B0B0D")
CARVAO = HexColor("#1A1A1F")
VERMELHO = HexColor("#E4002B")
VERMELHO_ESC = HexColor("#8E0019")
BRANCO = HexColor("#FFFFFF")
CREME = HexColor("#F4F2EF")
CINZA = HexColor("#8C8C94")
CINZA_ESC = HexColor("#2A2A30")
CINZA_CLARO = HexColor("#C9C6C2")
DOURADO = HexColor("#C9A227")
CINZA_LINHA = HexColor("#DAD6D0")

DATA_HOJE = "13 de outubro de 2026"

# ----------------------------------------------------------------------------- helpers
def wrap(text, font, size, maxw):
    """Quebra texto em linhas respeitando a largura."""
    out = []
    for bloco in text.split("\n"):
        atual = ""
        for p in bloco.split():
            teste = (atual + " " + p).strip()
            if pdfmetrics.stringWidth(teste, font, size) <= maxw or not atual:
                atual = teste
            else:
                out.append(atual)
                atual = p
        out.append(atual)
    return out


def linha(c, x, ytopo, txt, font, size, cor, align="l", maxw=None):
    """Desenha uma linha única. ytopo = topo da caixa do texto."""
    c.setFont(font, size)
    c.setFillColor(cor)
    if align == "c":
        x = x + (maxw - pdfmetrics.stringWidth(txt, font, size)) / 2.0
    elif align == "r":
        x = x + maxw - pdfmetrics.stringWidth(txt, font, size)
    c.drawString(x, H - ytopo - size * 0.80, txt)


def paragrafo(c, x, ytopo, txt, font, size, cor, maxw, leading=None, align="l"):
    """Parágrafo com quebra automática. Retorna o Y abaixo do bloco."""
    leading = leading if leading else size * 1.38
    y = ytopo
    for l in wrap(txt, font, size, maxw):
        linha(c, x, y, l, font, size, cor, align=align, maxw=maxw)
        y += leading
    return y


def paragrafo_misto(c, x, ytopo, partes, size, maxw, leading=None):
    """Parágrafo com trocas de fonte no meio. partes = [(texto, fonte, cor), ...]"""
    leading = leading if leading else size * 1.38
    tokens = [(w, f, cor) for (t, f, cor) in partes for w in t.split() if w]
    y = ytopo
    atual, larg = [], 0.0

    def fechar():
        nonlocal y, atual, larg
        cx = x
        for (w, f, cor) in atual:
            linha(c, cx, y, w, f, size, cor)
            cx += pdfmetrics.stringWidth(w + " ", f, size)
        y += leading
        atual, larg = [], 0.0

    for (w, f, cor) in tokens:
        wl = pdfmetrics.stringWidth(w + " ", f, size)
        if atual and larg + wl > maxw:
            fechar()
        atual.append((w, f, cor))
        larg += wl
    if atual:
        fechar()
    return y


def caixa(c, x, y, w, h, fill=None, stroke=None, lw=0.8):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
    if radius_pad := 0:
        pass
    c.rect(x, H - y - h, w, h, stroke=0, fill=1)


def estrela(c, cx, cy, r, interno=0.45, rot=-90):
    """Estrela de 5 pontas, centro em coordenadas PDF."""
    pontos = []
    for i in range(10):
        ang = math.radians(rot + i * 36)
        ra = r if i % 2 == 0 else r * interno
        pontos.append((cx + ra * math.cos(ang), cy + ra * math.sin(ang)))
    path = c.beginPath()
    path.moveTo(*pontos[0])
    for p in pontos[1:]:
        path.lineTo(*p)
    path.close()
    c.drawPath(path, stroke=0, fill=1)


def meia_tinta(c, x, y, cols, linhas_, passo, cor, raio=1.1):
    c.setFillColor(cor)
    for i in range(cols):
        for j in range(linhas_):
            c.circle(x + i * passo, H - y - j * passo, raio, stroke=0, fill=1)


def faixa_diagonal(c, x, y, w, h, ang, cor):
    c.saveState()
    c.translate(x, y)
    c.rotate(ang)
    c.setFillColor(cor)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.restoreState()


# ----------------------------------------------------------------------------- moldura
def cabecalho(c, titulo, subtitulo=""):
    caixa(c, 0, 0, W, 96, fill=PRETO)
    faixa_diagonal(c, W - 150, -20, 42, 150, 22, VERMELHO)
    c.setFillColor(VERMELHO)
    estrela(c, W - 74, H - 48, 8)
    c.setFillColor(BRANCO)
    estrela(c, W - 42, H - 34, 4.5)
    linha(c, MARGIN, 26, titulo.upper(), F_BL, 19, BRANCO)
    if subtitulo:
        linha(c, MARGIN, 54, subtitulo, F_REG, 9.5, HexColor("#B9B6B1"))
    caixa(c, MARGIN, 72, 54, 3, fill=VERMELHO)


def rodape(c):
    caixa(c, 0, H - 44, W, 44, fill=CREME)
    c.setStrokeColor(CINZA_LINHA)
    c.setLineWidth(0.6)
    c.line(MARGIN, H - 36, W - MARGIN, H - 36)
    linha(c, MARGIN, H - 28, "STRAY KIDS  ·  DOSSIÊ VISUAL", F_BL, 7.5, CINZA)
    linha(c, W - MARGIN - 60, H - 28, "p. %d" % c.getPageNumber(), F_BL, 7.5, CINZA,
          align="r", maxw=60)


def nova_pagina(c, titulo, sub=""):
    c.showPage()
    c.setFillColor(CREME)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    cabecalho(c, titulo, sub)
    rodape(c)


# ============================================================================= PÁGINA 1
def p1_capa(c):
    caixa(c, 0, 0, W, H, fill=PRETO)

    faixa_diagonal(c, 300, -60, 26, 980, 22, VERMELHO)
    faixa_diagonal(c, 352, -60, 8, 980, 22, VERMELHO_ESC)

    # círculos concêntricos + estrela (alusão ao "5-Star")
    c.setStrokeColor(HexColor("#26262C"))
    c.setLineWidth(1)
    for r in (150, 116, 82):
        c.circle(W - 128, H - 232, r, stroke=1, fill=0)
    c.setFillColor(VERMELHO)
    estrela(c, W - 128, H - 232, 56)
    c.setFillColor(PRETO)
    estrela(c, W - 128, H - 232, 34)

    meia_tinta(c, MARGIN, H - 470, 16, 7, 13, HexColor("#26262C"), 1.3)

    caixa(c, MARGIN, 62, 10, 10, fill=VERMELHO)
    linha(c, MARGIN + 20, 60, "JYP ENTERTAINMENT", F_BL, 8.5, BRANCO)
    linha(c, MARGIN + 20, 76, "SEUL  ·  DEBUT 26.03.2018", F_REG, 8.5, HexColor("#8E8E96"))

    linha(c, MARGIN, 168, "STRAY", F_BLACK, 104, BRANCO)
    linha(c, MARGIN - 4, 276, "KIDS", F_BLACK, 104, VERMELHO)
    caixa(c, MARGIN, 322, 232, 6, fill=BRANCO)

    linha(c, MARGIN, 352, "oito vozes, uma unidade de produção,", F_IT, 12, HexColor("#A8A6AC"))
    linha(c, MARGIN, 372, "milhões de cópias e um nome de fandom", F_IT, 12, HexColor("#A8A6AC"))

    caixa(c, MARGIN, 428, 250, 62, fill=CARVAO)
    caixa(c, MARGIN, 428, 6, 62, fill=VERMELHO)
    linha(c, MARGIN + 20, 442, "STAY", F_BLACK, 30, BRANCO)
    linha(c, MARGIN + 20, 472, "nome oficial do fandom · revelado em 02.08.2022",
          F_REG, 7.6, HexColor("#8E8E96"))

    for i, a in enumerate([10, 22, 34, 18, 28, 12, 24, 8]):
        cor = VERMELHO if i % 2 == 0 else BRANCO
        caixa(c, MARGIN + 292 + i * 14, 428 + (34 - a) / 2.0, 7, a, fill=cor)

    linha(c, MARGIN, H - 92, "Documento de estudo visual  ·  feito em " + DATA_HOJE,
          F_REG, 8, HexColor("#6E6E76"))
    linha(c, MARGIN, H - 74, "Cores e números têm fontes declaradas nas páginas 7 e 8.",
          F_IT, 8, HexColor("#6E6E76"))


# ============================================================================= PÁGINA 2
def p2_quem(c):
    nova_pagina(c, "Quem são os Stray Kids", "identidade  ·  formação  ·  fandom")

    y = 132
    y = paragrafo(
        c, MARGIN, y,
        "Stray Kids (SKZ) é um boy band sul-coreano formado pela JYP Entertainment. "
        "O grupo tem oito membros — Bang Chan, Lee Know, Changbin, Hyunjin, Han, Felix, "
        "Seungmin e I.N — e estreou oficialmente em 26 de março de 2018 com o EP I Am Not.",
        F_REG, 10.2, CINZA_ESC, CW, leading=15)

    y += 10
    y = paragrafo(
        c, MARGIN, y,
        "O que chama atenção é o modelo de trabalho: o grupo produz praticamente todo o "
        "próprio material. A unidade de produção interna, o 3RACHA, é formada por Bang Chan, "
        "Changbin e Han, e os demais成员 participam da composição com frequência. Na formação, "
        "o próprio líder escolheu cada integrante da lista de estagiários da JYPE.",
        F_REG, 10.2, CINZA_ESC, CW, leading=15)

    y += 18
    chips = [("8", "membros"), ("2018", "ano de debut"), ("3 RACHA", "unidade de produção")]
    larg = (CW - 2 * 14) / 3.0
    for i, (num, leg) in enumerate(chips):
        x = MARGIN + i * (larg + 14)
        caixa(c, x, y, larg, 64, fill=BRANCO)
        caixa(c, x, y, larg, 4, fill=VERMELHO)
        linha(c, x, y + 18, num, F_BLACK, 21, PRETO, align="c", maxw=larg)
        linha(c, x, y + 46, leg.upper(), F_BL, 7.4, CINZA, align="c", maxw=larg)

    y += 86
    caixa(c, MARGIN, y, CW, 106, fill=BRANCO)
    caixa(c, MARGIN, y, 5, 106, fill=VERMELHO)
    linha(c, MARGIN + 24, y + 20, "POR QUE O NOME IMPORTA", F_BL, 9, VERMELHO)
    paragrafo(
        c, MARGIN + 24, y + 40,
        "Os próprios members idealizaram o nome e desenharam o logo. A ideia nasceu de uma "
        "criança perdida querendo correr atrás do próprio sonho e amadureceu para "
        "“achar um caminho para fora do comum, juntos”. O logo foi desenhado à mão por "
        "Bang Chan e muda de cor a cada era, especialmente a letra K.",
        F_REG, 9, CINZA_ESC, CW - 48, leading=13)

    y += 122
    caixa(c, MARGIN, y, CW, 76, fill=PRETO)
    linha(c, MARGIN + 24, y + 18, "STAY", F_BLACK, 20, VERMELHO)
    paragrafo(
        c, MARGIN + 24, y + 44,
        "Nome oficial do fandom, revelado em 2 de agosto de 2022: é “Stray” sem a letra R. "
        "Em português, STAY também funciona como um “fica” — o compromisso de ficar junto "
        "durante a jornada. O grupo prefere a grafia em inglês.",
        F_REG, 9, CINZA_CLARO, CW - 48, leading=13)


# ============================================================================= PÁGINA 3
def p3_paleta(c):
    nova_pagina(c, "Paleta do grupo", "cores de referência usadas neste arquivo")

    y = 132
    y = paragrafo(
        c, MARGIN, y,
        "Esta paleta não é uma “cor oficial” publicada pela JYP: o grupo não tem uma cor única "
        "de referência divulgada oficialmente, e o próprio logo muda de cor a cada era. O que "
        "circula na fandom — e na linha de produtos — é a associação entre vermelho, preto "
        "e branco. Foi essa leitura que guiou o desenho do documento.",
        F_REG, 10, CINZA_ESC, CW, leading=15)

    y += 16
    swatches = [
        ("VERMELHO SKZ", "#E4002B", "cor de destaque", BRANCO),
        ("VERMELHO PROF.", "#8E0019", "apoio e sombras", BRANCO),
        ("PRETO", "#0B0B0D", "base e fundos", BRANCO),
        ("CARVÃO", "#1A1A1F", "caixas escuras", BRANCO),
        ("BRANCO", "#FFFFFF", "contraste e respiro", PRETO),
        ("DOURADO", "#C9A227", "alusão ao álbum 5-Star", PRETO),
        ("CREME", "#F4F2EF", "fundo de página", PRETO),
        ("CINZA", "#8C8C94", "texto secundário", BRANCO),
    ]
    larg = (CW - 3 * 12) / 4.0
    alt = 112
    for i, (nome, hexa, uso, txtcor) in enumerate(swatches):
        col, lin = i % 4, i // 4
        x = MARGIN + col * (larg + 12)
        yy = y + lin * (alt + 14)
        caixa(c, x, yy, larg, alt, fill=HexColor(hexa), stroke=CINZA_LINHA, lw=0.6)
        linha(c, x + 10, yy + 70, nome, F_BL, 8.4, txtcor)
        linha(c, x + 10, yy + 86, hexa, F_BL, 9.6, txtcor)
        paragrafo(c, x + 10, yy + 102, uso, F_IT, 7.4, txtcor, larg - 20, leading=9)

    y += 2 * (alt + 14) + 8

    caixa(c, MARGIN, y, CW, 172, fill=BRANCO)
    caixa(c, MARGIN, y, 5, 172, fill=DOURADO)
    linha(c, MARGIN + 24, y + 20, "CORES DOS MEMBROS  —  USAR COM CUIDADO", F_BL, 9, DOURADO)
    paragrafo(
        c, MARGIN + 24, y + 38,
        "NÃO CONFIRMADO. A tabela abaixo reproduz a lista da wiki de fandom kpop.fandom, que "
        "não é um anúncio oficial da JYPE. Não encontrei comunicado da agência fixando cores "
        "individuais. Se este material virar texto acadêmico, confirme no canal oficial ou "
        "descartar a seção.",
        F_IT, 8, CINZA, CW - 48, leading=11)

    membro_cores = [
        ("Bang Chan", "#2F6FD0"), ("Lee Know", "#E4002B"), ("Changbin", "#1A1A1A"),
        ("Hyunjin", "#F28522"), ("Han", "#7A4FC0"), ("Felix", "#F2F2F2"),
        ("Seungmin", "#7A4A2B"), ("I.N", None),
    ]
    for i, (nome, hexa) in enumerate(membro_cores):
        col, lin = i % 4, i // 4
        x = MARGIN + 24 + col * ((CW - 48) / 4.0)
        yy = y + 74 + lin * 46
        if hexa is None:
            caixa(c, x, yy + 8, 26, 26, fill=CREME, stroke=CINZA_LINHA, lw=0.6)
            linha(c, x + 34, yy + 12, nome, F_BL, 8.6, CINZA_ESC)
            linha(c, x + 34, yy + 25, "NÃO SEI · não consta na fonte", F_IT, 6.6, CINZA)
        else:
            caixa(c, x, yy + 8, 26, 26, fill=HexColor(hexa), stroke=CINZA_LINHA, lw=0.6)
            linha(c, x + 34, yy + 12, nome, F_BL, 8.6, CINZA_ESC)
            linha(c, x + 34, yy + 25, hexa.upper(), F_IT, 7, CINZA)


# ============================================================================= PÁGINA 4
def p4_timeline(c):
    nova_pagina(c, "Linha do tempo", "do reality ao festival próprio")

    itens = [
        ("2017", "A JYP anuncia o reality de sobrevivência “Stray Kids”. Bang Chan escolhe "
                 "pessoalmente cada membro entre os estagiários da agência."),
        ("08.01.2018", "Lança o EP pré-debut Mixtape, com sete faixas. O clipe de “Hellevator” "
                       "havia sido divulgado antes do programa."),
        ("26.03.2018", "Estreia oficial com o EP I Am Not e o clipe de “District 9”, no "
                       "estádio Jangchung Arena."),
        ("2019", "Trilogia Clé (Miroh, Yellow Wood, Levanter). Em outubro, Woojin deixa o "
                 "grupo por motivos pessoais."),
        ("2020", "Go Live, primeiro álbum de estúdio. “God's Menu” vira o carro-chefe. Estreia "
                 "no Japão com “Top”, que chega ao topo da Oricon."),
        ("2021", "Noeasy é o primeiro álbum do grupo a passar de 1 milhão de cópias. Vence "
                 "Kingdom: Legendary War."),
        ("2022", "Oddinary e Maxident. Maxident vira o primeiro álbum do grupo (e da JYP) a "
                 "vender mais de 2 e de 3 milhões."),
        ("2023", "5-Star alcança 5 milhões certificados pela KMCA. “Lalalala” vira a primeira "
                 "entrada do grupo no Billboard Hot 100."),
        ("2024", "Ate, Hop e “Lose My Breath” com Charlie Puth. Estreia no Met Gala como "
                 "convidado da Tommy Hilfiger."),
        ("2025", "Karma vende 3,03 milhões na primeira semana. “Do It” fecha o ano. Doação de "
                 "800 milhões de wones para as vítimas de incêndios."),
        ("2026", "This & That leva o grupo ao nono álbum seguido no topo do Billboard 200. "
                 "Estreia o festival próprio, StrayCity."),
    ]

    y = 130
    passo = 54
    caixa(c, MARGIN + 46, y - 4, 3, passo * (len(itens) - 1) + 10, fill=HexColor("#E6E2DD"))

    for i, (ano, txt) in enumerate(itens):
        yy = y + i * passo
        caixa(c, MARGIN + 42, yy, 11, 11, fill=VERMELHO)
        caixa(c, MARGIN + 45, yy + 3, 5, 5, fill=BRANCO)
        linha(c, MARGIN + 68, yy - 4, ano, F_BLACK, 12.5, PRETO)
        paragrafo(c, MARGIN + 68, yy + 12, txt, F_REG, 8.4, CINZA_ESC, CW - 68, leading=11)

    caixa(c, MARGIN, H - 108, CW, 34, fill=BRANCO)
    caixa(c, MARGIN, H - 108, 4, 34, fill=VERMELHO)
    linha(c, MARGIN + 18, H - 96,
          "Datas conferidas em verbete enciclopédico. Para publicação, cruzar com a discografia oficial (straykids.jype.com).",
          F_IT, 8, CINZA)


# ============================================================================= PÁGINA 5
def p5_membros(c):
    nova_pagina(c, "Os oito membros", "formação atual e papéis na produção")

    membros = [
        ("BC", "Bang Chan", "Líder e 3 RACHA. Escolheu os membros na formação e desenhou o logo.", VERMELHO),
        ("LN", "Lee Know", "Danceracha. Vocal e um dos núcleos de performance do grupo.", HexColor("#E4002B")),
        ("CB", "Changbin", "3 RACHA. Produção e rap.", HexColor("#1A1A1A")),
        ("HJ", "Hyunjin", "Danceracha. Rap, performance e moda de luxo.", HexColor("#F28522")),
        ("HN", "Han", "3 RACHA. Produção e vocal.", HexColor("#7A4FC0")),
        ("FX", "Felix", "Danceracha. Rap e o vocal grave que virou marca registrada.", HexColor("#F28522")),
        ("SM", "Seungmin", "Vocal. Presente nas faixas mais suaves do repertório.", HexColor("#2F6FD0")),
        ("IN", "I.N", "Maknae, o mais novo do grupo. Vocal.", HexColor("#8E8E96")),
    ]

    larg = (CW - 16) / 2.0
    alt = 112
    topo = 134
    for i, (sigla, nome, papel, cor) in enumerate(membros):
        col, lin = i % 2, i // 2
        x = MARGIN + col * (larg + 16)
        yy = topo + lin * (alt + 14)
        caixa(c, x, yy, larg, alt, fill=BRANCO)
        caixa(c, x, yy, larg, 5, fill=cor)

        c.setFillColor(HexColor("#F0EEEA"))
        c.circle(x + 44, H - yy - 58, 26, stroke=0, fill=1)
        linha(c, x + 18, yy + 44, sigla, F_BLACK, 19, cor, align="c", maxw=52)

        linha(c, x + 84, yy + 26, nome, F_BLACK, 17, PRETO)
        paragrafo(c, x + 84, yy + 48, papel, F_REG, 8.4, CINZA_ESC, larg - 100, leading=11)

    y = topo + 4 * (alt + 14) + 8
    caixa(c, MARGIN, y, CW, 62, fill=PRETO)
    linha(c, MARGIN + 24, y + 18, "DANCERACHA  =  LEE KNOW  +  HYUNJIN  +  FELIX",
          F_BL, 10, BRANCO)
    paragrafo(c, MARGIN + 24, y + 36,
              "Sub-unidade de performance formada em 2021. As cores dos círculos seguem a mesma "
              "lista de fandom da página 3 — ainda não confirmadas em canal oficial.",
              F_REG, 8.2, HexColor("#A8A6AC"), CW - 48, leading=11)


# ============================================================================= PÁGINA 6
def p6_som(c):
    nova_pagina(c, "Som e identidade", "3 RACHA  ·  mala taste  ·  trocadilhos")

    # ---- diagrama 3RACHA
    caixa(c, MARGIN, 132, 250, 250, fill=BRANCO)
    linha(c, MARGIN + 22, 152, "QUEM PRODUZ O QUÊ", F_BL, 8.6, VERMELHO)

    cx, cy = MARGIN + 125, H - 272
    nos = [(MARGIN + 125, H - 190, "Bang Chan"),
           (MARGIN + 62, H - 318, "Changbin"),
           (MARGIN + 188, H - 318, "Han")]
    c.setStrokeColor(HexColor("#DEDAD4"))
    c.setLineWidth(1.2)
    for nx, ny, _ in nos:
        c.line(cx, cy, nx, ny)
    for nx, ny, nome in nos:
        c.setFillColor(CARVAO)
        c.circle(nx, ny, 24, stroke=0, fill=1)
        linha(c, nx - 24, H - ny - 3.6, nome, F_BL, 8, BRANCO, align="c", maxw=48)
    c.setFillColor(VERMELHO)
    c.circle(cx, cy, 30, stroke=0, fill=1)
    linha(c, cx - 30, H - cy - 6.7, "SKZ", F_BLACK, 15, BRANCO, align="c", maxw=60)
    linha(c, MARGIN + 22, 350, "Os três circulos internos escrevem e produzem",
          F_IT, 7.6, CINZA, align="c", maxw=206)

    # ---- coluna direita: mala taste
    x2 = MARGIN + 266
    w2 = CW - 266
    yy = 132
    caixa(c, x2, yy, w2, 118, fill=PRETO)
    linha(c, x2 + 20, yy + 20, "MALATASTE", F_BLACK, 19, VERMELHO)
    paragrafo(c, x2 + 20, yy + 44,
              "Depois de Go Live, imprensa e público passaram a chamar o som do grupo de "
              "“mala taste” (comida apimentada). Em Noeasy, o grupo abraçou a crítica de "
              "“barulhento” e transformou o apelido em arma.",
              F_REG, 8.4, CINZA_CLARO, w2 - 40, leading=11.5)

    # ---- coluna direita: trocadilhos
    yy += 132
    linha(c, x2, yy, "TROCADILHOS E DUPLO SENTIDO", F_BL, 8.6, VERMELHO)
    yy += 14
    trocas = [
        ("Levanter", "바람", "(baram) = vento. A letra fala em chaves que estavam dentro de si."),
        ("Go Live", "GO生", "(go-saeng) tem a mesma pronúncia de 고생, que significa sofrimento."),
        ("Noeasy", "noisy", "O apelido “barulhento” virou identidade assumida."),
        ("God's Menu", "神메뉴", "(sin-menyu) soa como 신메뉴, “cardápio novo”."),
        ("Lalalala", "락 / 樂", "(rak) = prazer; a última emoção, depois do sofrimento."),
    ]
    for titulo, ko, desc in trocas:
        caixa(c, x2, yy, 3, 30, fill=VERMELHO)
        linha(c, x2 + 12, yy, titulo, F_BL, 8.8, PRETO)
        linha(c, x2 + 78, yy + 1, ko, F_KOR, 8.4, VERMELHO)
        paragrafo(c, x2 + 12, yy + 14, desc, F_REG, 7.6, CINZA_ESC, w2 - 16, leading=9.5)
        yy += 34

    # ---- caixa de identidade visual
    caixa(c, MARGIN, 400, 250, H - 84 - 400, fill=BRANCO, stroke=CINZA_LINHA, lw=0.6)
    linha(c, MARGIN + 20, 420, "IDENTIDADE VISUAL", F_BL, 8.6, VERMELHO)
    paragrafo(c, MARGIN + 20, 442,
              "O grupo cultiva o apelido de “concept matjib” (restaurante de conceito): cada "
              "lançamento muda de coreografia, figurino e clipe, mas a base permanece — cores "
              "fortes, humor e performance de palco.",
              F_REG, 8.4, CINZA_ESC, 210, leading=11.5)
    meia_tinta(c, MARGIN + 22, 520, 14, 8, 11, HexColor("#E6E2DD"), 1.2)


# ============================================================================= PÁGINA 7
def p7_numeros(c):
    nova_pagina(c, "Números", "tudo com a fonte ao lado — nada de chute")

    stats = [
        ("8", "membros na formação atual", "verbete enciclopédico, leitura de out/2026"),
        ("26.03.2018", "data do debut oficial", "verbete enciclopédico · I Am Not"),
        ("9", "álbuns seguidos no topo do Billboard 200", "verbete enciclopédico · This & That, 2026"),
        ("40 mi+", "álbuns vendidos até mai/2026 (KR + JP)", "verbete enciclopédico, mai/2026"),
        ("2º", "artista mais vendido do mundo em 2025", "IFPI, citado no verbete enciclopédico"),
        ("5 mi", "cópias de 5-Star, certificado pela KMCA", "verbete enciclopédico, jun/2023"),
        ("270 mil", "público do festival StrayCity", "verbete enciclopédico, set/2026"),
        ("800 mi", "wones doados às vítimas dos incêndios", "verbete enciclopédico, abr/2025"),
    ]
    larg = (CW - 16) / 2.0
    alt = 88
    topo = 132
    for i, (num, leg, fonte) in enumerate(stats):
        col, lin = i % 2, i // 2
        x = MARGIN + col * (larg + 16)
        yy = topo + lin * (alt + 14)
        caixa(c, x, yy, larg, alt, fill=BRANCO)
        caixa(c, x, yy, 5, alt, fill=VERMELHO)
        linha(c, x + 20, yy + 18, num, F_BLACK, 26, PRETO)
        paragrafo(c, x + 20, yy + 52, leg, F_BL, 8.4, CINZA_ESC, larg - 40, leading=10.5)
        linha(c, x + 20, yy + alt - 14, "fonte: " + fonte, F_IT, 6.6, CINZA)

    y = topo + 4 * (alt + 14) + 8
    caixa(c, MARGIN, y, CW, 78, fill=PRETO)
    caixa(c, MARGIN, y, 5, 78, fill=DOURADO)
    linha(c, MARGIN + 22, y + 18, "COMO LER ESTES NÚMEROS", F_BL, 8.6, DOURADO)
    paragrafo(c, MARGIN + 22, y + 36,
              "Vendas físicas coreanas e japonesas não equivalem a streams. Certificações da KMCA "
              "e da RIAA usam critérios próprios de corte. Comparar com outros grupos exige dizer "
              "se o número é de cópias, pré-venda ou streams.",
              F_REG, 8.4, CINZA_CLARO, CW - 44, leading=11.5)


# ============================================================================= PÁGINA 8
def p8_fontes(c):
    nova_pagina(c, "Fontes e limitações", "leia antes de reaproveitar o material")

    y = 132
    linha(c, MARGIN, y, "FONTES CONSULTADAS", F_BL, 8.6, VERMELHO)
    y += 18
    fontes = [
        "Verbete enciclopédico “Stray Kids” (Wikipédia em inglês), leitura de 13/10/2026 — "
        "base para datas, formação, discografia e números de vendas.",
        "straykids.jype.com/discography — discografia oficial. NÃO foi consultada nesta "
        "execução; use para confirmar datas de lançamento.",
        "kpop.fandom.com e stray-kids.fandom.com — wikis de fandom. Usadas apenas como pista "
        "de cor; não são fonte oficial.",
        "Agência Yonhap, citada no verbete enciclopédico a respeito de “God's Menu” — origem do "
        "termo “mala taste”.",
    ]
    for f in fontes:
        caixa(c, MARGIN, y + 4, 3, 12, fill=VERMELHO)
        y = paragrafo(c, MARGIN + 14, y, f, F_REG, 8.6, CINZA_ESC, CW - 14, leading=12) + 8

    y += 6
    linha(c, MARGIN, y, "LIMITAÇÕES DECLARADAS", F_BL, 8.6, VERMELHO)
    y += 18
    lim = [
        "A JYP não publica uma “cor oficial” única do grupo. Vermelho, preto e branco são "
        "associação de fandoms e de linha de produtos, não um anúncio da agência.",
        "As cores individuais dos membros vêm de wiki de fandom e NÃO foram confirmadas em canal "
        "oficial. I.N aparece como NÃO SEI porque a fonte consultada não lista a cor dele.",
        "Números de vendas e posições em rankings envelhecem. Confira a data antes de citar.",
        "Este documento é material de estudo visual, não texto acadêmico. Para a disciplina, "
        "cite a fonte primária: site da JYPE ou do próprio grupo.",
    ]
    for f in lim:
        caixa(c, MARGIN, y + 4, 3, 12, fill=CINZA)
        y = paragrafo(c, MARGIN + 14, y, f, F_REG, 8.6, CINZA_ESC, CW - 14, leading=12) + 8

    y += 10
    caixa(c, MARGIN, y, CW, 132, fill=BRANCO)
    caixa(c, MARGIN, y, 5, 132, fill=DOURADO)
    linha(c, MARGIN + 24, y + 20, "O QUE PRECISA DE DECISÃO HUMANA", F_BL, 9, DOURADO)
    itens = [
        "1. Este PDF é para uso pessoal ou entra como material da disciplina?",
        "2. Manter a seção de cores dos membros ou trocar por uma paleta mais segura?",
        "3. Faltou algum tema que a professora cobra (produção, fandom, globalização)?",
        "4. Autor, data e curso devem aparecer na capa antes da entrega?",
    ]
    yy = y + 42
    for it in itens:
        yy = paragrafo(c, MARGIN + 24, yy, it, F_REG, 8.8, CINZA_ESC, CW - 48, leading=12) + 6

    caixa(c, MARGIN, H - 92, CW, 34, fill=PRETO)
    linha(c, MARGIN + 18, H - 80, "FIM  ·  feito em " + DATA_HOJE, F_BL, 8.6, BRANCO)


# ============================================================================= main
def main():
    c = canvas.Canvas(OUT, pagesize=A4)
    c.setTitle("Stray Kids — Dossiê Visual")
    c.setAuthor("Material de estudo")
    c.setSubject("Dossiê visual sobre o grupo Stray Kids")

    p1_capa(c)
    p2_quem(c)
    p3_paleta(c)
    p4_timeline(c)
    p5_membros(c)
    p6_som(c)
    p7_numeros(c)
    p8_fontes(c)

    c.save()
    print("PDF gerado em:", OUT)
    print("Páginas: 8")


if __name__ == "__main__":
    main()