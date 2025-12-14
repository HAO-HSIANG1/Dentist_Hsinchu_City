import csv
import os
import re
from pathlib import Path

CSV_PATH = Path('Dentist_Hsinchu_City.csv')
OUTPUT_DIR = Path('.')
DETAIL_DIR = OUTPUT_DIR / 'clinics'

def slugify(name: str, fallback: str) -> str:
    slug = re.sub(r'[^\w\-]+', '-', name, flags=re.UNICODE).strip('-').lower()
    slug = re.sub(r'-{2,}', '-', slug)
    if not slug:
        return fallback
    return slug

def ensure_dirs():
    DETAIL_DIR.mkdir(exist_ok=True)

def read_clinics():
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_index(clinics):
    cards = []
    for idx, clinic in enumerate(clinics, start=1):
        slug = slugify(clinic['機構名稱'], f'clinic-{idx}')
        detail_path = f"clinics/{slug}.html"
        cards.append(f"""
            <article class='card'>
                <header>
                    <h3>{clinic['機構名稱']}</h3>
                    <p class='meta'>負責人：{clinic['負責人']} · 電話：{clinic['電話']}</p>
                </header>
                <p class='address'>地址：{clinic['街道項弄號']}</p>
                <a class='button' href='{detail_path}'>查看網站</a>
            </article>
        """)
    cards_html = "\n".join(cards)
    template = f"""<!DOCTYPE html>
<html lang='zh-Hant'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>新竹市牙醫診所總覽</title>
  <link rel='preconnect' href='https://fonts.googleapis.com'>
  <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
  <link href='https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap' rel='stylesheet'>
  <style>
    :root {{
      --primary: #2a7cbb;
      --bg: #f5f7fb;
      --card-bg: #fff;
      --shadow: 0 15px 40px rgba(31, 41, 55, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Noto Sans TC', sans-serif; background: var(--bg); color: #1f2937; }}
    header.hero {{ padding: 3rem 1rem; text-align: center; background: linear-gradient(135deg, #1e3a8a, #38bdf8); color: #fff; }}
    header.hero h1 {{ margin: 0 0 0.75rem; font-size: clamp(1.8rem, 3vw, 2.6rem); }}
    header.hero p {{ margin: 0; font-size: 1rem; opacity: 0.92; }}
    main {{ max-width: 1100px; margin: -2rem auto 3rem; padding: 0 1rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
    .card {{ background: var(--card-bg); border-radius: 16px; padding: 1.25rem; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 0.5rem; }}
    .card h3 {{ margin: 0; font-size: 1.2rem; }}
    .meta {{ margin: 0; color: #4b5563; font-size: 0.9rem; }}
    .address {{ margin: 0; color: #111827; font-weight: 500; }}
    .button {{ align-self: flex-start; padding: 0.6rem 1rem; background: var(--primary); color: #fff; border-radius: 10px; text-decoration: none; font-weight: 700; transition: transform 0.2s ease, box-shadow 0.2s ease; }}
    .button:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(42, 124, 187, 0.35); }}
  </style>
</head>
<body>
  <header class='hero'>
    <h1>新竹市牙醫診所清單</h1>
    <p>為每間診所建立專屬頁面，輕鬆找到位置與聯絡方式。</p>
  </header>
  <main>
    <section class='grid'>
      {cards_html}
    </section>
  </main>
</body>
</html>
"""
    (OUTPUT_DIR / 'index.html').write_text(template, encoding='utf-8')

def write_detail_pages(clinics):
    for idx, clinic in enumerate(clinics, start=1):
        slug = slugify(clinic['機構名稱'], f'clinic-{idx}')
        filename = DETAIL_DIR / f"{slug}.html"
        address = clinic['街道項弄號']
        map_query = f"{clinic['機構名稱']} {address} 新竹市"
        phone_link = re.sub(r"[\s()-]+", "", clinic['電話'])
        html = f"""<!DOCTYPE html>
<html lang='zh-Hant'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{clinic['機構名稱']}｜新竹市牙醫診所</title>
  <link rel='preconnect' href='https://fonts.googleapis.com'>
  <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
  <link href='https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap' rel='stylesheet'>
  <style>
    :root {{ --primary: #1e3a8a; --accent: #38bdf8; --bg: #f5f7fb; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Noto Sans TC', sans-serif; background: var(--bg); color: #111827; }}
    .hero {{ padding: 2.5rem 1.25rem 2rem; background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff; text-align: center; }}
    .hero h1 {{ margin: 0 0 0.4rem; font-size: clamp(1.8rem, 3vw, 2.5rem); }}
    .hero p {{ margin: 0; opacity: 0.9; }}
    main {{ max-width: 900px; margin: -1.5rem auto 2.5rem; padding: 0 1.25rem; }}
    .card {{ background: #fff; border-radius: 16px; padding: 1.5rem; box-shadow: 0 15px 40px rgba(31,41,55,0.1); margin-bottom: 1rem; }}
    .section-title {{ margin: 0 0 0.75rem; font-size: 1.1rem; color: #1f2937; }}
    .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.75rem; }}
    .info {{ background: #f1f5f9; border-radius: 12px; padding: 0.9rem; }}
    .info span {{ display: block; font-size: 0.85rem; color: #6b7280; margin-bottom: 0.35rem; }}
    .info strong {{ font-size: 1.02rem; color: #0f172a; }}
    .actions {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem; }}
    .button {{ padding: 0.7rem 1.1rem; border-radius: 10px; text-decoration: none; font-weight: 700; color: #fff; background: #2563eb; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.35); transition: transform 0.15s ease, box-shadow 0.15s ease; }}
    .button.secondary {{ background: #0ea5e9; box-shadow: 0 10px 25px rgba(14,165,233,0.35); }}
    .button:hover {{ transform: translateY(-2px); }}
    footer {{ text-align: center; padding: 1.2rem; color: #4b5563; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <header class='hero'>
    <h1>{clinic['機構名稱']}</h1>
    <p>專屬資訊頁面 · 新竹市牙醫診所</p>
  </header>
  <main>
    <section class='card'>
      <h2 class='section-title'>診所資訊</h2>
      <div class='info-grid'>
        <div class='info'><span>負責人</span><strong>{clinic['負責人']}</strong></div>
        <div class='info'><span>聯絡電話</span><strong>{clinic['電話']}</strong></div>
        <div class='info'><span>行政區域代碼</span><strong>{clinic['行政區域代碼']}</strong></div>
        <div class='info'><span>縣市代碼</span><strong>{clinic['縣市別代碼']}</strong></div>
      </div>
      <div class='info' style='margin-top: 1rem;'>
        <span>地址</span><strong>{address}</strong>
      </div>
      <div class='actions'>
        <a class='button' href='tel:{phone_link}'>撥打電話</a>
        <a class='button secondary' href='https://www.google.com/maps/search/{map_query}' target='_blank' rel='noopener'>在 Google 地圖查看</a>
        <a class='button' style='background:#111827' href='../index.html'>返回列表</a>
      </div>
    </section>
  </main>
  <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
</body>
</html>
"""
        filename.write_text(html, encoding='utf-8')

def main():
    ensure_dirs()
    clinics = read_clinics()
    write_index(clinics)
    write_detail_pages(clinics)
    print(f"Generated {len(clinics)} pages")

if __name__ == '__main__':
    main()
