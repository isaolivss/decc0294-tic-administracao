"""
coleta_pam_ma.py
Coleta de dados da PAM (Pesquisa Agropecuaria Municipal) do IBGE para o
estado do Maranhao (MA), ano de 2025 (e serie de apoio).

Fonte: API SIDRA / IBGE  -  tabela 5457
  https://apisidra.ibge.gov.br/values/t/5457/...
Base geografica: malhas do IBGE (API de malhas, estado 21).

Como rodar:
  python dados/pam-ma-2025/coleta_pam_ma.py

O script grava as respostas brutas em dados/pam-ma-2025/bruto/ (cache) e,
ao final, monta a base consolidada em dados/pam-ma-2025/saida/pam-ma-2025.json.
Se rodar de novo, reaproveita o cache (nao rebaixa nada).

OBS TECNICO IMPORTANTE
  Na tabela 5457 as variaveis 214 (quantidade produzida) e 112 (rendimento
  medio) tem a categoria "Total" marcada como excecao na sumarizacao. Por isso
  o "Total" dessas duas vem como ".." e precisa ser recalculado somando os
  produtos. As demais (8331, 216, 215) tem "Total" publicado.
"""

import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request

# ---------------------------------------------------------------- constantes
AQUI = os.path.dirname(os.path.abspath(__file__))
BRUTO = os.path.join(AQUI, "bruto")
SAIDA = os.path.join(AQUI, "saida")

SIDRA = "https://apisidra.ibge.gov.br/values"
TABELA = 5457          # PAM - Producao Agricola Municipal
VARIAVEIS = "214,112,8331,216,215"
CLASSIF = "c782/all"   # Produto das lavouras temporarias e permanentes
UF = "21"              # Maranhao
ANO_FOCO = 2025
ANOS_SERIE = list(range(2010, ANO_FOCO + 1))
ANOS_MUN = [2025, 2024]

VARS = {
    "214": "Quantidade produzida",
    "112": "Rendimento medio da producao",
    "8331": "Area plantada ou destinada a colheita",
    "216": "Area colhida",
    "215": "Valor da producao",
}

# valores sem informacao no SIDRA
VAZIOS = {"-", "..", "...", "", "x", "X"}

USER_AGENT = "Mozilla/5.0 (student dashboard - PAM/MA)"


# ---------------------------------------------------------------- utilidades
def _descompactar(raw):
    """A API do IBGE devolve gzip em alguns endpoints sem avisar no header."""
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw


def baixar(url, cache=None, tentativas=3):
    """Baixa uma URL JSON, com cache em disco e retentativa."""
    if cache:
        caminho = os.path.join(BRUTO, cache)
        if os.path.exists(caminho):
            with open(caminho, "rb") as fh:
                return json.loads(_descompactar(fh.read()).decode("utf-8"))

    erro = None
    for tentativa in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as resp:
                dados = json.loads(_descompactar(resp.read()).decode("utf-8"))
            if cache:
                os.makedirs(BRUTO, exist_ok=True)
                with open(os.path.join(BRUTO, cache), "w", encoding="utf-8") as fh:
                    json.dump(dados, fh, ensure_ascii=False)
            time.sleep(0.15)  #KG: educado com a API
            return dados
        except urllib.error.HTTPError as exc:
            corpo = exc.read().decode("utf-8", "replace")[:160]
            erro = "HTTP %s - %s" % (exc.code, corpo)
            if exc.code == 400:      # erro de parametro nao adianta repetir
                break
            time.sleep(1.5 * (tentativa + 1))
        except Exception as exc:      # noqa: BLE001
            erro = repr(exc)
            time.sleep(1.5 * (tentativa + 1))

    raise RuntimeError("falha ao baixar %s -> %s" % (url, erro))


def numero(bruto):
    """Converte o texto do SIDRA ('1.234', '..', '-') em float ou None."""
    if bruto is None:
        return None
    txt = str(bruto).strip()
    if txt in VAZIOS:
        return None
    txt = txt.replace(".", "").replace(" ", "").replace(" ", "")
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None


# ---------------------------------------------------------------- coleta
def coletar_municipios():
    """Lista oficial dos 217 municipios do MA (codigo IBGE + nome)."""
    dados = baixar(
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados/%s/municipios" % UF,
        cache="municipios-ma.json",
    )
    return [{"codigo": str(m["id"]), "nome": m["nome"]} for m in dados]


def coletar_mapa():
    """Malhas dos municipios do MA em GeoJSON (qualidade minima)."""
    url = (
        "https://servicodados.ibge.gov.br/api/v3/malhas/estados/%s"
        "?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio" % UF
    )
    return baixar(url, cache="malhas-ma-municipios.json")


def coletar_serie_estado():
    """Totais do estado por ano (variaveis com 'Total' publicado)."""
    anos = ",".join(str(a) for a in ANOS_SERIE)
    url = "%s/t/%d/n3/%s/v/%s/p/%s" % (SIDRA, TABELA, UF, VARIAVEIS, anos)
    return baixar(url, cache="estado-totais-%d-%d.json" % (ANOS_SERIE[0], ANOS_SERIE[-1]))


