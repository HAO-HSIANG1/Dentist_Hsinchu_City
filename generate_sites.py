import csv
import html
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent
DATA_FILE = REPO_ROOT / "Dentist_Hsinchu_City.csv"
DOCS_DIR = REPO_ROOT / "docs"
CLINICS_DIR = DOCS_DIR / "clinics"


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w-]+", "-", value.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-") or "clinic"


def load_clinics():
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_clinic_page(clinic: dict, slug: str):
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = CLINICS_DIR / f"{slug}.html"
    name = html.escape(clinic["機構名稱"])
    body = f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{name}</title>
    <link rel=\"stylesheet\" href=\"../style.css\">
</head>
<body>
    <header>
        <a class=\"back-link\" href=\"../index.html\">← 返回牙醫診所列表</a>
        <h1>{name}</h1>
    </header>
    <main>
        <section class=\"clinic-card\">
            <dl>
                <div><dt>縣市代碼</dt><dd>{html.escape(clinic['縣市別代碼'])}</dd></div>
                <div><dt>行政區域代碼</dt><dd>{html.escape(clinic['行政區域代碼'])}</dd></div>
                <div><dt>地址</dt><dd>{html.escape(clinic['街道項弄號'])}</dd></div>
                <div><dt>負責人</dt><dd>{html.escape(clinic['負責人'])}</dd></div>
                <div><dt>電話</dt><dd><a href=\"tel:{html.escape(clinic['電話'])}\">{html.escape(clinic['電話'])}</a></dd></div>
            </dl>
        </section>
    </main>
    <footer>資料來源：新竹市牙醫診所清單</footer>
</body>
</html>"""
    file_path.write_text(body, encoding="utf-8")


def build_index(clinics):
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    items_html = []
    for clinic in clinics:
        slug = slugify(clinic["機構名稱"])
        items_html.append(
            f"<li class='clinic-item'><a href='clinics/{slug}.html'>{html.escape(clinic['機構名稱'])}</a>"
            f"<div class='clinic-meta'>{html.escape(clinic['街道項弄號'])} · {html.escape(clinic['電話'])}</div>"
            f"</li>"
        )
        write_clinic_page(clinic, slug)

    body = f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>新竹市牙醫診所目錄</title>
    <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
    <header>
        <h1>新竹市牙醫診所目錄</h1>
        <p>每間診所都有自己的獨立頁面，點擊名稱即可查看詳細資訊。</p>
    </header>
    <main>
        <ul class=\"clinic-list\">
            {''.join(items_html)}
        </ul>
    </main>
    <footer>資料來源：新竹市牙醫診所清單</footer>
</body>
</html>"""
    (DOCS_DIR / "index.html").write_text(body, encoding="utf-8")


def main():
    clinics = load_clinics()
    build_index(clinics)


if __name__ == "__main__":
    main()
