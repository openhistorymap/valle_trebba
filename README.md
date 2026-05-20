# Valle Trebba

Dati e configurazione del rilievo della necropoli etrusca di **Valle Trebba**, presso Spina (Comacchio, Ferrara). Il repository contiene la cartografia archeologica, le schede di scavo per tomba e i metadati associati, in un formato leggibile sia in QGIS sia dal frontend di Open History Map.

Non è un'applicazione: è un *dataset pubblicato*. Tutto il contenuto è statico e viene servito direttamente da GitHub via [jsDelivr](https://www.jsdelivr.com/), letto a runtime da [`geocontext-front`](https://www.openhistorymap.org/geocontext-front/) — l'engine che ne ricostruisce la mappa interattiva.

**Mappa interattiva:** <https://www.openhistorymap.org/geocontext-front/openhistorymap/valle_trebba/map>

---

## Contesto

Valle Trebba è una delle due grandi necropoli (insieme a Valle Pega) della città etrusca di **Spina**, scalo commerciale dell'alto Adriatico tra VI e III secolo a.C., nei pressi della laguna comacchiese. Le tombe registrate in questo dataset coprono l'arco numerico **151–1213** e includono sia sepolture a inumazione sia a cremazione, in fosse, pozzetti e casse, distribuite su un'area di dossi e palificazioni lignee oggi sotto la quota di campagna.

I dati provengono da scavi storici (Proni, anni Venti) e da studi successivi, riorganizzati e georeferenziati per la pubblicazione.

---

## Contenuto del repository

### Cartografia (`datasets/`)

GeoJSON in CRS84 (WGS84, longitudine/latitudine). Tutti i file vengono caricati dalla configurazione `gcx.json`.

| File | Geometria | Descrizione |
|---|---|---|
| `valle_trebba_punti_32632.geojson` | punti | Le tombe — 1226 *features*, ciascuna con un'identificativo `tomba` e attributi archeologici (rito, fase, struttura, sesso, classe d'età, posizione del corredo, ecc.). |
| `valle_trebba_ustrina.geojson` | punti | Aree di cremazione (*ustrina*). |
| `valle_trebba_palificazioni.geojson` | punti | Sistema di palificazioni lignee. |
| `valle_trebba_linee.geojson` | linee | Allineamenti, profili di scavo, sezioni. |
| `valle_trebba_dossi_poligoni.geojson` | poligoni | Dossi sabbiosi su cui si distribuiscono le tombe. |

*Nota:* il suffisso `_32632` nel nome di `valle_trebba_punti_32632.geojson` è storico — il file è in CRS84, non in UTM 32N. Si veda il blocco `crs` interno.

### Schede di scavo (`tombe/`)

Per ogni tomba censita esiste almeno una scheda in formato Word:

- `VT_Tomba_<n>.docx` — 1223 schede, set autoritativo per l'arco 0–1213.
- `Tomba_<n>.docx` / `Tomba_<n>.html` / `Tomba_<n>.md` — sottoinsieme di 35 schede (151–185) convertite anche in HTML e Markdown per la visualizzazione *inline* nella sidebar della mappa.

### Schizzi (`schizzi/`)

100 disegni in formato JPEG, denominati `<tomba>.jpg`, con i rilievi grafici originali delle tombe per le quali sono disponibili.

### Tabelle di riferimento (file CSV / XLSX a livello radice)

Tabelle tabulari complementari, agganciate alle features via id tomba:

