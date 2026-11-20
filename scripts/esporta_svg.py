"""Esporta in SVG tutte le dataviz della repo. Apre ogni pagina con Edge headless (?svg=1, animazioni
spente, larghezza desktop 760px), legge l'SVG costruito da assets/export-svg.js e lo salva in svg/.
Serve un server locale sulla cartella Desktop\\Claude (porta 8765).
Uso: python -I esporta_svg.py <cartella repo>"""
import html
import os
import re
import subprocess
import sys

repo = sys.argv[1]
EDGE = next(p for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p))
PAGINE = ["top-comuni", "top-capoluoghi", "spesa-temi", "incassi-comune", "spesa-capoluoghi"]
os.makedirs(os.path.join(repo, "svg"), exist_ok=True)
for p in PAGINE:
    url = f"http://127.0.0.1:8765/multe-comuni/{p}/?svg=1&bg=bianco"
    out = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--force-prefers-reduced-motion", "--hide-scrollbars",
                          "--virtual-time-budget=15000", "--window-size=792,2400", "--dump-dom", url],
                         capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
    m = re.search(r'<textarea id="svg-out"[^>]*>(.*?)</textarea>', out, re.S)
    if not m:
        print(p, "ERRORE: SVG non trovato")
        continue
    svg = html.unescape(m.group(1))
    fn = os.path.join(repo, "svg", p + ".svg")
    open(fn, "w", encoding="utf-8").write(svg)
    w = re.search(r'width="(\d+)" height="(\d+)"', svg)
    print(p, "ok", w.group(0) if w else "", len(svg) // 1024, "KB", "var(" in svg and "ATTENZIONE: variabili CSS rimaste" or "")