def coletar_estado_por_produto():
    """Estado x produto x ano: base do ranking de produtos e da serie."""
    bruto = {}
    for ano in ANOS_SERIE:
        url = "%s/t/%d/n3/%s/v/%s/%s/p/%d" % (SIDRA, TABELA, UF, VARIAVEIS, CLASSIF, ano)
        bruto[str(ano)] = baixar(url, cache="estado-produtos-%d.json" % ano)
        print("    estado/produtos/%d ok" % ano)
    return bruto


def coletar_brasil_por_produto(ano):
    """Brasil x produto: base da comparacao de participacao do MA."""
    url = "%s/t/%d/n1/all/v/%s/%s/p/%d" % (SIDRA, TABELA, VARIAVEIS, CLASSIF, ano)
    return baixar(url, cache="brasil-produtos-%d.json" % ano)


def coletar_municipios_por_produto(municipios, ano):
    """Municipio x produto: base do ranking municipal e do mapa."""
    bruto = {}
    for i, mun in enumerate(municipios, start=1):
        url = "%s/t/%d/n6/%s/v/%s/%s/p/%d" % (
            SIDRA, TABELA, mun["codigo"], VARIAVEIS, CLASSIF, ano
        )
        bruto[mun["codigo"]] = baixar(
            url, cache="mun-produtos-%d-%s.json" % (ano, mun["codigo"])
        )
        if i % 25 == 0:
            print("    %d/%d municipios (%d)" % (i, len(municipios), ano))
    return bruto


# ---------------------------------------------------------------- montagem
def linhas_para_lista(tabela):
    """A primeira linha da resposta SIDRA sempre e cabecalho: joga fora."""
    if not isinstance(tabela, list) or not tabela:
        return []
    return tabela[1:]


