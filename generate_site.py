import csv
import html
import re
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
DATA_FILE = ROOT / 'Dentist_Hsinchu_City.csv'
OUTPUT_DIR = ROOT / 'docs'
ASSETS_DIR = OUTPUT_DIR / 'assets'
CLINICS_DIR = OUTPUT_DIR / 'clinics'

DISTRICT_MAP = {
    '10018010': '東區',
    '10018020': '北區',
    '10018030': '香山區',
}

PLACEHOLDER_IMAGE = 'assets/placeholder.svg'


def slugify(name: str) -> str:
    slug = re.sub(r'[^\w\-]+', '-', name.strip())
    slug = re.sub(r'-{2,}', '-', slug)
    return slug.strip('-').lower() or 'clinic'


def load_rows():
    with DATA_FILE.open('r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return list(reader)


def build_clinic_context(row):
    district_code = row.get('行政區域代碼', '').strip()
    district_name = DISTRICT_MAP.get(district_code, '未命名行政區')
    name = row.get('機構名稱', '').strip()
    address = row.get('街道項弄號', '').strip()
    phone = row.get('電話', '').strip()
    manager = row.get('負責人', '').strip()
    slug = slugify(name)
    map_query = quote_plus(f"{name} {address}")
    map_url = f"https://www.google.com/maps/search/?api=1&query={map_query}"
    return {
        'name': name,
        'district_code': district_code,
        'district_name': district_name,
        'address': address,
        'phone': phone,
        'manager': manager,
        'slug': slug,
        'map_url': map_url,
        'image': PLACEHOLDER_IMAGE,
        'rating': None,  # Google rating can be filled manually when available.
    }


def ensure_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)
    placeholder = ASSETS_DIR / 'placeholder.svg'
    if not placeholder.exists():
        placeholder.write_text(
            """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 360' role='img' aria-label='Clinic placeholder'>
  <defs>
    <linearGradient id='grad' x1='0%' y1='0%' x2='100%' y2='0%'>
      <stop offset='0%' style='stop-color:#7ed6df;stop-opacity:1' />
      <stop offset='100%' style='stop-color:#e056fd;stop-opacity:1' />
    </linearGradient>
  </defs>
  <rect width='600' height='360' rx='16' fill='url(#grad)' />
  <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='white' font-family='Arial, sans-serif' font-size='36'>牙醫診所</text>
</svg>""",
            encoding='utf-8',
        )

    stylesheet = ASSETS_DIR / 'style.css'
    if not stylesheet.exists():
        stylesheet.write_text(
            """:root {\n  --bg: #f6f7fb;\n  --card: #ffffff;\n  --text: #1e2a3a;\n  --muted: #4b5563;\n  --accent: #2563eb;\n  --accent-soft: #e0e7ff;\n  --border: #e5e7eb;\n}\n* { box-sizing: border-box; }\nbody {\n  margin: 0;\n  font-family: 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;\n  background: var(--bg);\n  color: var(--text);\n}\nheader {\n  background: linear-gradient(120deg, #1e40af, #3b82f6);\n  color: white;\n  padding: 48px 16px;\n  text-align: center;\n}\nheader h1 { margin: 0; font-size: 32px; }\nheader p { margin: 8px 0 0; color: #e5e7eb; }\nmain { padding: 24px 16px 64px; max-width: 1080px; margin: 0 auto; }\n.section-title { display: flex; align-items: center; gap: 12px; font-size: 22px; margin: 32px 0 12px; }\n.section-title span { background: var(--accent-soft); color: var(--accent); padding: 4px 10px; border-radius: 8px; font-weight: 700; }\n.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }\n.card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.06); transition: transform 0.15s ease, box-shadow 0.15s ease; display: flex; flex-direction: column; }\n.card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(0,0,0,0.08); }\n.card img { width: 100%; height: 160px; object-fit: cover; background: #e5e7eb; }\n.card-content { padding: 16px; display: flex; flex-direction: column; gap: 8px; flex: 1; }\n.card h3 { margin: 0; font-size: 18px; color: var(--text); }\n.meta { color: var(--muted); font-size: 14px; }\n.meta strong { color: var(--text); }\n.tags { display: flex; gap: 8px; flex-wrap: wrap; margin-top: auto; }\n.tag { background: var(--accent-soft); color: var(--accent); padding: 6px 10px; border-radius: 999px; font-size: 13px; }\na { color: var(--accent); text-decoration: none; }\na:hover { text-decoration: underline; }\n.footer { text-align: center; color: var(--muted); margin-top: 48px; font-size: 14px; }\n.details { max-width: 960px; margin: 0 auto; padding: 24px 16px 64px; }\n.hero { position: relative; }\n.hero img { width: 100%; height: 320px; object-fit: cover; border-radius: 18px; box-shadow: 0 12px 26px rgba(0,0,0,0.08); }\n.hero-info { position: absolute; bottom: 16px; left: 16px; background: rgba(0,0,0,0.55); color: white; padding: 12px 16px; border-radius: 12px; backdrop-filter: blur(3px); }\n.info-card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 16px; margin-top: 18px; box-shadow: 0 10px 24px rgba(0,0,0,0.06); }\n.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px,1fr)); gap: 12px; }\n.info-item { display: flex; gap: 8px; align-items: center; color: var(--muted); }\n.info-item strong { color: var(--text); min-width: 64px; }\n.actions { margin-top: 16px; display: flex; gap: 12px; flex-wrap: wrap; }\n.btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border); background: var(--accent); color: white; font-weight: 600; box-shadow: 0 10px 20px rgba(37,99,235,0.25); transition: transform 0.1s ease; }\n.btn:hover { transform: translateY(-2px); text-decoration: none; }\n.breadcrumb { margin: 20px 0 8px; color: var(--muted); font-size: 14px; }\n.rating { display: flex; align-items: center; gap: 6px; color: #f59e0b; font-weight: 700; }\n.star { width: 18px; height: 18px; color: #fbbf24; }\n@media (max-width: 640px) { header { padding: 36px 14px; } header h1 { font-size: 26px; } .hero img { height: 240px; } }\n""",
            encoding='utf-8',
        )


