import csv
import html
import os
import pathlib
import urllib.parse
from collections import defaultdict

CSV_PATH = pathlib.Path('Dentist_Hsinchu_City.csv')
OUTPUT_ROOT = pathlib.Path('.')
ASSET_DIR = OUTPUT_ROOT / 'assets'
CLINIC_DIR = OUTPUT_ROOT / 'clinics'

ASSET_DIR.mkdir(exist_ok=True)
CLINIC_DIR.mkdir(exist_ok=True)

STYLE_PATH = ASSET_DIR / 'style.css'
if not STYLE_PATH.exists():
    STYLE_PATH.write_text(
        """
:root {
    --bg: #f6f8fb;
    --card: #ffffff;
    --primary: #1c6dd0;
    --accent: #f7b731;
    --text: #1f2937;
    --muted: #4b5563;
    --shadow: 0 10px 30px rgba(0,0,0,0.08);
}

* { box-sizing: border-box; }
body {
    font-family: 'Noto Sans TC', 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(180deg, #f8fbff 0%, #eef3fa 100%);
    margin: 0;
    color: var(--text);
}
header {
    background: #0f172a;
    color: white;
    padding: 24px 20px 32px;
    box-shadow: var(--shadow);
}
header h1 { margin: 0; font-size: 28px; }
header p { margin: 6px 0 0; color: #cbd5f5; }

main { padding: 24px 20px 60px; max-width: 1200px; margin: 0 auto; }

.community {
    margin-bottom: 32px;
}
.community h2 {
    margin: 0 0 12px;
    font-size: 22px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.community h2 span {
    background: rgba(28,109,208,0.1);
    color: var(--primary);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 14px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
}
.card {
    background: var(--card);
    border-radius: 12px;
    padding: 16px;
    box-shadow: var(--shadow);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 36px rgba(0,0,0,0.12);
}
.card h3 { margin: 0 0 8px; font-size: 18px; }
.card .meta { color: var(--muted); font-size: 14px; margin: 4px 0; }

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(247, 183, 49, 0.16);
    color: #d97706;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 14px;
    margin-top: 6px;
}

.actions { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
.actions a {
    text-decoration: none;
    padding: 8px 12px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
.actions a.primary {
    background: var(--primary);
    color: white;
}
.actions a.secondary {
    background: #e2e8f0;
    color: #1f2937;
}
.icon {
    width: 18px;
    height: 18px;
}

.detail-hero {
    background: #0f172a;
    color: white;
    padding: 36px 20px;
}
.detail-hero h1 { margin: 0 0 8px; }
.detail-hero p { margin: 6px 0 0; color: #cbd5f5; }
.detail-body {
    max-width: 860px;
    margin: 0 auto;
    padding: 28px 20px 60px;
}
.info-card {
    background: var(--card);
    border-radius: 14px;
    padding: 20px;
    box-shadow: var(--shadow);
}
.info-row { display: grid; grid-template-columns: 120px 1fr; gap: 10px; margin: 10px 0; }
.info-label { font-weight: 700; color: var(--muted); }
.rating {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(247, 183, 49, 0.16);
    color: #d97706;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 700;
    margin-top: 12px;
}
.note {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #92400e;
    border-radius: 10px;
    padding: 10px 12px;
    margin-top: 10px;
}

.back-link { display: inline-flex; align-items: center; gap: 8px; color: var(--primary); font-weight: 700; text-decoration: none; }

footer { text-align: center; color: var(--muted); padding: 24px 0 40px; font-size: 14px; }
""",
        encoding='utf-8'
    )

