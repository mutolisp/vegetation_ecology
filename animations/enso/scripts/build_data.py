#!/usr/bin/env python3
"""重建 ENSO 動畫所用的資料檔（Rebuild the data embedded in ../index.html）。

用法 Usage:
    python3 build_data.py enso     # NOAA CPC ONI(ERSSTv6) 與 RONI 表 → data/enso_index_noaa_cpc.csv
    python3 build_data.py oisst    # NOAA OISST v2.1 1991–2020 長期月平均 → 1° 年平均（需 netCDF4、numpy）
    python3 build_data.py land     # Natural Earth 1:110m land → 動畫內嵌的精簡座標

產生的字串需手動貼回 index.html 對應的 <script id="ensoCsv">、<script id="oisstData">、<script id="landData"> 區塊。
"""
import base64
import json
import re
import sys
import urllib.request
from html import unescape
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'
SEASONS = 'DJF JFM FMA MAM AMJ MJJ JJA JAS ASO SON OND NDJ'.split()
CPC = {
    'oni_v6': 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/',
    'roni': 'https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/',
}
OISST_URL = 'https://downloads.psl.noaa.gov/Datasets/noaa.oisst.v2.highres/sst.mon.ltm.1991-2020.nc'
LAND_URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson'


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def parse_cpc_table(html):
    """解析 CPC 網頁表格：每列為年份加 12 個重疊季的數值。"""
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S)
    t = re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', t)))
    out = {}
    for m in re.finditer(r'\b(19[5-9]\d|20[0-9]\d)((?: -?\d\.\d){1,12})(?= (?:Year|19|20|Back|NOAA))', t):
        for i, v in enumerate(m.group(2).split()):
            out[(int(m.group(1)), i)] = float(v)
    return out


def build_enso():
    tables = {k: parse_cpc_table(fetch(u).decode('latin-1')) for k, u in CPC.items()}
    keys = sorted(set().union(*tables.values()))
    path = DATA / 'enso_index_noaa_cpc.csv'
    with open(path, 'w') as f:
        f.write('year,season,center_month,oni_v6,roni\n')
        for y, i in keys:
            f.write(f"{y},{SEASONS[i]},{i + 1},{tables['oni_v6'].get((y, i), '')},{tables['roni'].get((y, i), '')}\n")
    print(f'{path}: {len(keys)} seasons')


def build_oisst():
    import numpy as np
    import netCDF4 as nc
    nc_path = DATA / 'sst.mon.ltm.1991-2020.nc'
    if not nc_path.exists():
        nc_path.write_bytes(fetch(OISST_URL))          # 約 46 MB，未納入版本控制
    d = nc.Dataset(nc_path)
    a = np.ma.filled(d.variables['sst'][:].mean(axis=0).astype('f8'), np.nan)   # 12 個月平均
    b = a.reshape(180, 4, 360, 4)                                                 # 0.25° → 1°
    cnt = np.sum(~np.isnan(b), axis=(1, 3))
    g = np.where(cnt > 0, np.nansum(b, axis=(1, 3)) / np.maximum(cnt, 1), np.nan)
    with open(DATA / 'oisst_v2.1_ltm_1991-2020_annual_1deg.csv', 'w') as f:
        f.write('# NOAA/NCEI OISST v2.1, long-term monthly mean 1991-2020 (sst.mon.ltm.1991-2020.nc via NOAA PSL), '
                'annual mean of 12 months, averaged from 0.25 to 1 degree; ocean cells only (deg C)\n')
        f.write('lat,lon,sst_c\n')
        for j in range(180):
            for i in range(360):
                if not np.isnan(g[j, i]):
                    f.write(f'{-89.5 + j},{0.5 + i},{g[j, i]:.2f}\n')
    # 陸地格點以鄰近海值反覆填補（僅供貼圖內插，陸地在畫面上會被覆蓋）
    filled = ~np.isnan(g)
    f = np.where(filled, g, 0.0)
    while not filled.all():
        acc = np.zeros_like(f)
        n = np.zeros_like(f)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            sh = np.roll(np.roll(np.where(filled, f, 0), dx, axis=1), dy, axis=0)
            shm = np.roll(np.roll(filled, dx, axis=1), dy, axis=0)
            if dy == -1:
                sh[-1, :] = 0; shm[-1, :] = False
            if dy == 1:
                sh[0, :] = 0; shm[0, :] = False
            acc += sh
            n += shm
        new = (~filled) & (n > 0)
        f[new] = acc[new] / n[new]
        filled |= new
    q = np.clip(np.round((f + 2.0) * 7.0), 0, 255).astype(np.uint8)              # T = q/7 − 2 °C
    (DATA / 'oisst_1deg_u8.b64').write_text(base64.b64encode(q.tobytes()).decode())
    print('oisstData → data/oisst_1deg_u8.b64')


def build_land():
    path = DATA / 'ne_110m_land.geojson'
    if not path.exists():
        path.write_bytes(fetch(LAND_URL))
    rings = []
    for feat in json.loads(path.read_text())['features']:
        geom = feat['geometry']
        polys = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']
        for poly in polys:
            pts = []
            for lon, lat in poly[0]:                                   # 只取外環
                p = (round(lon * 10), round(lat * 10))                 # 座標 ×10 取整
                if not pts or pts[-1] != p:
                    pts.append(p)
            if len(pts) >= 4:
                rings.append([v for p in pts for v in p])
    (DATA / 'land_rings.json').write_text(json.dumps(rings, separators=(',', ':')))
    print(f'landData → data/land_rings.json ({len(rings)} rings)')


if __name__ == '__main__':
    {'enso': build_enso, 'oisst': build_oisst, 'land': build_land}[sys.argv[1]]()
