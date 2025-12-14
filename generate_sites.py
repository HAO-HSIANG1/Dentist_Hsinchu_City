from __future__ import annotations
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "Dentist_Hsinchu_City.csv"
DOCS_DIR = ROOT / "docs"
CLINICS_DIR = DOCS_DIR / "clinics"


def ensure_directories() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)


def load_rows():
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csvfile:
        return list(csv.DictReader(csvfile))


def clinic_slug(index: int) -> str:
    return f"clinic-{index:03d}.html"


def render_index(rows) -> str:
    cards = []
    for idx, row in enumerate(rows, start=1):
        slug = clinic_slug(idx)
        name = html.escape(row["機構名稱"])
        manager = html.escape(row["負責人"])
        address = html.escape(row["街道項弄號"])
        phone = html.escape(row["電話"])
        cards.append(
            f"""
            <article class=\"card\" data-name=\"{name}\" data-manager=\"{manager}\" data-address=\"{address}\" data-phone=\"{phone}\">
                <header>
                    <h2><a href=\"clinics/{slug}\">{name}</a></h2>
                    <p class=\"manager\">負責人：{manager}</p>
                </header>
                <p class=\"address\">地址：{address}</p>
                <p class=\"phone\">電話：{phone}</p>
                <a class=\"cta\" href=\"clinics/{slug}\">查看診所網站</a>
            </article>
            """
        )

    return f"""
    <!doctype html>
    <html lang=\"zh-Hant\">
    <head>
        <meta charset=\"utf-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <title>新竹市牙醫診所列表</title>
        <style>
            :root {{
                --bg: #f9fafb;
                --card: #ffffff;
                --primary: #1f6feb;
                --text: #0f172a;
                --muted: #475569;
                --border: #e2e8f0;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                font-family: 'Noto Sans TC', 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: var(--bg);
                color: var(--text);
            }}
            header.page-header {{
                padding: 2rem 1.25rem 1rem;
                text-align: center;
                background: linear-gradient(135deg, #e0f2fe, #eff6ff);
                border-bottom: 1px solid var(--border);
            }}
            header.page-header h1 {{ margin: 0 0 .5rem; font-size: clamp(1.75rem, 2vw + 1rem, 2.4rem); }}
            header.page-header p {{ margin: 0 auto; max-width: 720px; color: var(--muted); line-height: 1.5; }}
            main {{ max-width: 1200px; margin: 0 auto; padding: 1.5rem; }}
            .search {{ display: flex; gap: .75rem; flex-wrap: wrap; margin-bottom: 1.5rem; align-items: center; }}
            .search input {{ flex: 1 1 240px; padding: .85rem 1rem; border-radius: .75rem; border: 1px solid var(--border); font-size: 1rem; }}
            .search small {{ color: var(--muted); }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }}
            .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 1rem; padding: 1rem 1.1rem; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05); display: flex; flex-direction: column; gap: .35rem; }}
            .card h2 {{ margin: 0; font-size: 1.2rem; }}
            .card a {{ color: var(--primary); text-decoration: none; }}
            .card .manager, .card .address, .card .phone {{ margin: 0; color: var(--muted); line-height: 1.4; }}
            .cta {{ margin-top: .35rem; align-self: flex-start; font-weight: 600; }}
            footer {{ text-align: center; color: var(--muted); padding: 2rem 1rem; font-size: .95rem; }}
        </style>
    </head>
    <body>
        <header class=\"page-header\">
            <h1>新竹市牙醫診所專屬網站</h1>
            <p>從 CSV 資料自動產生的靜態網站。點擊任一診所即可進入其專屬頁面，查看負責人、地址與聯絡方式。</p>
        </header>
        <main>
            <div class=\"search\">
                <input id=\"search\" type=\"search\" placeholder=\"搜尋診所名稱、負責人、地址或電話\" aria-label=\"搜尋\">
                <small>共 {len(rows)} 間診所</small>
            </div>
            <section class=\"grid\" id=\"cards\">
                {''.join(cards)}
            </section>
        </main>
        <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
        <script>
            const searchInput = document.getElementById('search');
            const cards = Array.from(document.querySelectorAll('.card'));
            searchInput.addEventListener('input', () => {{
                const keyword = searchInput.value.trim().toLowerCase();
                cards.forEach(card => {{
                    const content = [
                        card.dataset.name,
                        card.dataset.manager,
                        card.dataset.address,
                        card.dataset.phone,
                    ].join(' ').toLowerCase();
                    const matched = content.includes(keyword);
                    card.style.display = matched ? 'flex' : 'none';
                }});
            }});
        </script>
    </body>
    </html>
    """