- `Tombe_VT_151-1213.csv` (+`.xlsx`) — metadati strutturati (anno di rinvenimento, stato di conservazione, rito, struttura, profondità, dimensioni, posizione del corredo, genere, sesso, classi d'età). 31 righe.
- `Bibliografia_tombe_171-1213.csv` (+`.xlsx`) — bibliografia essenziale per tomba. 1051 righe.
- `Giornali di scavo_151-1213.docx` + `giornali_di_scavo_151-1213.md` — registro sequenziale degli scavi, in versione documento Word e in Markdown.

### Configurazione

- `gcx.json` — configurazione della mappa (livelli, sorgenti, stili, blocco *detail* per ogni tomba). Vedi [FORMAT.md](https://github.com/openhistorymap/geocontext-front/blob/rewrite/angular-latest/FORMAT.md) per lo schema completo.
- `chcx-static.json` — registro delle pagine statiche associate al progetto (al momento: i *Giornali di scavo*).
- `datapackage.json` — descrittore [Frictionless Data Package](https://datapackage.org) (v2): metadati, fonti e l'elenco delle risorse dati (i GeoJSON e i CSV, con Table Schema). Rende il repository interoperabile con gli strumenti dell'ecosistema Frictionless; validabile con `frictionless validate datapackage.json`.

### File di servizio

- `CLAUDE.md` — note operative per agenti AI che modificano il repository.
- `layers/` — coppia GeoJSON/QML non collegata alla mappa principale, materiale di staging da un altro progetto.

---

## Come si naviga il dataset

Aprendo la [mappa interattiva](https://www.openhistorymap.org/geocontext-front/openhistorymap/valle_trebba/map), per ogni tomba cliccata il pannello laterale mostra automaticamente, quando disponibili:

1. lo **schizzo** della tomba (`schizzi/<id>.jpg`);
2. la **scheda di scavo** in HTML, *inline* nel pannello (per il sottoinsieme 151–185);
3. i **metadati tabulari** (riga corrispondente in `Tombe_VT_151-1213.csv`);
4. la **bibliografia essenziale** (riga corrispondente in `Bibliografia_tombe_171-1213.csv`);
5. il **download** della scheda in formato `.docx`.

Le voci la cui copertura è parziale (35 schede HTML, 100 schizzi, ecc.) vengono *silenziosamente nascoste* per le tombe non coperte — non viene mostrato un placeholder.

La mappa colora le tombe per **rito di seppellimento**:

- blu — inumazione (688 tombe);
- arancio — cremazione (492 tombe);
- grigio — non determinabile / dato mancante (46 tombe).

Il raggio del simbolo si adatta al livello di zoom (2 px a z12 → 7 px a z20).

Dalla barra superiore si raggiunge anche la pagina statica *Giornali di scavo*, che riporta il diario sequenziale dello scavo.

---

## Lavorare sul repository

Tutti i file sono statici. Non c'è codice, build o test. Le modifiche utili sono:

1. **Aggiornare un GeoJSON** — sostituire il file in `datasets/`. Validare con `python -c "import json; json.load(open('datasets/X.geojson'))"`.
2. **Aggiornare il `gcx.json`** — qualsiasi `datasources[].conf.source` deve corrispondere a un file effettivamente presente; ogni `layers[].datasource` deve riferirsi a un `datasources[].name` esistente.
3. **Aggiungere una scheda** — depositare `VT_Tomba_<n>.docx` in `tombe/`. Se serve la versione *inline*, generare anche `Tomba_<n>.html` (pandoc, formato frammento) e/o `Tomba_<n>.md` (`pandoc -t gfm`).
4. **Forzare il refresh della CDN** — dopo un push, invalidare jsDelivr con `curl https://purge.jsdelivr.net/gh/openhistorymap/valle_trebba@HEAD/<path>`.

Il file `CLAUDE.md` riassume le convenzioni del repository.

---

## Fonti e crediti

I riferimenti bibliografici minimi citati nelle schede sono raccolti in `Bibliografia_tombe_171-1213.csv`. Tra gli autori più ricorrenti:

- **N. Proni** — *Giornali di scavo*, 1923 e seguenti (testimonianza primaria della campagna originale).
- **F. Berti** — *Spina. Storia di una città tra Greci ed Etruschi*, 1983.
- **A. Trevisanello** — tesi di dottorato, 2024 (revisione moderna e raccordo dei dati).

I dati geografici (`datasets/`) e i materiali archeologici (`tombe/`, `schizzi/`) sono pubblicati a fini di studio e divulgazione, nell'ambito del progetto **Open History Map**.

---

## Contatti

Repository: <https://github.com/openhistorymap/valle_trebba>
Open History Map: <https://www.openhistorymap.org>
