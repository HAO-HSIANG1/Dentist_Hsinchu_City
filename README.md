# Dentist_Hsinchu_City

整理新竹市的牙醫診所，並作成獨立網站。

## 產生靜態網站

1. 安裝 Python 3（本工具使用標準函式庫，不需額外套件）。
2. 執行 `python generate_sites.py` 會讀取 `Dentist_Hsinchu_City.csv` 並在 `docs/` 產出：
   - `index.html`：所有診所的列表頁面。
   - `docs/clinics/*.html`：每間診所各自的獨立頁面。
3. 將專案推送到 GitHub，並在 repo 設定的 **Pages** 中將來源設為 `main` 分支的 `docs/` 路徑，即可在 GitHub Pages 上公開所有頁面。

如需重新整理資料，只要更新 CSV 檔後再次執行腳本即可覆蓋產出的頁面。
