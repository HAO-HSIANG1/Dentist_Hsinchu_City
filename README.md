# 新竹市牙醫診所 GitHub Pages 網站

此專案將 `Dentist_Hsinchu_City.csv` 轉成可於 GitHub Pages 發佈的靜態網站：首頁依「里」分組列出診所，並為每家診所建立獨立的頁面，附上 Google 地圖捷徑與 Google 星等資訊欄位（若尚未提供評分，則顯示「尚未提供」）。

## 快速使用
1. 安裝 Python 3.11 以上（標準函式庫即可）。
2. 執行下列指令產生靜態頁面檔案：
   ```bash
   python generate_pages.py
   ```
   產出的檔案位於 `docs/`，其中 `index.html` 為首頁、`docs/clinics/` 內為各診所獨立頁面。
3. 於 GitHub Repository 設定 Pages 發佈來源為 **`docs/` 資料夾**，即可直接開啟網站而非 README。

## Google 星等資料
目前資料集未提供 Google 星等，頁面會顯示「尚未提供」。若日後取得評分，可在 `generate_pages.py` 中填入對應診所的評分後重新執行產生腳本，網站即會自動呈現星星數。

## 專案結構
- `generate_pages.py`：從 CSV 產生 `docs/` 內容的腳本。
- `docs/index.html`：依里別分組的首頁。
- `docs/clinics/*.html`：每間診所的獨立頁面，含地圖連結與聯絡資訊。
- `docs/assets/style.css`：簡易版面與樣式設定。
