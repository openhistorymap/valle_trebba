#!/usr/bin/env python3
"""
Quick-and-dirty renderer for the Valle Trebba georender ruleset.

Pragmatic deviations from the full georender spec:
  - polygon_texture rules render as flat tint (texture tiling skipped).
  - palificazioni_legno (Point + 15 cm buffer) skipped: sub-pixel at this scale.
  - edge_fade implemented via ImageMagick distance morphology.

Inputs:
  georender_ruleset.json, gcx.json, exports/valle_trebba.bbox.json,
  exports/valle-trebba-wms-agea2011.jpg (base).
Output:
  exports/valle-trebba-5.png
"""
import json
import os
import subprocess
import tempfile

ROOT = '/srv/ohm/valle_trebba'
RULESET = f'{ROOT}/georender_ruleset.json'
GCX = f'{ROOT}/gcx.json'
BBOX_FILE = f'{ROOT}/exports/valle_trebba.bbox.json'
WMS_BASE = f'{ROOT}/exports/valle-trebba-wms-agea2011.jpg'
OUT = f'{ROOT}/exports/valle-trebba-5.png'

bb = json.load(open(BBOX_FILE))
W, S, E, N = bb['bbox']

TW, TH = (int(x) for x in subprocess.check_output(
    ['identify', '-format', '%w %h', WMS_BASE]).decode().split())
print(f'target: {TW} x {TH}')

ruleset = json.load(open(RULESET))
gcx = json.load(open(GCX))

ds_to_file = {d['name']: d.get('conf', {}).get('source') for d in gcx['datasources']}
layer_to_ds = {L['name']: L.get('datasource') for L in gcx['layers']}


def hex_to_rgba(h):
    h = h.lstrip('#')
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    raise ValueError(h)


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True, text=True)


with tempfile.TemporaryDirectory(prefix='render_') as tmp:
    canvas = f'{tmp}/canvas.png'
    run(['convert', WMS_BASE, canvas])

    rules = sorted(
        [r for r in ruleset['rules'] if r['symbolizer'].get('type') != 'wms'],
        key=lambda r: r.get('z_index', 0),
    )

    for rule in rules:
        sym = rule['symbolizer']
        flt = rule.get('filter', {})
        layer_name = flt.get('__layer')
        if not layer_name:
            continue
        ds_name = layer_to_ds.get(layer_name)
        src = ds_to_file.get(ds_name)
        if not src:
            print(f'  SKIP {rule["name"]:22s}  no file for ds={ds_name!r}')
            continue
        src_path = f'{ROOT}/{src}'
        if not os.path.exists(src_path):
            print(f'  SKIP {rule["name"]:22s}  missing {src}')
            continue

        sym_type = sym.get('type')
        if sym_type == 'polygon_fill':
            r, g, b, a = hex_to_rgba(sym['fill'])
            op = sym.get('opacity', 1.0) * (a / 255)
        elif sym_type == 'polygon_texture':
            r, g, b, _ = hex_to_rgba(sym.get('tint', '#ffffff'))
            op = sym.get('opacity', 1.0)
        else:
            continue

        edge_fade = rule.get('edge_fade', {}).get('distance_px', 0)
        print(f'  {rule["name"]:22s}  src={os.path.basename(src_path):42s}  '
              f'rgb=({r:3d},{g:3d},{b:3d}) op={op:.2f} fade={edge_fade}')

        mask = f'{tmp}/{rule["name"]}_mask.tif'
        run([
            'gdal_rasterize', '-q',
            '-burn', '255',
            '-te', str(W), str(S), str(E), str(N),
            '-ts', str(TW), str(TH),
            '-ot', 'Byte', '-of', 'GTiff',
            src_path, mask,
        ])

        # Build the per-layer alpha: blur for soft edge, scale by opacity.
        # IM's `-morphology Distance Euclidean:N` clamps to 0 past N steps,
        # so a small distance_px zeros the whole mask; Gaussian blur is the
        # robust fallback.
        alpha = f'{tmp}/{rule["name"]}_alpha.png'
        blur_radius = max(edge_fade / 2.0, 0.0)
        run([
            'convert', mask,
            '-blur', f'0x{blur_radius}',
            '-evaluate', 'Multiply', str(op),
            alpha,
        ])

        tinted = f'{tmp}/{rule["name"]}_tinted.png'
        run([
            'convert', '-size', f'{TW}x{TH}', f'xc:rgb({r},{g},{b})',
            alpha, '-compose', 'CopyOpacity', '-composite',
            tinted,
        ])

        out = f'{tmp}/canvas_next.png'
        run(['convert', canvas, tinted, '-compose', 'Over', '-composite', out])
        os.replace(out, canvas)

    run(['convert', canvas, OUT])
    print(f'wrote {OUT}')
    print(f'  size: {os.path.getsize(OUT)/1024:.1f} KB')