def read_clinics():
    clinics = []
    with CSV_PATH.open(encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            address = row['街道項弄號'].strip()
            community = '未標註社區'
            if '里' in address:
                before, _, _ = address.partition('里')
                community_candidate = (before + '里').strip()
                if community_candidate:
                    community = community_candidate
            slug = f"clinic-{idx:03d}"
            clinics.append({
                'id': idx,
                'slug': slug,
                'name': row['機構名稱'].strip(),
                'city_code': row['縣市別代碼'].strip(),
                'area_code': row['行政區域代碼'].strip(),
                'address': address,
                'director': row['負責人'].strip(),
                'phone': row['電話'].strip(),
                'community': community,
            })
    return clinics


def map_link(name, address):
    query = urllib.parse.quote_plus(f"{name} {address} 新竹市 牙醫")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def cover_image(slug: str) -> str:
    """Return a deterministic cover image for a clinic page."""

    seed = urllib.parse.quote_plus(slug)
    return f"https://picsum.photos/seed/{seed}/900/480"


def rating_display(clinic):
    """Create a friendly (illustrative) Google rating string.

    We do not have live ratings locally, so we provide a deterministic,
    easy-to-read placeholder to remind users to verify on Google Maps.
    """

    base = 3.6
    span = 1.4
    score = min(5.0, base + (clinic['id'] * 0.27) % span)
    return f"{score:.1f} / 5.0（示意）"


def star_badge(text="請至 Google 地圖查看最新評分"):
    return f"<span class='badge'>\u2b50 Google 星星數：{html.escape(text)}</span>"


def build_index(clinics):
    by_community = defaultdict(list)
    for clinic in clinics:
        by_community[clinic['community']].append(clinic)
    for lst in by_community.values():
        lst.sort(key=lambda c: c['name'])

    community_blocks = []
    for community in sorted(by_community):
        cards = []
        for clinic in by_community[community]:
            gmap = map_link(clinic['name'], clinic['address'])
            cards.append(
                f"""
                <article class='card'>
                    <div class='card-cover' style="background-image: url('{cover_image(clinic['slug'])}');"></div>
                    <h3>{html.escape(clinic['name'])}</h3>
                    <div class='meta'>社區：{html.escape(clinic['community'])}</div>
                    <div class='meta'>地址：{html.escape(clinic['address'])}</div>
                    {star_badge(rating_display(clinic))}
                    <div class='actions'>
                        <a class='primary' href='clinics/{clinic['slug']}.html'>查看診所頁面</a>
                        <a class='secondary' href='{gmap}' target='_blank' rel='noopener'>
                            <svg class='icon' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
                                <path d='M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 1 1 18 0Z'/>
                                <circle cx='12' cy='10' r='3'/>
                            </svg>
                            Google 地圖
                        </a>
                    </div>
                </article>
                """
            )
        community_blocks.append(
            f"""
            <section class='community'>
                <h2>{html.escape(community)} <span>{len(by_community[community])} 家</span></h2>
                <div class='grid'>
                    {''.join(cards)}
                </div>
            </section>
            """
        )

    index_html = f"""
    <!doctype html>
    <html lang='zh-Hant'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>新竹市牙醫診所地圖 | GitHub Pages</title>
        <link rel='stylesheet' href='assets/style.css'>
        <link rel='preconnect' href='https://fonts.googleapis.com'>
        <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
        <link href='https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap' rel='stylesheet'>
    </head>
    <body>
        <header>
            <h1>新竹市牙醫診所地圖</h1>
            <p>依社區名稱分類，一鍵查看診所資訊與 Google 地圖</p>
        </header>
        <main>
            {''.join(community_blocks)}
        </main>
        <footer>資料來源：Dentist_Hsinchu_City.csv。Google 星等以地圖資訊為準。</footer>
    </body>
    </html>
    """

    (OUTPUT_ROOT / 'index.html').write_text(index_html, encoding='utf-8')


def build_detail(clinic):
    gmap = map_link(clinic['name'], clinic['address'])
    detail_html = f"""
    <!doctype html>
    <html lang='zh-Hant'>
    <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>{html.escape(clinic['name'])} | 新竹市牙醫診所</title>
        <link rel='stylesheet' href='../assets/style.css'>
        <link rel='preconnect' href='https://fonts.googleapis.com'>
        <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
        <link href='https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap' rel='stylesheet'>
    </head>
    <body>
        <div class='detail-hero'>
            <a class='back-link' href='../index.html'>&larr; 返回總覽</a>
            <h1>{html.escape(clinic['name'])}</h1>
            <p>{html.escape(clinic['community'])} · 牙醫診所</p>
        </div>
        <div class='detail-body'>
            <div class='detail-cover' style="background-image: url('{cover_image(clinic['slug'])}');"></div>
            <div class='info-card'>
                <div class='info-row'><div class='info-label'>社區</div><div>{html.escape(clinic['community'])}</div></div>
                <div class='info-row'><div class='info-label'>地址</div><div>{html.escape(clinic['address'])}</div></div>
                <div class='info-row'><div class='info-label'>負責人</div><div>{html.escape(clinic['director'])}</div></div>
                <div class='info-row'><div class='info-label'>電話</div><div>{html.escape(clinic['phone'])}</div></div>
                <div class='rating'>\u2b50 Google 星星數：{html.escape(rating_display(clinic))}</div>
                <div class='note'>星等為示意值，實際評分以 Google 地圖顯示為準。</div>
                <div class='actions' style='margin-top:14px;'>
                    <a class='primary' href='{gmap}' target='_blank' rel='noopener'>
                        <svg class='icon' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
                            <path d='M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 1 1 18 0Z'/>
                            <circle cx='12' cy='10' r='3'/>
                        </svg>
                        開啟 Google 地圖
                    </a>
                    <a class='secondary' href='../index.html'>返回列表</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    (CLINIC_DIR / f"{clinic['slug']}.html").write_text(detail_html, encoding='utf-8')


def main():
    clinics = read_clinics()
    build_index(clinics)
    for clinic in clinics:
        build_detail(clinic)


if __name__ == '__main__':
    main()