def render_clinic_page(idx: int, row) -> str:
    name = html.escape(row["機構名稱"])
    manager = html.escape(row["負責人"])
    address = html.escape(row["街道項弄號"])
    city_code = html.escape(row["縣市別代碼"])
    district_code = html.escape(row["行政區域代碼"])
    phone = html.escape(row["電話"])
    return f"""
    <!doctype html>
    <html lang=\"zh-Hant\">
    <head>
        <meta charset=\"utf-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <title>{name}｜新竹市牙醫診所</title>
        <style>
            body {{
                margin: 0;
                font-family: 'Noto Sans TC', 'Segoe UI', system-ui, -apple-system, sans-serif;
                background: #f8fafc;
                color: #0f172a;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1.5rem;
            }}
            .card {{
                background: #fff;
                border: 1px solid #e2e8f0;
                border-radius: 1.25rem;
                max-width: 720px;
                width: min(720px, 100%);
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
                overflow: hidden;
            }}
            .hero {{
                background: linear-gradient(120deg, #c7d2fe, #dbeafe);
                padding: 1.25rem 1.5rem 1rem;
                color: #111827;
            }}
            .hero h1 {{ margin: 0 0 .35rem; font-size: 1.75rem; }}
            .hero p {{ margin: 0; color: #1f2937; }}
            .content {{ padding: 1.5rem; display: grid; gap: 1rem; }}
            .info {{ display: grid; gap: .5rem; }}
            .info p {{ margin: 0; font-size: 1.05rem; color: #334155; }}
            .label {{ display: inline-block; padding: .35rem .65rem; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: .9rem; font-weight: 600; }}
            .actions {{ display: flex; gap: .75rem; flex-wrap: wrap; }}
            .btn {{
                display: inline-flex;
                align-items: center;
                gap: .45rem;
                padding: .85rem 1rem;
                border-radius: .9rem;
                text-decoration: none;
                font-weight: 700;
                border: 1px solid #cbd5e1;
                color: #1d4ed8;
                background: #fff;
                transition: transform .15s ease, box-shadow .15s ease;
            }}
            .btn:hover {{
                transform: translateY(-1px);
                box-shadow: 0 12px 25px rgba(59, 130, 246, 0.15);
            }}
            .footer {{ padding: 1.25rem 1.5rem 1.5rem; border-top: 1px solid #e2e8f0; color: #64748b; font-size: .95rem; }}
        </style>
    </head>
    <body>
        <article class=\"card\">
            <section class=\"hero\">
                <p class=\"label\">牙醫診所 #{idx:03d}</p>
                <h1>{name}</h1>
                <p>位於新竹市，為您提供牙科醫療服務。</p>
            </section>
            <section class=\"content\">
                <div class=\"info\">
                    <p><strong>負責人：</strong>{manager}</p>
                    <p><strong>地址：</strong>{address}</p>
                    <p><strong>縣市代碼：</strong>{city_code}</p>
                    <p><strong>行政區代碼：</strong>{district_code}</p>
                    <p><strong>電話：</strong>{phone}</p>
                </div>
                <div class=\"actions\">
                    <a class=\"btn\" href=\"tel:{phone}\">📞 立即撥打</a>
                    <a class=\"btn\" href=\"../index.html\">⬅️ 返回診所列表</a>
                </div>
            </section>
            <section class=\"footer\">資料來源：Dentist_Hsinchu_City.csv</section>
        </article>
    </body>
    </html>
    """


def build():
    ensure_directories()
    rows = load_rows()
    (DOCS_DIR / "index.html").write_text(render_index(rows), encoding="utf-8")
    for idx, row in enumerate(rows, start=1):
        html_path = CLINICS_DIR / clinic_slug(idx)
        html_path.write_text(render_clinic_page(idx, row), encoding="utf-8")


if __name__ == "__main__":
    build()
