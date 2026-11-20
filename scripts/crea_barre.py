"""Crea le due pagine a barre (primi 10 comuni e primi 10 capoluoghi per incassi da multe per abitante,
gennaio-agosto 2026) dallo stesso modello. Uso: python -I crea_barre.py <cartella repo>"""
import os
import sys

repo = sys.argv[1]
MODELLO = r"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITOLO_PAGINA__ – Radar QN</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,700&display=swap">
<link rel="stylesheet" href="../assets/radar.css">
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="../assets/radar.js"></script>
<style>
  .r-read { margin: 28px 0 0; border-top: 1px solid var(--rule); padding-top: 10px; }
  .r-read summary { font: 600 13px var(--sans); color: var(--ink); cursor: pointer; list-style: none; display: flex; align-items: center; gap: 6px; }
  .r-read summary::-webkit-details-marker { display: none; }
  .r-read summary::before { content: "+"; display: inline-block; width: 14px; font-weight: 700; color: var(--blue); }
  .r-read[open] summary::before { content: "\2212"; }
  .r-read .r-note:first-of-type { margin-top: 8px; }
  .r-read + .r-foot { margin-top: 16px; }
  .row-sub { font-size: 11px; fill: var(--ink-2); }
</style>
</head>
<body>
<main class="radar">
  <header>
    <h1 class="r-title" id="title">__TITOLO__</h1>
    <p class="r-sub">__SOTTOTITOLO__</p>
  </header>

  <figure class="r-chart" id="barre"></figure>

  <details class="r-read">
    <summary>Come leggere i dati</summary>
    <p class="r-note">Incassi di cassa registrati in SIOPE tra gennaio e agosto 2026 per le multe del Codice della strada pagate dalle famiglie, divisi per i residenti Istat al 1° gennaio 2026. Comprendono multe di anni precedenti. Da settembre molti incassi non sono ancora attribuiti alla voce delle multe, per questo il periodo si ferma ad agosto. Nei comuni turistici o attraversati da strade di grande traffico le multe le pagano soprattutto i non residenti: l'euro per abitante misura il peso sul bilancio del comune, non sui cittadini.__NOTA__</p>
  </details>

  <footer class="r-foot">
    <span>Fonte: SIOPE (Ragioneria generale dello Stato e Banca d'Italia), dati al 19 novembre 2026; Istat, residenti al 1° gennaio 2026</span>
    <span>Elaborazione Radar – QN</span>
  </footer>
</main>

<script>
(function () {
  var R = Radar, fmt = R.fmt;
  var SOLO_CAP = __SOLO_CAP__;
  var eur = function (v) { return fmt(v, v >= 100 ? 0 : 1) + " €"; };
  R.loadCSV("../data/comuni.csv").then(function (rows) {
    var all = rows.map(function (r) {
      var pop = R.num(r["Residenti"]) || 0;
      return { nome: r["Comune"], prov: r["Provincia"], pop: pop, cap: r["Capoluogo"] === "sì",
        a26: R.num(r["Incassi gen-ago 2026"]) || 0, a25: R.num(r["Incassi gen-ago 2025"]) || 0 };
    }).filter(function (d) { return d.pop > 0; });
    var media = d3.sum(all, function (d) { return d.a26; }) / d3.sum(all, function (d) { return d.pop; });
    var base = SOLO_CAP ? all.filter(function (d) { return d.cap; }) : all;
    base.forEach(function (d) { d.v = d.a26 / d.pop; d.v25 = d.a25 / d.pop; });
    var top = base.slice().sort(function (a, b) { return b.v - a.v; }).slice(0, 10);
    var first = top[0];

    // titolo dai dati
    var t = SOLO_CAP
      ? first.nome + " prima tra i capoluoghi: " + fmt(first.v, 0) + " euro di multe per abitante in otto mesi"
      : (first.v >= 1000 ? "A " + first.nome + " oltre mille euro di multe per abitante in otto mesi"
                         : first.nome + " prima per multe per abitante: " + fmt(first.v, 0) + " euro in otto mesi");
    d3.select("#title").text(t);

    var host = document.getElementById("barre"), tip = R.tooltip(host), clear = function () {};
    R.dismissOutside(host, function () { tip.hide(); clear(); });

    R.responsive(host, function (W, phase) {
      var narrow = R.isNarrow(W);
      var labW = narrow ? 0 : 190, row = narrow ? 44 : 36, bh = narrow ? 16 : 20;
      var m = { top: 26, right: narrow ? 52 : 70, bottom: 6, left: labW };
      var H = m.top + row * top.length + m.bottom, w = W - m.left - m.right;
      var x = d3.scaleLinear().domain([0, first.v]).range([0, w]);
      d3.select(host).select("svg").remove();
      var svg = d3.select(host).insert("svg", ".r-tip").attr("width", W).attr("height", H).attr("role", "img")
        .attr("aria-label", "Grafico a barre: " + top.map(function (d, i) { return (i + 1) + ". " + d.nome + " " + eur(d.v); }).join("; ") +
          ". Media italiana " + eur(media) + " per abitante.");
      svg.append("title").text(t);
      var g = svg.append("g").attr("transform", "translate(" + m.left + "," + m.top + ")");
      var yy = function (i) { return narrow ? i * row + 18 : i * row + (row - bh) / 2; };

      g.append("g").selectAll("text").data(top).join("text").attr("class", "tick-label")
        .attr("x", narrow ? 0 : -10).attr("text-anchor", narrow ? "start" : "end").attr("y", function (d, i) { return narrow ? i * row + 12 : yy(i) + bh / 2; }).attr("dy", narrow ? 0 : "0.35em")
        .style("fill", function (d, i) { return i === 0 ? "var(--ink)" : "var(--ink)"; }).style("font-weight", function (d, i) { return i === 0 ? 600 : 500; })
        .each(function (d) {
          var el = d3.select(this);
          el.text(d.nome);
          if (!SOLO_CAP) el.append("tspan").attr("class", "row-sub").text(" (" + d.prov + ")");
        });
      if (!narrow) g.append("line").attr("class", "baseline").attr("x1", 0.5).attr("x2", 0.5).attr("y1", 0).attr("y2", row * top.length);

      var bars = g.append("g").selectAll("path").data(top).join("path").attr("class", "mark")
        .style("fill", function (d, i) { return i === 0 ? "var(--red)" : "var(--blue)"; });
      R.enter(bars, phase,
        function (s) { s.attr("d", function (d, i) { return R.barPathH(1, yy(i), 0, bh, 2); }); },
        function (s) {
          var p = function (d, k) { var i = top.indexOf(d); return R.barPathH(1, yy(i), x(d.v) * k, bh, 2); };
          if (typeof s.attrTween === "function") s.attrTween("d", function (d) { return function (k) { return p(d, k); }; });
          else s.attr("d", function (d) { return p(d, 1); });
        });
      var vals = g.append("g").selectAll("text").data(top).join("text").attr("class", "val-label mark")
        .attr("x", function (d) { return x(d.v) + 7; }).attr("y", function (d, i) { return yy(i) + bh / 2; }).attr("dy", "0.35em");
      vals.each(function (d) { R.countUp(d3.select(this), d.v, eur, phase); });

      // riferimento: media italiana
      var an = g.append("g").attr("class", "anno"), xm = x(media) + 1;
      an.append("line").attr("class", "dash").attr("x1", xm).attr("x2", xm).attr("y1", -8).attr("y2", row * top.length);
      an.append("text").attr("x", xm + 4).attr("y", -12).style("fill", "var(--ink-2)").text("Media italiana " + eur(media));
      R.enter(an, phase, function (s) { s.style("opacity", 0); }, function (s) { s.style("opacity", 1); }, R.DUR * 0.6);

      clear = function () { bars.classed("is-dimmed", false); vals.classed("is-dimmed", false); };
      g.append("g").selectAll("rect").data(top).join("rect").attr("class", "hit")
        .attr("x", -m.left).attr("width", W).attr("y", function (d, i) { return i * row; }).attr("height", row)
        .on("pointerenter pointerdown", function (ev, d) {
          bars.classed("is-dimmed", function (q) { return q !== d; }); vals.classed("is-dimmed", function (q) { return q !== d; });
          tip.show(R.tipHTML({ title: d.nome + (SOLO_CAP ? "" : " (" + d.prov + ")"), value: eur(d.v), unit: "per abitante",
            rows: [["Incassi gen-ago 2026", fmt(Math.round(d.a26), 0) + " €"], ["Residenti", fmt(d.pop, 0)], ["Gen-ago 2025", eur(d.v25) + " per abitante"]] }),
            Math.min(m.left + x(d.v), W - 30), yy(top.indexOf(d)) + m.top);
        })
        .on("pointerleave", function (ev) { if (ev.pointerType === "mouse") { tip.hide(); clear(); } });
    });
  }).catch(function (e) { R.fail("#barre", e); });
})();
</script>
<script src="../assets/export-svg.js"></script>
</body>
</html>
"""

PAGINE = {
    "top-comuni": dict(TITOLO_PAGINA="I comuni con più multe per abitante", TITOLO="I comuni con più multe per abitante",
                       SOTTOTITOLO="Incassi delle multe stradali pagate dalle famiglie, in euro per abitante, gennaio-agosto 2026. I dieci comuni italiani con il valore più alto",
                       SOLO_CAP="false", NOTA=""),
    "top-capoluoghi": dict(TITOLO_PAGINA="I capoluoghi con più multe per abitante", TITOLO="I capoluoghi con più multe per abitante",
                           SOTTOTITOLO="Incassi delle multe stradali pagate dalle famiglie, in euro per abitante, gennaio-agosto 2026. I dieci capoluoghi di provincia con il valore più alto",
                           SOLO_CAP="true", NOTA=""),
}
for slug, cfg in PAGINE.items():
    html = MODELLO
    for k, v in cfg.items():
        html = html.replace("__" + k + "__", v)
    os.makedirs(os.path.join(repo, slug), exist_ok=True)
    open(os.path.join(repo, slug, "index.html"), "w", encoding="utf-8").write(html)
    print(slug, "ok")
