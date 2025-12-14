import csv
import html
import unicodedata
from pathlib import Path

SOURCE_CSV = Path("Dentist_Hsinchu_City.csv")
OUTPUT_DIR = Path("docs")
CLINICS_DIR = OUTPUT_DIR / "clinics"


def slugify(name: str, index: int) -> str:
    """Create a stable, readable slug for each clinic page."""
    normalized = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(
        ch if ch.isalnum() else "-" for ch in normalized if not unicodedata.combining(ch)
    ).strip("-")
    ascii_only = "-".join(filter(None, ascii_only.split("-")))
    base = ascii_only.lower() if ascii_only else "clinic"
    return f"{base}-{index + 1:03d}.html"


def read_clinics():
    with SOURCE_CSV.open(encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        clinics = []
        for idx, row in enumerate(reader):
            name = row["機構名稱"].strip()
            address = row["街道項弄號"].strip()
            director = row["負責人"].strip()
            phone = row["電話"].strip()
            city_code = row["縣市別代碼"].strip()
            district_code = row["行政區域代碼"].strip()
            slug = slugify(name, idx)
            clinics.append(
                {
                    "name": name,
                    "address": f"新竹市{address}",
                    "director": director,
                    "phone": phone,
                    "city_code": city_code,
                    "district_code": district_code,
                    "slug": slug,
                }
            )
    return clinics


def write_base_files():
    OUTPUT_DIR.mkdir(exist_ok=True)
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)
    style_path = OUTPUT_DIR / "style.css"
    style_path.write_text(
        """
:root {
  --brand: #0f766e;
  --brand-dark: #0c615b;
  --bg: #f8fafc;
  --text: #0f172a;
  --muted: #475569;
  --card-bg: #ffffff;
  --border: #e2e8f0;
}

* { box-sizing: border-box; }
body {
  font-family: "Noto Sans TC", "Inter", system-ui, -apple-system, sans-serif;
  margin: 0;
  color: var(--text);
  background: var(--bg);
}
header {
  background: linear-gradient(135deg, var(--brand), var(--brand-dark));
  color: white;
  padding: 48px 24px 32px;
  text-align: center;
}
.header-inner { max-width: 960px; margin: 0 auto; }
h1 { margin: 0; font-size: 2.25rem; letter-spacing: 0.5px; }
p.lead { margin-top: 12px; color: rgba(255,255,255,0.9); }
main { max-width: 1100px; margin: -32px auto 0; padding: 0 16px 48px; }
.search-box {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.08);
}
input[type="search"] {
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  font-size: 1rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 20px;
}
.card {
  background: var(--card-bg);
  padding: 18px;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 14px 34px rgba(15, 23, 42, 0.1); }
.card h2 { margin: 0 0 6px; font-size: 1.1rem; }
.card .meta { color: var(--muted); margin-bottom: 8px; font-size: 0.95rem; }
.card a.primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--brand);
  text-decoration: none;
  font-weight: 600;
}
.card a.primary:hover { text-decoration: underline; }
.detail {
  max-width: 760px;
  margin: 0 auto;
  background: var(--card-bg);
  padding: 24px;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 10px 36px rgba(15, 23, 42, 0.08);
}
.detail h1 { margin-top: 0; }
.detail .row { margin: 10px 0; color: var(--muted); }
.detail .label { display: block; font-weight: 700; color: var(--text); }
.detail .back-link { margin-top: 16px; display: inline-block; }
footer { text-align: center; color: var(--muted); padding: 32px 12px 40px; }
@media (max-width: 640px) { header { padding: 36px 20px; } }
""",
        encoding="utf-8",
    )


def build_index(clinics):
    cards = []
    for clinic in clinics:
        card = f"""
        <article class=\"card\" data-filter=\"{html.escape(clinic['name'])} {html.escape(clinic['address'])} {html.escape(clinic['director'])}\">
          <h2>{html.escape(clinic['name'])}</h2>
          <div class=\"meta\">{html.escape(clinic['address'])}</div>
          <div class=\"meta\">負責人：{html.escape(clinic['director'])}</div>
          <div class=\"meta\">電話：<a href=\"tel:{html.escape(clinic['phone'])}\">{html.escape(clinic['phone'])}</a></div>
          <a class=\"primary\" href=\"clinics/{clinic['slug']}\">查看診所專頁 →</a>
        </article>
        """
        cards.append(card)

    search_script = """
      const input = document.querySelector('input[type="search"]');
      const cards = document.querySelectorAll('[data-filter]');
      input.addEventListener('input', () => {
        const keyword = input.value.trim().toLowerCase();
        cards.forEach(card => {
          const matches = card.dataset.filter.toLowerCase().includes(keyword);
          card.style.display = matches ? '' : 'none';
        });
      });
    """

    index_html = f"""
<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>新竹市牙醫診所彙整</title>
  <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
<header>
  <div class=\"header-inner\">
    <h1>新竹市牙醫診所地圖</h1>
    <p class=\"lead\">每一家診所都有專屬頁面，方便快速找到聯絡資訊與負責人。</p>
  </div>
</header>
<main>
  <section class=\"search-box\">
    <label for=\"search\">搜尋診所名稱、地址或醫師：</label>
    <input type=\"search\" id=\"search\" placeholder=\"輸入關鍵字...\" aria-label=\"搜尋診所\">
  </section>
  <section class=\"grid\">
    {''.join(cards)}
  </section>
</main>
<footer>
  依據《Dentist_Hsinchu_City.csv》資料生成，可直接部署於 GitHub Pages。
</footer>
<script>
{search_script}
</script>
</body>
</html>
"""
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")


def build_clinic_pages(clinics):
    for clinic in clinics:
        detail_html = f"""
<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html.escape(clinic['name'])}｜新竹市牙醫診所</title>
  <link rel=\"stylesheet\" href=\"../style.css\">
</head>
<body>
<header>
  <div class=\"header-inner\">
    <h1>{html.escape(clinic['name'])}</h1>
    <p class=\"lead\">專屬頁面包含地址、聯絡電話與負責人資訊。</p>
  </div>
</header>
<main>
  <div class=\"detail\">
    <div class=\"row\"><span class=\"label\">地址</span>{html.escape(clinic['address'])}</div>
    <div class=\"row\"><span class=\"label\">負責人</span>{html.escape(clinic['director'])}</div>
    <div class=\"row\"><span class=\"label\">聯絡電話</span><a href=\"tel:{html.escape(clinic['phone'])}\">{html.escape(clinic['phone'])}</a></div>
    <div class=\"row\"><span class=\"label\">縣市代碼</span>{html.escape(clinic['city_code'])}</div>
    <div class=\"row\"><span class=\"label\">行政區域代碼</span>{html.escape(clinic['district_code'])}</div>
    <a class=\"primary back-link\" href=\"../index.html\">← 返回診所總覽</a>
  </div>
</main>
<footer>
  由《Dentist_Hsinchu_City.csv》資料自動產生，適用 GitHub Pages 靜態部署。
</footer>
</body>
</html>
"""
        (CLINICS_DIR / clinic["slug"]).write_text(detail_html, encoding="utf-8")


def main():
    clinics = read_clinics()
    write_base_files()
    build_index(clinics)
    build_clinic_pages(clinics)


if __name__ == "__main__":
    main()
