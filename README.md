# Multe stradali nei comuni – dataviz Radar QN

| Dataviz | URL | Dati |
|---|---|---|
| Multe stradali, quanto incassa il tuo comune: menu regione/provincia/comune, euro per abitante 2024, 2025 e proiezione 2026 contro la media provinciale, tabella gennaio-agosto 2025 e 2026, distribuzione dei comuni della provincia | https://cosimofire.github.io/multe-comuni/incassi-comune/ | `data/comuni.csv` |
| Multe, quanto vincolano i capoluoghi alla sicurezza stradale: menu capoluogo/anno, quota vincolata della voce A e destinazione degli autovelox | https://cosimofire.github.io/multe-comuni/spesa-capoluoghi/ | `data/capoluoghi.csv` (in `data/` restano anche temi e interventi, non usati dalla pagina) |
| Treemap "Quasi quattro euro su dieci dei fondi vincolati vanno alle «altre finalità»": interventi 2025 dei capoluoghi divisi per voce di legge (art. 208 lettere a, b, c; autovelox strade e controlli) e, dentro ogni voce, per tipo di spesa | https://cosimofire.github.io/multe-comuni/spesa-temi/ | `data/capoluoghi-interventi.csv` |

**Fonti**
- SIOPE, download massivo aggiornato al 19 novembre 2026: voce 3.02.02.01.004 (multe e sanzioni per violazioni del Codice della strada a carico delle famiglie), incassi di cassa; spesa = pagamenti dei titoli 1-4. Da settembre 2026 molti incassi sono ancora "da regolarizzare", per questo il 2026 si ferma ad agosto.
- Relazioni art. 142, comma 12-quater, del Codice della strada inviate dai comuni al ministero dell'Interno (finanzalocale.interno.gov.it), proventi 2024 e 2025. Estratte con due motori PDF e controllate nelle somme.
- Istat, residenti al 1° gennaio 2026 (stima, API SDMX).

**Calcoli fatti nel browser:** media provinciale (incassi dei comuni della provincia / residenti), posizione in provincia, media dei capoluoghi per tema. **Calcoli nei CSV:** proiezione 2026 = incassi gennaio-agosto 2026 / quota di gennaio-agosto sull'anno nel 2024-2025 (del comune se ha almeno 20.000 € di incassi e una quota tra 45% e 90%, altrimenti della provincia). Il tema di ogni intervento è assegnato per parole chiave della descrizione.

**File:** `radar.css`, `radar.js`, `embed*.js` e `logo/` vengono dalla skill radar-dataviz. `scripts/prepara_csv.py` ricostruisce i CSV dai dati di lavoro. Librerie: d3 v7 da jsDelivr.

## Sfondo e logo

Come nelle altre dataviz Radar: la pagina riconosce i quattro sfondi QN. Anteprime: `?bg=grigio`, `?bg=bianco`, `?bg=nero`, `?bg=notte`.

## Snippet per il CMS

Sono nella pagina indice (https://cosimofire.github.io/multe-comuni/), con il pulsante Copia.
