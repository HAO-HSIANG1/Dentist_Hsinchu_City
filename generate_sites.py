import csv
import html
import os
import re
from pathlib import Path
from urllib.parse import quote

CSV_PATH = Path("Dentist_Hsinchu_City.csv")
DOCS_DIR = Path("docs")
CLINIC_DIR = DOCS_DIR / "clinics"
CITY_NAME = "新竹市"

STYLE = """
body {font-family: "Noto Sans TC", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; padding: 0; background: #f5f7fb; color: #1f2933;}
header {background: linear-gradient(120deg, #3b82f6, #06b6d4); color: white; padding: 28px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);} 
header h1 {margin: 0; font-size: 32px;}
main {max-width: 960px; margin: 0 auto; padding: 24px 16px 48px;}
.grid {display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));}
.card {background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);} 
.card h2 {margin: 0 0 8px 0; font-size: 20px;}
.card p {margin: 4px 0; color: #4a5568;}
.card a {color: #2563eb; text-decoration: none;}
.card a:hover {text-decoration: underline;}
.info {background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);} 
.back {display: inline-flex; align-items: center; gap: 6px; margin-bottom: 12px; color: #2563eb; text-decoration: none;}
.meta {color: #4a5568; margin: 6px 0;}
button.search-btn {background: #2563eb; color: white; border: none; padding: 8px 12px; border-radius: 8px; cursor: pointer; margin-left: 8px;}
input.search-input {padding: 8px 10px; border-radius: 8px; border: 1px solid #cbd5e1; min-width: 200px;}
@media (max-width: 600px) {header h1 {font-size: 24px;}}
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>新竹市牙醫診所地圖</title>
  <style>{style}</style>
</head>
<body>
  <header>
    <h1>新竹市牙醫診所</h1>
    <p>從 {count} 筆資料自動生成的獨立網站清單</p>
  </header>
  <main>
    <section class=\"info\">
      <p>輸入診所名稱快速篩選：</p>
      <div>
        <input class=\"search-input\" id=\"search\" placeholder=\"輸入診所名稱或負責人\" />
        <button class=\"search-btn\" onclick=\"filterClinics()\">搜尋</button>
      </div>
    </section>
    <div class=\"grid\" id=\"clinics\">
      {cards}
    </div>
  </main>
  <script>
    function filterClinics() {{
      const term = document.getElementById('search').value.trim();
      const cards = document.querySelectorAll('[data-name]');
      cards.forEach(card => {{
        const name = card.dataset.name;
        const owner = card.dataset.owner;
        const match = name.includes(term) || owner.includes(term);
        card.style.display = match ? 'block' : 'none';
      }});
    }}
  </script>
</body>
</html>
"""

CARD_TEMPLATE = """
<div class=\"card\" data-name=\"{name}\" data-owner=\"{owner}\">
  <h2>{name}</h2>
  <p>負責人：{owner}</p>
  <p>電話：{phone}</p>
  <p>地址：{address}</p>
  <a href=\"{link}\">前往診所頁面 →</a>
</div>
"""

DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{name}｜新竹市牙醫診所</title>
  <style>{style}</style>
</head>
<body>
  <header>
    <h1>{name}</h1>
    <p>{city}牙醫診所</p>
  </header>
  <main>
    <a class=\"back\" href=\"../index.html\">← 返回清單</a>
    <div class=\"info\">
      <h2>診所資訊</h2>
      <p class=\"meta\"><strong>負責人：</strong>{owner}</p>
      <p class=\"meta\"><strong>電話：</strong><a href=\"tel:{phone}\">{phone}</a></p>
      <p class=\"meta\"><strong>地址：</strong>{address}</p>
      <p class=\"meta\"><strong>地圖：</strong><a href=\"{map_link}\" target=\"_blank\" rel=\"noopener\">在地圖上開啟</a></p>
    </div>
  </main>
</body>
</html>
"""

def slugify(name: str, index: int) -> str:
    base = f"{index+1}-{name}"
    sanitized = re.sub(r"[^\w\u4e00-\u9fff-]", "-", base, flags=re.UNICODE)
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    return sanitized or f"clinic-{index+1}"

def load_clinics(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        clinics = []
        for idx, row in enumerate(reader):
            name = row.get("機構名稱", "").strip()
            owner = row.get("負責人", "").strip() or "—"
            phone = row.get("電話", "").strip() or "—"
            street = row.get("街道項弄號", "").strip()
            address = f"{CITY_NAME}{street}" if street else CITY_NAME
            clinics.append({
                "name": name,
                "owner": owner,
                "phone": phone,
                "address": address,
                "slug": slugify(name, idx),
            })
        return clinics

def render_detail(clinic):
    map_link = f"https://www.google.com/maps/search/{quote(clinic['address'])}"
    return DETAIL_TEMPLATE.format(
        style=STYLE,
        name=html.escape(clinic["name"] or "牙醫診所"),
        city=CITY_NAME,
        owner=html.escape(clinic["owner"]),
        phone=html.escape(clinic["phone"]),
        address=html.escape(clinic["address"]),
        map_link=map_link,
    )

def render_cards(clinics):
    cards = []
    for clinic in clinics:
        cards.append(CARD_TEMPLATE.format(
            name=html.escape(clinic["name"]),
            owner=html.escape(clinic["owner"]),
            phone=html.escape(clinic["phone"]),
            address=html.escape(clinic["address"]),
            link=f"clinics/{clinic['slug']}.html",
        ))
    return "\n".join(cards)

def render_index(clinics):
    return INDEX_TEMPLATE.format(style=STYLE, count=len(clinics), cards=render_cards(clinics))

def build_sites():
    clinics = load_clinics(CSV_PATH)
    DOCS_DIR.mkdir(exist_ok=True)
    CLINIC_DIR.mkdir(parents=True, exist_ok=True)

    index_html = render_index(clinics)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    for clinic in clinics:
        html_content = render_detail(clinic)
        (CLINIC_DIR / f"{clinic['slug']}.html").write_text(html_content, encoding="utf-8")

    print(f"生成完成：{len(clinics)} 個診所頁面")

if __name__ == "__main__":
    build_sites()
