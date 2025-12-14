# Dentist_Hsinchu_City

整理新竹市的牙醫診所，並作成獨立網站。

## 如何生成 GitHub Pages 靜態網站

1. 安裝 Python 3。
2. 執行 `python generate_sites.py`，會依照 `Dentist_Hsinchu_City.csv` 在 `docs/` 產生首頁及每間診所的獨立頁面。
3. 將 GitHub Pages 的來源設定為 `docs/` 資料夾即可部署。

首頁支援名稱／負責人關鍵字篩選，每個診所頁面包含電話、地址與 Google Maps 開啟連結。
