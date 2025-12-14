import csv
import html
import re
from pathlib import Path
from string import Template
from urllib.parse import quote_plus

DATA_FILE = Path("Dentist_Hsinchu_City.csv")
DOCS_DIR = Path("docs")
CLINICS_DIR = DOCS_DIR / "clinics"
ASSETS_DIR = DOCS_DIR / "assets"


def slugify(name: str, idx: int) -> str:
    safe = re.sub(r"[^\w\u4e00-\u9fff]+", "-", name).strip("-")
    base = safe or "clinic"
    return f"{idx + 1:03d}-{base}"


def ensure_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    style = ASSETS_DIR / "style.css"
    if not style.exists():
        style.write_text(
            """
:root {
  font-family: 'Noto Sans TC', 'Noto Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: #1f2933;
  background: #f7fafc;
}
body {
  margin: 0;
  background: #f7fafc;
}
header {
  background: linear-gradient(120deg, #5cc8d7, #4da1ff);
  color: #fff;
  padding: 2.5rem 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}
main {
  max-width: 1100px;
  margin: -2rem auto 3rem;
  padding: 0 1rem;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}
.card {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.card h2 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
}
.card p {
  margin: 0;
  color: #475569;
}
.card a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}
.details {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  border: 1px solid #e5e7eb;
}
.details dl {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 0.75rem 1rem;
  margin: 0;
}
.details dt {
  font-weight: 700;
  color: #1f2933;
}
.details dd {
  margin: 0;
  color: #475569;
}
.breadcrumb {
  margin: 1rem 0 1.5rem;
}
.breadcrumb a {
  color: #2563eb;
  text-decoration: none;
}
footer {
  text-align: center;
  color: #94a3b8;
  padding: 1.5rem 0 3rem;
}
.search-box {
  max-width: 520px;
  margin: 0 auto 2rem;
  position: sticky;
  top: 0.75rem;
}
.search-box input {
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  font-size: 1rem;
}
.no-results {
  text-align: center;
  color: #94a3b8;
}
@media (max-width: 640px) {
  .details dl { grid-template-columns: 1fr; }
  .details dt { color: #2563eb; }
}
""",
            encoding="utf-8",
        )


def build_index(rows):
    DOCS_DIR.mkdir(exist_ok=True)
    cards = []
    for row in rows:
        cards.append(
            f"<article class='card'>"
            f"<h2><a href='clinics/{row['slug']}.html'>{html.escape(row['機構名稱'])}</a></h2>"
            f"<p>地址：{html.escape(row['街道項弄號'])}</p>"
            f"<p>電話：{html.escape(row['電話'])}</p>"
            f"</article>"
        )
    index_template = Template(
        """
<!DOCTYPE html>
<html lang='zh-Hant'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>新竹市牙醫診所地圖</title>
  <link rel='stylesheet' href='assets/style.css'>
</head>
<body>
  <header>
    <h1>新竹市牙醫診所地圖</h1>
    <p>依據資料集自動生成的診所網站，點擊即可進入個別診所頁面。</p>
  </header>
  <main>
    <div class='search-box'>
      <input type='search' id='search' placeholder='輸入診所名稱或地址關鍵字搜尋'>
    </div>
    <section class='card-grid' id='clinic-list'>
      $cards
    </section>
    <p class='no-results' id='no-results' style='display:none;'>查無符合條件的診所</p>
  </main>
  <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
  <script>
    const searchInput = document.getElementById('search');
    const cards = Array.from(document.querySelectorAll('#clinic-list .card'));
    const noResult = document.getElementById('no-results');
    searchInput.addEventListener('input', () => {
      const keyword = searchInput.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach(card => {
        const text = card.innerText.toLowerCase();
        const match = text.includes(keyword);
        card.style.display = match ? 'flex' : 'none';
        if (match) visible += 1;
      });
      noResult.style.display = visible === 0 ? 'block' : 'none';
    });
  </script>
</body>
</html>
        """
    )
    index_html = index_template.substitute(cards="\n      ".join(cards))
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")


def build_clinic_pages(rows):
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)
    template = """
<!DOCTYPE html>
<html lang='zh-Hant'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>{title}</title>
  <link rel='stylesheet' href='../assets/style.css'>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>為新竹市牙醫診所資料自動生成的獨立頁面。</p>
  </header>
  <main>
    <div class='breadcrumb'><a href='../index.html'>← 回到診所列表</a></div>
    <article class='details'>
      <dl>
        <dt>機構名稱</dt><dd>{name}</dd>
        <dt>負責人</dt><dd>{owner}</dd>
        <dt>電話</dt><dd><a href='tel:{tel}'>{tel}</a></dd>
        <dt>地址</dt><dd>{address}</dd>
        <dt>縣市別代碼</dt><dd>{city_code}</dd>
        <dt>行政區域代碼</dt><dd>{district_code}</dd>
      </dl>
      <p style='margin-top:1.25rem;'>
        <a href='{map_link}' target='_blank' rel='noopener'>在 Google 地圖開啟</a>
      </p>
    </article>
  </main>
  <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
</body>
</html>
"""
    for row in rows:
        map_query = quote_plus(f"{row['機構名稱']} {row['街道項弄號']}")
        clinic_html = template.format(
            title=html.escape(row['機構名稱']),
            name=html.escape(row['機構名稱']),
            owner=html.escape(row['負責人']),
            tel=html.escape(row['電話']),
            address=html.escape(row['街道項弄號']),
            city_code=html.escape(row['縣市別代碼']),
            district_code=html.escape(row['行政區域代碼']),
            map_link=f"https://www.google.com/maps/search/?api=1&query={map_query}",
        )
        (CLINICS_DIR / f"{row['slug']}.html").write_text(clinic_html, encoding="utf-8")


def load_data():
    if not DATA_FILE.exists():
        raise SystemExit("找不到 Dentist_Hsinchu_City.csv 檔案")
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    prepared = []
    for idx, row in enumerate(rows):
        prepared.append({**row, "slug": slugify(row["機構名稱"], idx)})
    return prepared


def main():
    rows = load_data()
    ensure_assets()
    build_index(rows)
    build_clinic_pages(rows)
    print(f"已產生 {len(rows)} 筆診所網站，存放於 docs/ 目錄下。")


if __name__ == "__main__":
    main()
