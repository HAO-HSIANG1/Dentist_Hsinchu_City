import csv
import pathlib
import re
from html import escape

DATA_FILE = pathlib.Path('Dentist_Hsinchu_City.csv')
DOCS_DIR = pathlib.Path('docs')
CLINIC_DIR = DOCS_DIR / 'clinics'


def slugify(name: str) -> str:
    slug = re.sub(r'[^\w\-]+', '-', name)
    slug = re.sub(r'-+', '-', slug).strip('-').lower()
    return slug or 'clinic'


def build_head(title: str) -> str:
    return f"""<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{escape(title)}</title>
    <style>
        :root {{
            font-family: 'Noto Sans TC', 'Noto Sans', sans-serif;
            color: #1f2933;
            background: #f7f9fb;
        }}
        body {{
            margin: 0;
            padding: 0 1rem 2rem;
            line-height: 1.6;
        }}
        header {{
            background: #0f766e;
            color: white;
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
        }}
        h1, h2, h3 {{
            margin: 0;
            letter-spacing: 0.03em;
        }}
        a {{ color: #0f766e; }}
        a:hover {{ color: #0b5d57; }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 10px 25px rgba(15, 118, 110, 0.08);
            margin-bottom: 1rem;
        }}
        .clinic-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1rem;
        }}
        .label {{
            font-size: 0.9rem;
            color: #52606d;
            margin-right: 0.5rem;
        }}
        .value {{
            font-weight: 600;
        }}
        .breadcrumbs {{
            margin: 0.5rem 0 1rem;
            font-size: 0.95rem;
        }}
        footer {{
            margin-top: 2rem;
            color: #52606d;
            font-size: 0.9rem;
        }}
    </style>
</head>"""


def render_clinic_page(clinic: dict, index_slug: str) -> str:
    title = f"{clinic['機構名稱']} | 新竹市牙醫診所"
    address_parts = [clinic.get('街道項弄號', '').strip()]
    address = ''.join(part for part in address_parts if part)

    return f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
{build_head(title)}
<body>
    <header>
        <div class=\"breadcrumbs\"><a style=\"color: white; text-decoration: none;\" href=\"../index.html\">← 返回列表</a></div>
        <h1>{escape(clinic['機構名稱'])}</h1>
        <p>新竹市牙醫診所資訊</p>
    </header>
    <main>
        <section class=\"card\">
            <h2>診所資訊</h2>
            <p><span class=\"label\">地址：</span><span class=\"value\">{escape(address)}</span></p>
            <p><span class=\"label\">行政區域代碼：</span><span class=\"value\">{escape(clinic.get('行政區域代碼', ''))}</span></p>
            <p><span class=\"label\">縣市別代碼：</span><span class=\"value\">{escape(clinic.get('縣市別代碼', ''))}</span></p>
            <p><span class=\"label\">負責人：</span><span class=\"value\">{escape(clinic.get('負責人', ''))}</span></p>
            <p><span class=\"label\">聯絡電話：</span><span class=\"value\">{escape(clinic.get('電話', ''))}</span></p>
        </section>
    </main>
    <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
</body>
</html>"""


def render_index(clinics: list[dict]) -> str:
    title = "新竹市牙醫診所地圖"
    cards = []
    for clinic in clinics:
        cards.append(
            f"""<article class=\"card\">
                <h3><a href=\"clinics/{clinic['slug']}.html\">{escape(clinic['機構名稱'])}</a></h3>
                <p><span class=\"label\">地址：</span><span class=\"value\">{escape(clinic.get('街道項弄號', '').strip())}</span></p>
                <p><span class=\"label\">聯絡電話：</span><span class=\"value\">{escape(clinic.get('電話', ''))}</span></p>
            </article>"""
        )

    cards_markup = '\n'.join(cards)
    return f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
{build_head(title)}
<body>
    <header>
        <h1>新竹市牙醫診所列表</h1>
        <p>依據資料集自動生成的 GitHub Pages 網站，每個診所都有自己的頁面。</p>
    </header>
    <main>
        <section>
            <div class=\"clinic-grid\">
                {cards_markup}
            </div>
        </section>
    </main>
    <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
</body>
</html>"""


def ensure_directories() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    CLINIC_DIR.mkdir(parents=True, exist_ok=True)


def generate() -> None:
    ensure_directories()

    with DATA_FILE.open('r', encoding='utf-8-sig', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        clinics = []
        used_slugs = set()
        for row in reader:
            base_slug = slugify(row.get('機構名稱', ''))
            slug = base_slug
            counter = 2
            while slug in used_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            used_slugs.add(slug)
            row['slug'] = slug
            clinics.append(row)

    for clinic in clinics:
        page = render_clinic_page(clinic, 'index')
        file_path = CLINIC_DIR / f"{clinic['slug']}.html"
        file_path.write_text(page, encoding='utf-8')

    index_content = render_index(clinics)
    (DOCS_DIR / 'index.html').write_text(index_content, encoding='utf-8')


if __name__ == '__main__':
    generate()
