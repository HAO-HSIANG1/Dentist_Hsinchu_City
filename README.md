# Dentist_Hsinchu_City

整理新竹市的牙醫診所，並作成獨立網站。

## GitHub Pages 頁面

已將靜態網站放在 `docs/` 目錄中，可直接啟用 GitHub Pages（來源：`docs` 資料夾）。首頁位於 `docs/index.html`，每家診所有獨立頁面在 `docs/clinics/` 底下。

## 如何重新產生網站

1. 確保已安裝 Python 3。
2. 執行產生腳本：

   ```bash
   python generate_sites.py
   ```

腳本會讀取 `Dentist_Hsinchu_City.csv`，更新 `docs/` 內的首頁與各診所頁面。