def render_rating(rating):
    if rating is None:
        return "<div class='rating' aria-label='Google rating unavailable'>Google 星等：暫無資料</div>"
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    stars = "".join("<span class='star'>★</span>" for _ in range(full_stars))
    if half_star:
        stars += "<span class='star'>☆</span>"
    return f"<div class='rating' aria-label='Google rating {rating}'>Google 星等：{rating:.1f} {stars}</div>"


def render_index(grouped):
    sections = []
    for district, clinics in grouped.items():
        cards = []
        for clinic in clinics:
            cards.append(
                f"""
                <article class='card'>
                  <img src='{clinic['image']}' alt='{html.escape(clinic['name'])} 封面照'>
                  <div class='card-content'>
                    <h3><a href='clinics/{clinic['slug']}.html'>{html.escape(clinic['name'])}</a></h3>
                    <div class='meta'><strong>地址：</strong>{html.escape(clinic['address'])}</div>
                    <div class='meta'><strong>電話：</strong>{html.escape(clinic['phone'])}</div>
                    <div class='meta'>{render_rating(clinic['rating'])}</div>
                    <div class='tags'>
                      <span class='tag'>{html.escape(clinic['district_name'])}</span>
                      <a class='tag' href='{clinic['map_url']}' target='_blank' rel='noopener'>Google 地圖</a>
                    </div>
                  </div>
                </article>
                """
            )
        sections.append(
            f"""
            <section>
              <div class='section-title'><span>{html.escape(district)}</span><div>社區診所列表</div></div>
              <div class='grid'>
                {''.join(cards)}
              </div>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang='zh-Hant'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>新竹市牙醫診所地圖</title>
  <link rel='stylesheet' href='assets/style.css'>
</head>
<body>
  <header>
    <h1>新竹市牙醫診所地圖</h1>
    <p>按行政區瀏覽牙醫診所，一鍵查看封面照、Google 地圖與聯絡資訊。</p>
  </header>
  <main>
    {''.join(sections)}
    <div class='footer'>資料來源：Dentist_Hsinchu_City.csv（更新時間請依資料檔為準）。</div>
  </main>
</body>
</html>
"""


def render_clinic_page(clinic):
    return f"""<!doctype html>
<html lang='zh-Hant'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{html.escape(clinic['name'])} | 新竹市牙醫診所</title>
  <link rel='stylesheet' href='../assets/style.css'>
</head>
<body>
  <main class='details'>
    <div class='breadcrumb'><a href='../index.html'>← 返回首頁</a> / {html.escape(clinic['district_name'])}</div>
    <div class='hero'>
      <img src='../{clinic['image']}' alt='{html.escape(clinic['name'])} 封面照'>
      <div class='hero-info'>
        <div>{html.escape(clinic['district_name'])}</div>
        <h1 style='margin:6px 0 0;'>{html.escape(clinic['name'])}</h1>
      </div>
    </div>
    <div class='info-card'>
      {render_rating(clinic['rating'])}
      <div class='info-grid'>
        <div class='info-item'><strong>地址</strong><span>{html.escape(clinic['address'])}</span></div>
        <div class='info-item'><strong>電話</strong><span>{html.escape(clinic['phone'])}</span></div>
        <div class='info-item'><strong>負責人</strong><span>{html.escape(clinic['manager'])}</span></div>
      </div>
      <div class='actions'>
        <a class='btn' href='{clinic['map_url']}' target='_blank' rel='noopener'>📍 在 Google 地圖上查看</a>
      </div>
    </div>
  </main>
</body>
</html>
"""


def main():
    ensure_assets()
    clinics = [build_clinic_context(r) for r in load_rows()]
    grouped = {}
    for clinic in clinics:
        grouped.setdefault(clinic['district_name'], []).append(clinic)

    for district_clinics in grouped.values():
        district_clinics.sort(key=lambda x: x['name'])

    index_html = render_index(grouped)
    (OUTPUT_DIR / 'index.html').write_text(index_html, encoding='utf-8')

    for clinic in clinics:
        clinic_html = render_clinic_page(clinic)
        (CLINICS_DIR / f"{clinic['slug']}.html").write_text(clinic_html, encoding='utf-8')

    print(f"Generated {len(clinics)} clinic pages and index at {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
