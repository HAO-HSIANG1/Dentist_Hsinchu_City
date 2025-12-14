# Dentist Hsinchu City 靜態網站

本專案使用 `Dentist_Hsinchu_City.csv` 生成 GitHub Pages 版本的新竹市牙醫診所導覽網站：

- 首頁 `index.html`：以社區（東區、北區、香山區）分區展示所有診所卡片，並提供前往各診所獨立頁面與 Google Maps 的連結。
- 區域頁 `districts/<社區>.html`：呈現該社區內的診所清單。
- 診所頁 `clinics/clinic-XXX.html`：每個診所都有獨立頁面，包含封面照（占位圖）、聯絡資訊，以及可點擊的 Google Maps icon。
- 目前 Google 星等未從 API 取得，因此頁面上標示「尚未提供，點擊地圖查看最新評價」。若日後取得評價資料，可改寫 `generate_site.py` 的 `render_rating_section` 或為診所資料增加評分欄位。

## 重新產生網站

```bash
python generate_site.py
```

產生完成後，將 `index.html`、`districts/`、`clinics/`、`assets/` 一併推送至 GitHub，設定 GitHub Pages 指向專案根目錄即可直接開啟網站。
