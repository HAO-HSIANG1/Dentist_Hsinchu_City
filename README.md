# 新竹市牙醫診所 GitHub Pages 網站

這個倉庫會把 `Dentist_Hsinchu_City.csv` 的 154 家牙醫診所資料轉成靜態網站，並以 GitHub Pages 發佈。

## 功能亮點
- 首頁 `index.html` 直接呈現網站內容（不再顯示 README），依行政區（東區、北區、香山區）分類卡片列表。
- 每家診所有自己的獨立頁面（`clinics/*.html`），包含地址、負責人、電話與 Google 星等示意分數（依診所名稱雜湊產生，方便後續替換為真實評價）。
- 採用一致的樣式檔 `styles.css`，首頁與獨立頁面共用。

## 重新產生頁面
若更新了 `Dentist_Hsinchu_City.csv`，執行下列指令會重新生成首頁與所有獨立頁面：

```bash
python generate_site.py
```

生成的檔案包含：
- `index.html`：依行政區呈現的總覽首頁。
- `clinics/*.html`：每家牙醫診所的獨立介紹頁。
- `styles.css`：網站樣式。

## GitHub Pages 設定建議
在 GitHub 專案設定中，將 Pages 來源設為 `main` 分支的 `/root`（專案根目錄）即可直接以 `index.html` 做為首頁。
