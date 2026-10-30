# ENSO 聖嬰－南方振盪 3D 示意動畫

赤道太平洋（10°N–10°S）的 3D 互動示意動畫，說明正常年、聖嬰（El Niño）與反聖嬰（La Niña）的海氣交互作用，以及對陸域生態系與臺灣降雨的影響。

- 線上版：<https://mutolisp.github.io/vegetation_ecology/animations/enso/>
- `index.html` 為單一檔案，three.js、地圖與資料皆已內嵌，可離線開啟。

## 功能

- 三種狀態切換與平滑過渡；信風、沃克環流、積雨雲與降雨、溫躍層、湧升流、陸域植被（乾旱、林火）等圖層。
- 陸地輪廓為真實海岸線；模型範圍南北向放大 3 倍，底圖為以太平洋為中心的世界地圖。
- 海表溫度：NOAA OISST v2.1 的 1991–2020 年平均，熱帶太平洋疊加示意的 ENSO 距平。
- 資料模式：以 NOAA CPC 的 RONI／ONI（1950 起）驅動動畫，時間軸標示國際與臺灣的重要事件；可載入自訂 CSV（需 `year` 與 `season` 或 `month` 欄位）。
- 專有名詞游標提示（定義附來源）、側欄參考文獻。

## 檔案

| 路徑 | 說明 |
|---|---|
| `index.html` | 動畫本體（內嵌下列資料） |
| `data/enso_index_noaa_cpc.csv` | NOAA CPC ONI（ERSSTv6）與 RONI，1950 DJF 起之 3 個月滑動季 |
| `data/oisst_v2.1_ltm_1991-2020_annual_1deg.csv` | OISST v2.1 1991–2020 長期月平均之年平均，1° 網格，僅海洋格點（°C） |
| `data/ne_110m_land.geojson` | Natural Earth 1:110m 陸地多邊形（原始檔） |
| `scripts/build_data.py` | 重建上述資料與內嵌字串 |
| `scripts/build_three_bundle.sh` | 重建內嵌的 three.js 0.160.0 |

## 資料來源與授權

- **ONI / RONI**：NOAA Climate Prediction Center。<https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/>、<https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/>（擷取日期 2026-10-30；最近數季為暫估值，可能修正）。
- **海表溫度**：NOAA/NCEI 1/4° Daily OISST v2.1（Huang et al., 2021, *Journal of Climate*, 34(8), 2923–2939, <https://doi.org/10.1175/JCLI-D-20-0166.1>）。Data provided by the NOAA PSL, Boulder, Colorado, USA, from their website at <https://psl.noaa.gov>.
- **地圖**：Made with Natural Earth（公有領域），<https://github.com/nvkelso/natural-earth-vector>。
- **three.js**：MIT License，© 2010–2023 three.js authors。
- 事件、臺灣降雨與名詞定義的來源列於動畫側欄的參考文獻。

動畫為教學示意：垂直尺度、海平面高低、ENSO 距平與地形高度皆經簡化或誇大，非實際觀測場。
