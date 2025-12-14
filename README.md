# Dentist_Hsinchu_City

整理新竹市的牙醫診所，並作成獨立網站。

## 生成靜態頁面

1. 安裝 Python 3.10+。
2. 在儲存庫根目錄執行：
   ```bash
   python generate_sites.py
   ```
3. 產生的網站位於 `docs/`（GitHub Pages 可直接使用），`docs/clinics/` 中每個 HTML 檔案對應一間牙醫診所。

## GitHub Pages 設定提示

- 將專案的 GitHub Pages Source 設為 `main` 分支的 `/docs` 資料夾即可。
- 入口頁面為 `docs/index.html`，列出所有診所並連結到對應的獨立頁面。
