#!/usr/bin/env python3
"""
Generate a pre-baked coastline GeoJSON clipped to the NeSPReSO bbox and save under assets/.

Usage:
  python tools/make_coastline.py

Requires: cartopy, shapely
"""
import os
import json

try:
    from cartopy.io import shapereader as shpreader
except Exception as exc:
    raise SystemExit(f"Cartopy not available: {exc}")

try:
    from shapely.geometry import LineString, MultiLineString, box
except Exception as exc:
    raise SystemExit(f"Shapely not available: {exc}")


def extract_lines(geom):
    if isinstance(geom, LineString):
        return [geom]
    if isinstance(geom, MultiLineString):
        return list(geom.geoms)
    if hasattr(geom, 'geoms'):
        lines = []
        for g in geom.geoms:
            lines.extend(extract_lines(g))
        return lines
    return []


def collect_features(name: str, clip_box):
    """Return list of GeoJSON features for the given Natural Earth layer name."""
    try:
        shp_path = shpreader.natural_earth(resolution="50m", category="physical", name=name)
        reader = shpreader.Reader(shp_path)
    except Exception as exc:
        print(f"Failed to get Natural Earth layer '{name}': {exc}")
        return []

    feats = []
    CUTOFF_LON = -100.0  # remove any segments west of -100W
    for rec in reader.records():
        geom = rec.geometry
        try:
            inter = geom.intersection(clip_box)
        except Exception:
            continue
        if inter.is_empty:
            continue
        # For 'land' layer, use boundary
        to_lines = inter if name != 'land' else inter.boundary
        for line in extract_lines(to_lines):
            xs, ys = line.xy
            seg_xs, seg_ys = [], []
            for x, y in zip(xs, ys):
                if float(x) >= CUTOFF_LON:
                    seg_xs.append(float(x))
                    seg_ys.append(float(y))
                else:
                    if seg_xs:
                        coords = [[sx, sy] for sx, sy in zip(seg_xs, seg_ys)]
                        feats.append({
                            'type': 'Feature',
                            'properties': {},
                            'geometry': {'type': 'LineString', 'coordinates': coords}
                        })
                        seg_xs, seg_ys = [], []
            if seg_xs:
                coords = [[sx, sy] for sx, sy in zip(seg_xs, seg_ys)]
                feats.append({
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {'type': 'LineString', 'coordinates': coords}
                })
    return feats


def main():
    bbox = dict(lon_min=-102, lon_max=-78, lat_min=17, lat_max=31)
    clip = box(bbox['lon_min'], bbox['lat_min'], bbox['lon_max'], bbox['lat_max'])

    features = collect_features('coastline', clip)
    if not features:
        features = collect_features('land', clip)

    fc = {'type': 'FeatureCollection', 'features': features}
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'coastline_gom_50m.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(fc, f)
    print(f"Wrote coastline: {out_path} (features: {len(features)})")


if __name__ == '__main__':
    main()


