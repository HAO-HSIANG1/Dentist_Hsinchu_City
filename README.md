# Dentist_Hsinchu_City
整理新竹市的牙醫診所，並作成獨立網站。

## 產生 GitHub Pages 靜態網站

1. 執行 `python generate_site.py`，會依據 `Dentist_Hsinchu_City.csv` 讀出的 154 筆資料，在 `docs/` 底下產生首頁與每間診所的獨立頁面。
2. 將 `docs/` 作為 GitHub Pages 的來源，即可線上瀏覽：首頁位於 `/docs/index.html`，每家診所的詳細頁則在 `/docs/clinics/*.html`。
