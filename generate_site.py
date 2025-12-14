import csv
import html
import re
from pathlib import Path

DATA_FILE = Path("Dentist_Hsinchu_City.csv")
OUTPUT_DIR = Path("docs")


def load_clinics():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"找不到資料檔案: {DATA_FILE}")

    with DATA_FILE.open(newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        clinics = []
        for index, row in enumerate(reader, start=1):
            name = row.get("機構名稱") or row.get("\ufeff機構名稱") or "未知牙醫診所"
            clinic = {
                "name": name.strip(),
                "city_code": (row.get("縣市別代碼") or "").strip(),
                "district_code": (row.get("行政區域代碼") or "").strip(),
                "address": (row.get("街道項弄號") or "").strip(),
                "owner": (row.get("負責人") or "").strip(),
                "phone": (row.get("電話") or "").strip(),
                "slug": slugify(name, index),
                "index": index,
            }
            clinics.append(clinic)
    return clinics


def slugify(name: str, index: int) -> str:
    base = re.sub(r"\s+", "-", name)
    base = re.sub(r"[^\w\-一-龥]", "", base)
    base = base.strip("-_")
    if not base:
        base = "clinic"
    return f"{index:03d}-{base}"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "clinics").mkdir(exist_ok=True)


def write_index(clinics):
    cards = "\n".join(
        f"""
        <article class=\"clinic-card\">
            <h2><a href=\"clinics/{html.escape(c['slug'])}.html\">{html.escape(c['name'])}</a></h2>
            <p class=\"clinic-meta\">電話：<a href=\"tel:{html.escape(c['phone'])}\">{html.escape(c['phone'])}</a></p>
            <p class=\"clinic-meta\">地址：{html.escape(c['address'] or '未提供')}</p>
        </article>
        """.strip()
        for c in clinics
    )

    content = f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>新竹市牙醫診所列表</title>
    <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
    <header class=\"page-header\">
        <div class=\"container\">
            <p class=\"tag\">GitHub Pages</p>
            <h1>新竹市牙醫診所</h1>
            <p class=\"lead\">依照 csv 資料，為每間牙醫診所建立了獨立頁面。點擊任何診所名稱即可查看詳細資訊。</p>
        </div>
    </header>
    <main class=\"container\">
        <section class=\"grid\" aria-label=\"診所列表\">
            {cards}
        </section>
    </main>
    <footer class=\"page-footer\">
        <div class=\"container\">
            <p>資料來源：Dentist_Hsinchu_City.csv</p>
        </div>
    </footer>
</body>
</html>"""

    (OUTPUT_DIR / "index.html").write_text(content, encoding="utf-8")


def write_clinic_page(clinic):
    content = f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{html.escape(clinic['name'])}｜新竹市牙醫診所</title>
    <link rel=\"stylesheet\" href=\"../style.css\">
</head>
<body>
    <header class=\"page-header\">
        <div class=\"container\">
            <p class=\"tag\">牙醫診所 #{clinic['index']:03d}</p>
            <h1>{html.escape(clinic['name'])}</h1>
            <p class=\"lead\">為 GitHub Pages 所建立的獨立診所頁面。</p>
            <p><a class=\"button\" href=\"../index.html\">← 返回全部診所</a></p>
        </div>
    </header>
    <main class=\"container\">
        <section class=\"clinic-detail\">
            <dl>
                <div>
                    <dt>負責人</dt>
                    <dd>{html.escape(clinic['owner'] or '未提供')}</dd>
                </div>
                <div>
                    <dt>聯絡電話</dt>
                    <dd><a href=\"tel:{html.escape(clinic['phone'])}\">{html.escape(clinic['phone'] or '未提供')}</a></dd>
                </div>
                <div>
                    <dt>地址</dt>
                    <dd>{html.escape(clinic['address'] or '未提供')}</dd>
                </div>
                <div>
                    <dt>縣市代碼</dt>
                    <dd>{html.escape(clinic['city_code'] or '未提供')}</dd>
                </div>
                <div>
                    <dt>行政區域代碼</dt>
                    <dd>{html.escape(clinic['district_code'] or '未提供')}</dd>
                </div>
            </dl>
        </section>
    </main>
    <footer class=\"page-footer\">
        <div class=\"container\">
            <p>資料來源：Dentist_Hsinchu_City.csv</p>
        </div>
    </footer>
</body>
</html>"""

    output_file = OUTPUT_DIR / "clinics" / f"{clinic['slug']}.html"
    output_file.write_text(content, encoding="utf-8")


def write_styles():
    styles = """:root {
    color-scheme: light;
    --bg: #f8fafc;
    --text: #0f172a;
    --muted: #475569;
    --accent: #0ea5e9;
    --card: #ffffff;
    --border: #e2e8f0;
}

* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: "Noto Sans TC", "Inter", system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.container {
    width: min(1100px, 92vw);
    margin: 0 auto;
}

.page-header {
    background: linear-gradient(120deg, #e0f2fe, #e2f8f8);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 0;
    margin-bottom: 1.5rem;
}

.page-header h1 { margin: 0.4rem 0; font-size: 2.25rem; }
.page-header .lead { margin: 0; color: var(--muted); }

.page-footer {
    border-top: 1px solid var(--border);
    background: #f1f5f9;
    padding: 1.25rem 0;
    margin-top: 2rem;
    color: var(--muted);
}

.tag {
    display: inline-block;
    padding: 0.3rem 0.7rem;
    background: #0ea5e911;
    color: var(--accent);
    border-radius: 999px;
    font-weight: 600;
    letter-spacing: 0.01em;
}

.lead { font-size: 1.05rem; }

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1rem;
}

.clinic-card {
    background: var(--card);
    border: 1px solid var(--border);
    padding: 1.1rem 1.2rem;
    border-radius: 12px;
    box-shadow: 0 12px 30px -22px rgba(15, 23, 42, 0.3);
}

.clinic-card h2 {
    margin: 0;
    font-size: 1.2rem;
}

.clinic-card .clinic-meta {
    margin: 0.4rem 0;
    color: var(--muted);
}

.clinic-detail dl {
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
}

.clinic-detail dt {
    font-weight: 700;
    color: var(--muted);
}

.clinic-detail dd {
    margin: 0.2rem 0 0;
    font-size: 1.05rem;
}

.button {
    display: inline-block;
    padding: 0.55rem 0.9rem;
    border-radius: 10px;
    background: var(--accent);
    color: #fff;
    font-weight: 700;
}

.button:hover { filter: brightness(1.05); }
"""
    (OUTPUT_DIR / "style.css").write_text(styles, encoding="utf-8")


def main():
    clinics = load_clinics()
    ensure_output_dir()
    write_styles()
    write_index(clinics)
    for clinic in clinics:
        write_clinic_page(clinic)
    print(f"已建立 {len(clinics)} 間牙醫診所的獨立頁面於 {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
