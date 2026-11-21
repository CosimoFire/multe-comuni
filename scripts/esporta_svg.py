"""Esporta in SVG tutte le dataviz della repo. Apre ogni pagina con Edge headless (?svg=1, animazioni
spente, larghezza desktop 760px), legge l'SVG costruito da assets/export-svg.js e lo salva in svg/.
Serve un server locale sulla cartella Desktop\\Claude (porta 8765).
Uso: python -I esporta_svg.py <cartella repo>"""
import html
import os
import re
import subprocess
import tempfile
import sys

repo = sys.argv[1]
EDGE = next(p for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p))
PAGINE = ["top-comuni", "top-capoluoghi", "spesa-temi", "incassi-comune", "spesa-capoluoghi"]
os.makedirs(os.path.join(repo, "svg"), exist_ok=True)
# profilo separato: se Edge e' gia' aperto, headless non si aggancia alla finestra esistente
PROFILO = tempfile.mkdtemp(prefix="edge-svg-")
# copia anche nella cartella Download dell'utente
DL = os.path.join(os.path.expanduser("~"), "Downloads", "multe-comuni-svg")
os.makedirs(DL, exist_ok=True)
for p in PAGINE:
    url = f"http://127.0.0.1:8765/multe-comuni/{p}/?svg=1&bg=bianco" + ("&c=Milano" if p in ("incassi-comune", "spesa-capoluoghi") else "")
    # con Edge 158 --dump-dom lanciato da Python non restituisce nulla: lo lancia PowerShell (Start-Process),
    # che scrive l'output su file
    dump = os.path.join(PROFILO, "dump.html")
    args = ["--headless=new", "--user-data-dir=" + PROFILO, "--disable-gpu", "--force-prefers-reduced-motion", "--hide-scrollbars",
            "--virtual-time-budget=15000", "--window-size=792,2400", "--dump-dom", url]
    ps = ("Start-Process -FilePath '" + EDGE + "' -ArgumentList " + ",".join("'" + a + "'" for a in args) +
          " -Wait -WindowStyle Hidden -RedirectStandardOutput '" + dump + "' -RedirectStandardError '" + dump + ".err'")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], timeout=150)
    out = open(dump, "rb").read().decode("utf-8", "replace") if os.path.exists(dump) else ""
    m = re.search(r'<textarea id="svg-out"[^>]*>(.*?)</textarea>', out, re.S)
    if not m:
        print(p, "ERRORE: SVG non trovato")
        continue
    svg = html.unescape(m.group(1))
    fn = os.path.join(repo, "svg", p + ".svg")
    open(fn, "w", encoding="utf-8").write(svg)
    open(os.path.join(DL, p + ".svg"), "w", encoding="utf-8").write(svg)
    w = re.search(r'width="(\d+)" height="(\d+)"', svg)
    print(p, "ok", w.group(0) if w else "", len(svg) // 1024, "KB", "var(" in svg and "ATTENZIONE: variabili CSS rimaste" or "")
