"""CSV delle due dataviz Radar, ricavati dai dati gia' verificati in multe_siope/dashboard.
- data/comuni.csv: incassi SIOPE (multe CdS a carico delle famiglie) per comune, residenti ISTAT 1/1/2026,
  spesa complessiva (pagamenti titoli 1-4), proiezione 2026 su gennaio-agosto.
- data/capoluoghi.csv, capoluoghi-temi.csv, capoluoghi-interventi.csv: relazioni art. 142 c. 12-quater
  al Ministero dell'Interno, proventi 2024 e 2025.
Separatore ; e virgola decimale (stile Radar). Uso: python -I prepara_csv.py <cartella multe_siope> <cartella repo>
"""
import csv
import json
import os
import sys

src, repo = sys.argv[1], sys.argv[2]
D = json.load(open(os.path.join(src, "dashboard", "dati.json"), encoding="utf-8"))
K = json.load(open(os.path.join(src, "dashboard", "dati_capoluoghi.json"), encoding="utf-8"))
out = os.path.join(repo, "data")


def scrivi(nome, head, rows):
    with open(os.path.join(out, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(head)
        for r in rows:
            w.writerow([(f"{v}".replace(".", ",") if isinstance(v, float) else v) for v in r])
    print(nome, len(rows))


prov = D["province"]
scrivi("comuni.csv",
       ["Regione", "Provincia", "Comune", "Residenti", "Incassi 2024", "Incassi 2025",
        "Incassi gen-ago 2025", "Incassi gen-ago 2026", "Proiezione 2026", "Proiezione su dati del comune",
        "Altre multe 2025", "Spesa 2024", "Spesa 2025"],
       [[D["regioni"][prov[c[1]][0]], prov[c[1]][1], c[0], c[2], c[3], c[4], c[8], c[5], c[6],
         "sì" if c[7] else "no", c[9], c[10], c[11]] for c in D["comuni"]])

TEMI = K["temi"]
cap, temi, its = [], [], []
for c in K["capoluoghi"]:
    for anno, a in sorted(c["anni"].items()):
        if a.get("vuota"):
            cap.append([anno, c["n"], K["regioni"][c["r"]], c["pop"], a["nota"], "", "", "", "", "", "", "", ""])
            continue
        cap.append([anno, c["n"], K["regioni"][c["r"]], c["pop"], a["nota"], a["T"], a["A"], a["V"],
                    a["q2"][0], a["q2"][1], a["q2"][2], a["q3"][0], a["q3"][1]])
        for k, t in enumerate(TEMI):
            temi.append([anno, c["n"], t, a["temi"][k][0], a["temi"][k][1]])
        for voce, descr, costo, perc, ti in a["it"]:
            its.append([anno, c["n"], voce, " ".join((descr or "").split()), TEMI[ti], costo, perc])

scrivi("capoluoghi.csv",
       ["Anno", "Capoluogo", "Regione", "Residenti", "Nota", "Proventi totali", "Proventi voce A", "Proventi autovelox",
        "Vincolato segnaletica", "Vincolato controlli", "Vincolato altre finalita", "Autovelox strade e sicurezza",
        "Autovelox controlli e personale"], cap)
scrivi("capoluoghi-temi.csv", ["Anno", "Capoluogo", "Tema", "Programmato", "Realizzato"], temi)
scrivi("capoluoghi-interventi.csv", ["Anno", "Capoluogo", "Voce", "Descrizione", "Tema", "Costo", "Realizzazione %"], its)
