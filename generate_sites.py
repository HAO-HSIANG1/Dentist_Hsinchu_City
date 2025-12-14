import csv
from pathlib import Path
from typing import Dict, List

DATA_FILE = Path('Dentist_Hsinchu_City.csv')
OUTPUT_DIR = Path('docs')
CLINICS_DIR = OUTPUT_DIR / 'clinics'

BASE_STYLES = """
/* Base styling for generated clinic pages */
:root {
    --primary: #1e90ff;
    --text-main: #1a1a1a;
    --muted: #4b5563;
    --card-bg: #ffffff;
    --bg: #f4f7fb;
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', 'Noto Sans TC', sans-serif;
    margin: 0;
    background: var(--bg);
    color: var(--text-main);
}

a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

header {
    background: #0f172a;
    color: #f8fafc;
    padding: 24px 16px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.16);
}

main {
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 16px 48px;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
}

.card {
    background: var(--card-bg);
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}

.card h2 {
    margin: 0 0 8px;
    font-size: 1.1rem;
}

.meta {
    margin: 6px 0;
    color: var(--muted);
    font-size: 0.95rem;
}

.tag {
    display: inline-block;
    padding: 4px 8px;
    background: #e0f2fe;
    color: #075985;
    border-radius: 999px;
    font-size: 0.85rem;
    margin-right: 8px;
}

.search {
    margin: 16px 0 24px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.search input {
    flex: 1;
    padding: 12px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    font-size: 1rem;
}

.section {
    margin-top: 16px;
    padding: 16px;
    background: #eef2ff;
    border-radius: 10px;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px 20px;
    margin-top: 12px;
}

.detail-item {
    background: #fff;
    padding: 12px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.06);
}

.footer {
    text-align: center;
    margin-top: 32px;
    color: var(--muted);
    font-size: 0.95rem;
}
"""


def read_clinics() -> List[Dict[str, str]]:
    with DATA_FILE.open('r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def clinic_slug(index: int) -> str:
    return f"clinic-{index + 1:03d}"


def write_stylesheet():
    OUTPUT_DIR.mkdir(exist_ok=True)
    styles_path = OUTPUT_DIR / 'styles.css'
    styles_path.write_text(BASE_STYLES, encoding='utf-8')


def render_index(clinics: List[Dict[str, str]]):
    cards_html = []
    for idx, clinic in enumerate(clinics):
        slug = clinic_slug(idx)
        cards_html.append(
            """
            <article class='card' data-name="{name}" data-area="{area}">
                <div class='tag'>#{number}</div>
                <h2><a href='clinics/{slug}.html'>{name}</a></h2>
                <div class='meta'>負責人：{owner}</div>
                <div class='meta'>電話：<a href='tel:{phone}'>{phone}</a></div>
                <div class='meta'>地點：{address}</div>
            </article>
            """.format(
                name=clinic['機構名稱'],
                area=clinic['行政區域代碼'],
                number=idx + 1,
                slug=slug,
                owner=clinic['負責人'],
                phone=clinic['電話'],
                address=clinic['街道項弄號'],
            )
        )

    content = f"""
    <!doctype html>
    <html lang='zh-Hant'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>新竹市牙醫診所總覽</title>
        <link rel='stylesheet' href='styles.css'>
        <style>
        .empty {{ display: none; text-align: center; padding: 12px; color: var(--muted); }}
        </style>
    </head>
    <body>
        <header>
            <h1>新竹市牙醫診所總覽</h1>
            <p>從 CSV 自動生成的 GitHub Pages：為每間牙醫診所建立獨立頁面</p>
        </header>
        <main>
            <section class='search'>
                <input id='search' type='search' placeholder='輸入診所名稱或行政區域代碼快速篩選'>
            </section>
            <section class='card-grid' id='clinic-list'>
                {''.join(cards_html)}
            </section>
            <p id='empty' class='empty'>找不到符合條件的診所</p>
            <div class='footer'>資料來源：Dentist_Hsinchu_City.csv</div>
        </main>
        <script>
        const searchInput = document.getElementById('search');
        const cards = Array.from(document.querySelectorAll('#clinic-list .card'));
        const empty = document.getElementById('empty');
        function normalize(text) {{ return text.toLowerCase(); }}
        function filter() {{
            const term = normalize(searchInput.value.trim());
            let visible = 0;
            cards.forEach(card => {{
                const name = normalize(card.dataset.name || '');
                const area = normalize(card.dataset.area || '');
                const match = !term || name.includes(term) || area.includes(term);
                card.style.display = match ? '' : 'none';
                if (match) visible++;
            }});
            empty.style.display = visible ? 'none' : 'block';
        }}
        searchInput.addEventListener('input', filter);
        </script>
    </body>
    </html>
    """
    (OUTPUT_DIR / 'index.html').write_text(content, encoding='utf-8')


def render_clinic_pages(clinics: List[Dict[str, str]]):
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)
    for idx, clinic in enumerate(clinics):
        slug = clinic_slug(idx)
        content = f"""
        <!doctype html>
        <html lang='zh-Hant'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>{clinic['機構名稱']}｜新竹市牙醫診所</title>
            <link rel='stylesheet' href='../styles.css'>
        </head>
        <body>
            <header>
                <h1>{clinic['機構名稱']}</h1>
                <p>新竹市牙醫診所專屬頁面</p>
            </header>
            <main>
                <div class='section'>
                    <div class='detail-grid'>
                        <div class='detail-item'><strong>負責人</strong><br>{clinic['負責人']}</div>
                        <div class='detail-item'><strong>電話</strong><br><a href='tel:{clinic['電話']}'>{clinic['電話']}</a></div>
                        <div class='detail-item'><strong>縣市別代碼</strong><br>{clinic['縣市別代碼']}</div>
                        <div class='detail-item'><strong>行政區域代碼</strong><br>{clinic['行政區域代碼']}</div>
                        <div class='detail-item'><strong>地址</strong><br>{clinic['街道項弄號']}</div>
                    </div>
                </div>
                <p class='footer'><a href='../index.html'>回診所清單</a></p>
            </main>
        </body>
        </html>
        """
        (CLINICS_DIR / f"{slug}.html").write_text(content, encoding='utf-8')


def main():
    clinics = read_clinics()
    write_stylesheet()
    render_index(clinics)
    render_clinic_pages(clinics)
    print(f"Generated {len(clinics)} clinic pages into {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
