# 新竹市牙醫診所 GitHub Pages 導覽

此專案提供基於 `Dentist_Hsinchu_City.csv` 的靜態網站，於 GitHub Pages 開啟即看到依社區分類的診所列表，每間診所亦有獨立頁面、封面圖與前往 Google 地圖的捷徑。

## 主要特色
- **社區分類首頁**：`docs/index.html` 會讀取 CSV 並依地址中的「里」自動分組，可搜尋診所名稱或社區關鍵字。
- **獨立診所頁面**：每間診所會有 `clinic.html?slug=...` 的獨立頁面，含封面、聯絡資訊、社區標籤與 Google 地圖連結。
- **Google 星等區塊**：可選擇設定 Google Maps API Key 來取得即時評分，未設定時會顯示提醒文字。

## GitHub Pages 發佈
1. 確認已啟用 GitHub Pages，並將發佈來源設為 `docs/` 目錄。
2. Push 後，造訪倉庫的 Pages 網址即可直接看到首頁，而非 README。

## 設定 Google 星等（可選）
1. 打開 `docs/config.js`。
2. 將 `window.GOOGLE_MAPS_API_KEY` 填入您的 Google Maps/Places API Key。
3. 儲存並重新部署 GitHub Pages；首頁與獨立頁面會透過 Places API 取得星等與評價數。

> 提醒：前端直接呼叫 Google API 會公開金鑰，建議限制網域或改用自架的 proxy 服務。
