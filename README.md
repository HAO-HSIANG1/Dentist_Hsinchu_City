# 新竹市牙醫診所 GitHub Pages 生成器

此專案會將 `Dentist_Hsinchu_City.csv` 的牙醫診所資料轉成 GitHub Pages 靜態網站：

- 首頁 `docs/index.html` 依社區分類列出所有診所，提供地圖捷徑與專屬頁面連結。
- 每家診所在 `docs/clinics/` 中擁有獨立頁面，包含地址、電話、負責人與 Google 地圖按鈕。
- `docs/ratings.json` 可填入 Google 星等（未填寫時頁面會提示使用者改至地圖檢視最新評價）。

## 如何重新生成網頁

1. 確認 `Dentist_Hsinchu_City.csv` 已更新。
2. 執行下列指令重新輸出 JSON 與每家診所頁面：

```bash
python generate_site.py
```

生成結果會寫入 `docs/`。GitHub Pages 可直接設定根目錄為 `docs` 以便發布網站。

## 提供或更新 Google 星等

- 打開 `docs/ratings.json`，依診所 `slug`（檔名同名）填入 `rating`，範例如下：

```json
"森美牙醫診所": { "rating": 4.6, "note": "2024/05 由營運團隊更新" }
```

- 若 `rating` 為 `null` 或未填寫，頁面會顯示「尚未提供星等，請點擊地圖查看最新評論」。

## GitHub Pages 建議設定

在 GitHub Repository 的 **Settings → Pages** 中，將 Source 指定為 `Deploy from a branch`，並選擇 `main` 分支與 `/docs` 資料夾，即可讓訪客直接看到網站而非 README。
