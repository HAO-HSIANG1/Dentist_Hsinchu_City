# Dentist_Hsinchu_City

整理新竹市的牙醫診所，並作成獨立網站。

## GitHub Pages 靜態網站

專案已經能將 `Dentist_Hsinchu_City.csv` 轉成 GitHub Pages 可以直接上線的靜態網站：

- `docs/index.html`：診所列表、搜尋與導向各診所專頁。
- `docs/clinics/*.html`：每一家牙醫診所的獨立專頁，包含地址、電話、負責人與代碼資訊。

啟用 GitHub Pages 時，請將發佈來源設定為 **docs/** 資料夾。

## 如何重新產生網站

1. 確認系統有 Python 3。
2. 執行 `python generate_sites.py`，會依據最新 CSV 重新生成 `docs/` 內容。
3. 若在本機預覽，可在專案根目錄啟動簡易伺服器：
   ```bash
   cd docs
   python -m http.server 8000
   ```
   然後在瀏覽器開啟 `http://localhost:8000`。