def montar(municipios, serie_estado, estado_produtos, brasil_produtos, mun_produtos, mapa, metadados):
    """Monta a base consolidada para o painel."""
    produtos = {}
    for ano, tabela in estado_produtos.items():
        for linha in linhas_para_lista(tabela):
            chave = linha["D3N"]
            if chave == "Total":
                # "Total" e a linha agregada do proprio IBGE: somar junto com os
                # produtos duplicaria tudo. Fica fora dos rankings; o total do
            # estado vem da variavel com D4N == "Total" (ou da soma, ver 214/112).
                continue
            produtos.setdefault(chave, {"produto": chave, "codigo": linha.get("D3C")})
            produtos[chave].setdefault(ano, {})[linha["D2C"]] = {
                "v": numero(linha["V"]),
                "bruto": linha["V"],
            }

    brasil = {}
    for linha in linhas_para_lista(brasil_produtos):
        if linha["D3N"] == "Total":
            continue
        brasil.setdefault(linha["D3N"], {})[linha["D2C"]] = numero(linha["V"])

    # ---- serie do estado (totais publicados + agregados recalculados)
    # sem c782 as dimensicoes sao: D1=UF, D2=variavel, D3=ano, D4=produto(Total)   # SEM c782
    serie = {}
    for linha in linhas_para_lista(serie_estado):
        serie.setdefault(linha["D2C"], {})[linha["D3C"]] = numero(linha["V"])

    recalculado = {}
    for ano in ANOS_SERIE:
        soma_prod = {"214": 0.0, "216": 0.0, "8331": 0.0, "215": 0.0}
        n_prod = 0
        for chave, dados in produtos.items():
            ano_dados = dados.get(str(ano))
            if not ano_dados:
                continue
            n_prod += 1
            for cod, campo in (("214", "214"), ("216", "216"), ("8331", "8331"), ("215", "215")):
                val = ano_dados.get(cod, {}).get("v")
                if val is not None:
                    soma_prod[cod] += val
        recalculado[str(ano)] = {
            "produtos_com_dado": n_prod,
            "producao_t": soma_prod["214"],
            "area_colhida_ha": soma_prod["216"],
            "area_plantada_ha": soma_prod["8331"],
            "valor_mil_reais": soma_prod["215"],
        }
        if soma_prod["216"] > 0:
            recalculado[str(ano)]["rendimento_kg_ha"] = (
                soma_prod["214"] * 1000 / soma_prod["216"]
            )

    # ---- municipios
    linhas_mun = []
    for mun in municipios:
        cod = mun["codigo"]
        registro = {
            "codigo": cod,
            "nome": mun["nome"],
            "produtos": {},
        }
        for ano, tabelas in mun_produtos.items():
            tabela = tabelas.get(cod)
            if not tabela:
                continue
            agreg = {"214": 0.0, "8331": 0.0, "216": 0.0, "215": 0.0}
            zeros = 0            # "-" = produto nao ocorreu no municipio (zero real)
            indisponivel = 0     # ".."/"..." = o IBGE nao disseminated esse dado
            for linha in linhas_para_lista(tabela):
                produto = linha["D3N"]
                if produto == "Total":
                    continue
                valor = numero(linha["V"])
                if valor is None:
                    if str(linha["V"]).strip() == "-":
                        zeros += 1
                    else:
                        indisponivel += 1
                    continue
                # cada linha e (produto, variavel). Sem o setdefault aninhado a
                # linha seguinte do mesmo produto APAGARIA a anterior.
                registro["produtos"].setdefault(produto, {}).setdefault(
                    ano, {"214": None, "112": None, "8331": None, "216": None, "215": None}
                )
                registro["produtos"][produto][ano][linha["D2C"]] = valor
                if linha["D2C"] in agreg:
                    agreg[linha["D2C"]] += valor
            registro[ano] = {
                "producao_t": agreg["214"] if agreg["214"] else None,
                "area_plantada_ha": agreg["8331"] if agreg["8331"] else None,
                "area_colhida_ha": agreg["216"] if agreg["216"] else None,
                "valor_mil_reais": agreg["215"] if agreg["215"] else None,
                "rendimento_kg_ha": (
                    agreg["214"] * 1000 / agreg["216"] if agreg["216"] else None
                ),
                "n_produtos": sum(
                    1 for p, a in registro["produtos"].items()
                    if ano in a and a[ano].get("214") is not None
                ),
                "celulas_zero": zeros,
                "celulas_indisponivel": indisponivel,
            }
        linhas_mun.append(registro)

    # ---- mapa enxuto: so o contorno + codigo/nome, sem peso de arquivo
    nomes = {m["codigo"]: m["nome"] for m in municipios}
    mapa_leve = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "codigo": str(f["properties"].get("codarea", "")),
                    "nome": nomes.get(str(f["properties"].get("codarea", "")), ""),
                },
                "geometry": f["geometry"],
            }
            for f in mapa.get("features", [])
        ],
    }

    return {
        "fonte": {
            "tabela_sidra": TABELA,
            "pesquisa": "PAM - Pesquisa Agropecuaria Municipal",
            "orgao": "IBGE",
            "url_sidra": "https://apisidra.ibge.gov.br/values/t/5457",
            "url_meta": "https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados",
            "url_mapa": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/21",
            "ano_foco": ANO_FOCO,
            "publicado_em": metadados.get("publicado_em"),
            "gerado_em": time.strftime("%Y-%m-%d %H:%M"),
            "variaveis": VARS,
        },
        "uf": {"codigo": UF, "nome": "Maranhao", "n_municipios": len(municipios)},
        "serie_estado": {
            "publicado": serie,
            "recalculado": recalculado,
        },
        "produtos": produtos,
        "brasil": brasil,
        "municipios": linhas_mun,
        "mapa": mapa_leve,
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    print("1/6 metadados da tabela %d" % TABELA)
    baixar(
        "https://servicodados.ibge.gov.br/api/v3/agregados/5457/metadados",
        cache="metadados-5457.json",
    )
    periodos = baixar(
        "https://servicodados.ibge.gov.br/api/v3/agregados/%d/periodos" % TABELA,
        cache="periodos-5457.json",
    )
    metadados = {}
    for periodo in periodos:
        if str(periodo.get("id")) == str(ANO_FOCO):
            bruto_mod = str(periodo.get("modificacao", ""))
            try:
                dia, mes, ano = reversed(bruto_mod.split("/"))
                metadados["publicado_em"] = "%s/%s/%s" % (dia, mes, ano)
            except ValueError:
                metadados["publicado_em"] = bruto_mod
    print("    PAM %d publicado em %s" % (ANO_FOCO, metadados.get("publicado_em")))

    print("2/6 municipios do MA")
    municipios = coletar_municipios()
    print("    %d municipios" % len(municipios))

    print("3/6 malhas dos municipios")
    mapa = coletar_mapa()
    print("    %d feições" % len(mapa.get("features", [])))

    print("4/6 serie do estado")
    serie_estado = coletar_serie_estado()
    estado_produtos = coletar_estado_por_produto()

    print("5/6 Brasil x produto (referencia nacional)")
    brasil_produtos = coletar_brasil_por_produto(ANO_FOCO)

    mun_produtos = {}
    for ano in ANOS_MUN:
        print("6/6 municipios x produto / %d" % ano)
        mun_produtos[str(ano)] = coletar_municipios_por_produto(municipios, ano)

    print("montando a base consolidada")
    base = montar(
        municipios, serie_estado, estado_produtos,
        brasil_produtos, mun_produtos, mapa, metadados,
    )

    destino = os.path.join(SAIDA, "pam-ma-%d.json" % ANO_FOCO)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(base, fh, ensure_ascii=False, separators=(",", ":"))
    tamanho = os.path.getsize(destino) / 1024
    print("pronto -> %s (%.0f KB)" % (destino, tamanho))

    mapa_destino = os.path.join(SAIDA, "ma-municipios.geojson")
    with open(mapa_destino, "w", encoding="utf-8") as fh:
        json.dump(base["mapa"], fh, ensure_ascii=False, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    sys.exit(main())