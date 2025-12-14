import csv
import html
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

DATA_FILE = Path("Dentist_Hsinchu_City.csv")
OUTPUT_DIR = Path("docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
CLINIC_ROOT = OUTPUT_DIR / "clinics"

@dataclass
class Clinic:
    name: str
    city_code: str
    district_code: str
    address: str
    principal: str
    phone: str
    slug: str

def slugify(name: str, existing: set[str]) -> str:
    base = re.sub(r"\W+", "-", name.strip()).strip("-") or "clinic"
    slug = base
    suffix = 2
    while slug in existing:
        slug = f"{base}-{suffix}"
        suffix += 1
    existing.add(slug)
    return slug

def read_clinics() -> list[Clinic]:
    clinics: list[Clinic] = []
    seen_slugs: set[str] = set()
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("機構名稱", "").strip()
            slug = slugify(name, seen_slugs)
            clinics.append(
                Clinic(
                    name=name,
                    city_code=row.get("縣市別代碼", "").strip(),
                    district_code=row.get("行政區域代碼", "").strip(),
                    address=row.get("街道項弄號", "").strip(),
                    principal=row.get("負責人", "").strip(),
                    phone=row.get("電話", "").strip(),
                    slug=slug,
                )
            )
    return clinics


def ensure_directories():
    OUTPUT_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if CLINIC_ROOT.exists():
        shutil.rmtree(CLINIC_ROOT)
    CLINIC_ROOT.mkdir(parents=True, exist_ok=True)


def write_style():
    css = """
    :root {
        font-family: 'Noto Sans TC', system-ui, -apple-system, 'Segoe UI', sans-serif;
        color: #1f2933;
        background: #f7fafc;
        line-height: 1.6;
    }
    body {
        margin: 0;
        min-height: 100vh;
        background: linear-gradient(180deg, #fefefe 0%, #eef2f7 100%);
    }
    header {
        background: #0f766e;
        color: #fff;
        padding: 1.5rem 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    header h1 { margin: 0; font-size: 1.8rem; }
    header p { margin: 0.4rem 0 0; opacity: 0.9; }
    main { padding: 1.25rem; max-width: 1200px; margin: 0 auto; }
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
    }
    .card {
        background: #fff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    .card h2 { margin-top: 0; margin-bottom: 0.4rem; font-size: 1.25rem; }
    .card a { color: #0f766e; text-decoration: none; font-weight: 600; }
    .meta { color: #52606d; margin: 0.2rem 0; }
    nav {
        margin-bottom: 1rem;
    }
    nav a { color: #0f766e; text-decoration: none; font-weight: 600; }
    .detail {
        background: #fff;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 8px 22px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
    }
    .detail h2 { margin-top: 0; }
    .info-row { margin: 0.3rem 0; color: #334155; }
    footer {
        text-align: center;
        padding: 1rem;
        color: #52606d;
    }
    """
    (ASSETS_DIR / "style.css").write_text(css, encoding="utf-8")


def render_index(clinics: list[Clinic]):
    cards = "\n".join(
        f"""
        <article class=\"card\">
            <h2><a href=\"clinics/{c.slug}/\">{html.escape(c.name)}</a></h2>
            <p class=\"meta\">地址：{html.escape(c.address)}</p>
            <p class=\"meta\">電話：{html.escape(c.phone)}</p>
        </article>
        """
        for c in clinics
    )
    index_html = f"""
    <!doctype html>
    <html lang=\"zh-Hant\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>新竹市牙醫診所索引</title>
        <link rel=\"stylesheet\" href=\"assets/style.css\" />
    </head>
    <body>
        <header>
            <h1>新竹市牙醫診所</h1>
            <p>資料來源：Dentist_Hsinchu_City.csv</p>
        </header>
        <main>
            <div class=\"grid\">
                {cards}
            </div>
        </main>
        <footer>自動產生的診所索引</footer>
    </body>
    </html>
    """
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")


def render_clinic_page(clinic: Clinic):
    page_dir = CLINIC_ROOT / clinic.slug
    page_dir.mkdir(parents=True, exist_ok=True)
    detail_html = f"""
    <!doctype html>
    <html lang=\"zh-Hant\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>{html.escape(clinic.name)}｜牙醫診所</title>
        <link rel=\"stylesheet\" href=\"../../assets/style.css\" />
    </head>
    <body>
        <header>
            <h1>{html.escape(clinic.name)}</h1>
            <p>負責人：{html.escape(clinic.principal)}</p>
        </header>
        <main>
            <nav><a href=\"../../index.html\">← 回到診所索引</a></nav>
            <section class=\"detail\">
                <h2>診所資訊</h2>
                <p class=\"info-row\"><strong>地址：</strong>{html.escape(clinic.address)}</p>
                <p class=\"info-row\"><strong>電話：</strong>{html.escape(clinic.phone)}</p>
                <p class=\"info-row\"><strong>縣市代碼：</strong>{html.escape(clinic.city_code)}</p>
                <p class=\"info-row\"><strong>行政區代碼：</strong>{html.escape(clinic.district_code)}</p>
            </section>
        </main>
        <footer>自動產生的診所網頁</footer>
    </body>
    </html>
    """
    (page_dir / "index.html").write_text(detail_html, encoding="utf-8")


def main():
    clinics = read_clinics()
    ensure_directories()
    write_style()
    render_index(clinics)
    for clinic in clinics:
        render_clinic_page(clinic)
    print(f"Generated {len(clinics)} clinic pages in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
