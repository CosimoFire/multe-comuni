/* Radar – QN · esportazione in SVG statico (solo con ?svg=1 nell'URL).
   Ricostruisce la pagina come un unico SVG: testi HTML (titolo, sottotitolo, numeri, note, piede)
   riga per riga nella posizione in cui il browser li ha impaginati, logo, grafici SVG con gli stili
   calcolati scritti come attributi (nessuna variabile CSS, così si apre anche in Illustrator).
   Il risultato va in <textarea id="svg-out"> e in un link "Scarica SVG". */
(function () {
  "use strict";
  if (!/[?&]svg=1\b/.test(location.search)) return;
  var NS = "http://www.w3.org/2000/svg";
  var TESTI = ".r-title, .r-sub, .r-name, .r-big__num, .r-big__unit, .r-big__label, .r-chart__head, .r-chart__sub, .r-key span, .r-read summary, .r-warn, .r-foot span, .r-place";
  var PROPS = ["fill", "fill-opacity", "stroke", "stroke-width", "stroke-dasharray", "stroke-linejoin", "stroke-opacity", "opacity",
    "font-family", "font-size", "font-weight", "font-style", "letter-spacing", "paint-order"];

  function el(name, attrs) { var e = document.createElementNS(NS, name); for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }
  function vis(e) { var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== "hidden"; }

  function testoInRighe(node, ox, oy, out) {
    var w = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null);
    var t;
    while ((t = w.nextNode())) {
      var par = t.parentElement, cs = getComputedStyle(par);
      if (cs.display === "none" || !vis(par)) continue;
      var txt = t.textContent, re = /\S+/g, m, righe = [];
      while ((m = re.exec(txt))) {
        var rg = document.createRange(); rg.setStart(t, m.index); rg.setEnd(t, m.index + m[0].length);
        var r = rg.getClientRects()[0]; if (!r) continue;
        var ultima = righe[righe.length - 1];
        if (ultima && Math.abs(ultima.top - r.top) < r.height * 0.5) { ultima.parole.push(m[0]); ultima.right = r.right; }
        else righe.push({ top: r.top, h: r.height, left: r.left, right: r.right, parole: [m[0]] });
      }
      righe.forEach(function (rr) {
        var fs = parseFloat(cs.fontSize);
        var tx = el("text", {
          x: (rr.left - ox).toFixed(1), y: (rr.top - oy + rr.h / 2 + fs * 0.35).toFixed(1),
          "font-family": cs.fontFamily, "font-size": cs.fontSize, "font-weight": cs.fontWeight, "font-style": cs.fontStyle,
          fill: cs.color, "letter-spacing": cs.letterSpacing === "normal" ? 0 : cs.letterSpacing
        });
        tx.textContent = rr.parole.join(" ");
        out.appendChild(tx);
      });
    }
  }

  function copiaStili(orig, clone) {
    var cs = getComputedStyle(orig);
    PROPS.forEach(function (p) {
      var v = cs.getPropertyValue(p);
      if (v && v !== "normal" && v !== "none" || p === "fill" || p === "stroke") clone.setAttribute(p, v);
    });
    clone.removeAttribute("class"); clone.removeAttribute("style");
    var o = orig.children, c = clone.children;
    for (var i = 0; i < o.length; i++) if (c[i]) copiaStili(o[i], c[i]);
  }

  function esporta() {
    var root = document.querySelector(".radar"), R = root.getBoundingClientRect();
    var W = Math.ceil(R.width), H = Math.ceil(R.height);
    var svg = el("svg", { xmlns: NS, width: W, height: H, viewBox: "0 0 " + W + " " + H });
    svg.appendChild(el("rect", { width: W, height: H, fill: getComputedStyle(document.body).backgroundColor }));
    var ox = R.left, oy = R.top;
    // linee sottili sopra "Come leggere i dati" e sopra il piede
    document.querySelectorAll(".r-read, .r-foot").forEach(function (e) {
      if (!vis(e)) return;
      var r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      if (parseFloat(cs.borderTopWidth) > 0) svg.appendChild(el("line", { x1: r.left - ox, x2: r.right - ox, y1: r.top - oy + 0.5, y2: r.top - oy + 0.5, stroke: cs.borderTopColor, "stroke-width": 1 }));
    });
    // quadratini delle chiavi
    document.querySelectorAll(".r-key .sw").forEach(function (e) {
      if (!vis(e)) return;
      var r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      svg.appendChild(el("rect", { x: r.left - ox, y: r.top - oy, width: r.width, height: r.height, rx: 2, fill: cs.backgroundColor }));
    });
    // grafici
    document.querySelectorAll(".radar svg").forEach(function (s) {
      if (s.classList.contains("r-logo") || !vis(s)) return;
      var r = s.getBoundingClientRect(), c = s.cloneNode(true);
      copiaStili(s, c);
      c.querySelectorAll("title").forEach(function (t) { t.remove(); });
      c.setAttribute("x", (r.left - ox).toFixed(1)); c.setAttribute("y", (r.top - oy).toFixed(1));
      c.setAttribute("overflow", "visible");
      c.removeAttribute("role"); c.removeAttribute("aria-label");
      // le aree trasparenti per il passaggio del mouse non servono
      c.querySelectorAll("[fill='rgba(0, 0, 0, 0)'], [fill='transparent']").forEach(function (n) { if (n.tagName === "rect") n.remove(); });
      svg.appendChild(c);
    });
    // logo QN
    var logo = document.querySelector(".r-logo");
    if (logo && vis(logo)) {
      var lr = logo.getBoundingClientRect(), lc = logo.cloneNode(true);
      lc.setAttribute("x", lr.left - ox); lc.setAttribute("y", lr.top - oy); lc.setAttribute("width", lr.width); lc.setAttribute("height", lr.height);
      lc.removeAttribute("class"); lc.removeAttribute("role");
      lc.querySelectorAll("path").forEach(function (p) { p.setAttribute("fill", getComputedStyle(logo).color); });
      lc.querySelectorAll("title").forEach(function (t) { t.remove(); });
      svg.appendChild(lc);
    }
    // testi HTML
    var g = el("g", {});
    document.querySelectorAll(TESTI).forEach(function (e) { if (vis(e)) testoInRighe(e, ox, oy, g); });
    svg.appendChild(g);

    var str = '<?xml version="1.0" encoding="UTF-8"?>\n' + new XMLSerializer().serializeToString(svg);
    var ta = document.createElement("textarea"); ta.id = "svg-out"; ta.style.display = "none"; ta.value = str; ta.textContent = str;
    document.body.appendChild(ta);
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([str], { type: "image/svg+xml" }));
    a.download = (location.pathname.split("/").filter(Boolean).pop() || "dataviz") + ".svg";
    a.textContent = "Scarica SVG"; a.id = "svg-link";
    a.style.cssText = "position:fixed;right:8px;bottom:8px;font:600 13px sans-serif;background:#1f4fd1;color:#fff;padding:6px 10px;border-radius:2px;z-index:9";
    document.body.appendChild(a);
    document.documentElement.setAttribute("data-svg-pronto", "1");
  }
  function quandoPronto() {
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () { setTimeout(esporta, 1800); });
  }
  if (document.readyState === "complete") quandoPronto(); else window.addEventListener("load", quandoPronto);
})();
