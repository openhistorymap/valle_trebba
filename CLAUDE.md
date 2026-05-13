# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`valle_trebba` is a **data + configuration repository**, not a service. It contains one geocontext descriptor (`gcx.json`) and the GeoJSON datasets it points at. There is no code, no build system, and no tests — changes are evaluated by whether `gcx.json` stays valid against the gcx schema and whether the referenced GeoJSON files load.

The subject matter is the Etruscan necropolis of **Valle Trebba** (Spina, near Comacchio/Ferrara, Italy). The dataset attributes are archaeological — tomb metadata in Italian (`t_rito`, `t_fase`, `t_struttur`, `t_orienta`, etc., with `tomba` as the grave ID).

Remote: `github.com/openhistorymap/valle_trebba`.

## How it is consumed

This repo is a backing store for the OHM **geocontext** subsystem. See `/srv/ohm/CLAUDE.md` for the broader OHM service graph; the specific consumers are:

- `gcx/` + `gcx-api/` in the parent tree — Flask proxies that fetch geocontext assets from `raw.githubusercontent.com` on a `geocontext` branch. The published `gcx.json` and `datasets/*.geojson` are served straight through to clients.
- Clients (the OHM front-end / digitizer) parse `gcx.json` and request each `conf.source` URL relative to the geocontext root.

Practical consequence: every path referenced inside `gcx.json` must exist at the same relative path in this repo, and any rename of a file under `datasets/` is a breaking change for anyone who has the URL pinned.

## `gcx.json` structure

The schema in use here:

```
{
  "title":     string,
  "type":      "2d",
  "center":    [lat, lon],         // note: lat-first, not GeoJSON [lon, lat]
  "minzoom" / "startzoom" / "maxzoom": int,
  "datasources": [ { "name", "type": "geojson+http+remote", "conf": { "source": "datasets/..." } } ],
  "layers":      [ { "name", "type": "features", "datasource": <name>, "style": { ... } } ]
}
```

A `layer.datasource` must equal some `datasources[].name`. Styles use the `"style": "mapbox"` family with `mode` ∈ {`marker`, `line`, `polygon`}; marker layers additionally take `markerType` (e.g. `circle`) and Leaflet-style `options` (`radius`, `fillColor`, `color`, `weight`, `opacity`, `fillOpacity`).

When adding a dataset, add **both** a `datasources` entry and a matching `layers` entry — having one without the other produces a broken UI rather than a load error.

## Directory layout

- `datasets/` — the GeoJSON files referenced by `gcx.json`. **These are the canonical files**; touch carefully.
- `layers/` — a separate pair (`locations_cdcdzczcd.geojson` + `.qml`) that is **not** wired into `gcx.json`. The `.qml` is a QGIS style export (QGIS 3.18). The `.geojson` here uses fractional `[lon, lat]` near `(0,0)` with Minecraft-looking `x/y/z` properties — it is unrelated to the Valle Trebba archaeological dataset and appears to be staging material from a different project.

## Conventions and gotchas

- **CRS is WGS84/CRS84 everywhere.** All GeoJSON files in `datasets/` declare `urn:ogc:def:crs:OGC:1.3:CRS84` and use `[lon, lat]` decimal degrees. The filename `valle_trebba_punti_32632.geojson` is misleading — the `_32632` suffix suggests UTM zone 32N but the actual coordinates are lon/lat, not easting/northing. Do not reproject on the assumption that the suffix is accurate; check the file's `crs` block.
- **Property names contain mojibake.** `t_età` appears as `t_et�` (the `à` replaced by U+FFFD) in `valle_trebba_punti_32632.geojson`. This is preserved on disk — front-end code may key off the corrupted name, so do not silently "fix" it without checking consumers. If you do clean it up, do so in a dedicated commit and grep the gcx-api consumer side first.
- **`center` is `[lat, lon]`.** The gcx renderer expects latitude first in `center`, opposite of the GeoJSON `coordinates` convention used inside the dataset files. The current value `[44.702654, 12.121156]` is lat-first (Valle Trebba is at ~44.7°N, 12.1°E).
- **Large files are normal here.** `valle_trebba_linee.geojson` is ~3.5 MB and `locations_cdcdzczcd.geojson` is ~1.7 MB. They are the product, not bloat — don't try to gitignore or LFS-migrate them without coordinating with the geocontext deployment.
- **No `.gitattributes` / LFS.** Commits go in as plain blobs; this is how `raw.githubusercontent.com` serves them to `gcx-api`.

## Working on this repo

There is nothing to build or run locally. The useful checks before a commit are:

1. `python -c "import json; json.load(open('gcx.json'))"` — confirms `gcx.json` parses.
2. For each modified dataset: `python -c "import json; d=json.load(open('datasets/<file>.geojson')); print(d['type'], len(d['features']))"` — confirms it loads and reports feature count.
3. Eyeball that every `datasources[].conf.source` in `gcx.json` corresponds to an existing file under `datasets/`, and that every `layers[].datasource` matches a `datasources[].name`.

If you need to preview the rendered map, point a local `gcx-api` (in `/srv/ohm/gcx-api/`) at this working tree, or push to a branch the deployed `gcx-api` is configured to read from.
