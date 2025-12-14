# Dentist_Hsinchu_City
整理新竹市的牙醫診所，並作成獨立網站。

## 生成靜態網站

1. 安裝 Python 3（內建於大部分環境）。
2. 執行 `python generate_sites.py`，會讀取 `Dentist_Hsinchu_City.csv` 並在 `docs/` 下生成：
   - 首頁 `index.html`：可搜尋並瀏覽所有診所卡片。
   - `clinics/`：每間牙醫診所的獨立頁面，包含電話、地址與地圖連結。
3. 啟動開發伺服器預覽，例如：`python -m http.server 8000 -d docs`，在瀏覽器開啟 `http://localhost:8000`。

將 `docs/` 目錄推送到 GitHub 後，可直接用 GitHub Pages 發佈整個靜態網站。
