import json, sys, gzip, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def get(u):
    req = urllib.request.Request(u, headers={"Accept-Encoding": "gzip", "User-Agent": "moeda/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        bruto = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            bruto = gzip.decompress(bruto)
        return json.loads(bruto.decode("utf-8"))

mun = get("https://servicodados.ibge.gov.br/api/v1/localidades/municipios")
ma = sorted([m for m in mun if str(m["id"]).startswith("21")], key=lambda m: m["nome"])
print("municipios do MA:", len(ma), "| exemplo:", ma[0]["nome"], ma[0]["id"])
amostra = ",".join(str(ma[i]["id"]) for i in (0, 1))
r = get("https://apisidra.ibge.gov.br/values/t/1612/n6/%s/v/214/p/2025/c81/2702" % amostra)
print("\namostra de registros:")
for x in r:
    print("  ", json.dumps(x, ensure_ascii=False))
