import csv
import html
from pathlib import Path

CSV_PATH = Path("Dentist_Hsinchu_City.csv")
DOCS_DIR = Path("docs")
CLINICS_DIR = DOCS_DIR / "clinics"


def read_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            rows.append(cleaned)
        return rows


def get_value(row: dict, key: str, default: str = "") -> str:
    for k, v in row.items():
        if k.strip() == key:
            return v or default
    return default


def clinic_slug(index: int) -> str:
    return f"clinic-{index:03d}"


def render_page(clinic: dict, slug: str) -> str:
    name = html.escape(get_value(clinic, "機構名稱"))
    address = html.escape(get_value(clinic, "街道項弄號"))
    director = html.escape(get_value(clinic, "負責人"))
    phone = html.escape(get_value(clinic, "電話"))
    full_address = f"新竹市{address}" if address else "新竹市"
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{name} | 新竹市牙醫診所</title>
  <link rel=\"stylesheet\" href=\"../style.css\">
</head>
<body>
  <header class=\"site-header\">
    <a class=\"home-link\" href=\"../index.html\">← 返回診所列表</a>
    <h1>{name}</h1>
  </header>
  <main>
    <section class=\"card\">
      <h2>診所資訊</h2>
      <dl>
        <div>
          <dt>地址</dt>
          <dd>{full_address}</dd>
        </div>
        <div>
          <dt>電話</dt>
          <dd><a href=\"tel:{phone}\">{phone}</a></dd>
        </div>
        <div>
          <dt>負責人</dt>
          <dd>{director}</dd>
        </div>
      </dl>
    </section>
  </main>
  <footer class=\"site-footer\">
    <p>資料來源：Dentist_Hsinchu_City.csv</p>
  </footer>
</body>
</html>"""


def render_index(clinics: list[dict]) -> str:
    rows = []
    for index, clinic in enumerate(clinics):
        slug = clinic_slug(index)
        name = html.escape(get_value(clinic, "機構名稱"))
        phone = html.escape(get_value(clinic, "電話"))
        address = html.escape(get_value(clinic, "街道項弄號"))
        rows.append(
            f"<tr><td><a href=\"clinics/{slug}.html\">{name}</a></td>"
            f"<td><a href=\"tel:{phone}\">{phone}</a></td>"
            f"<td>新竹市{address}</td></tr>"
        )

    table_rows = "\n        ".join(rows)
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>新竹市牙醫診所列表</title>
  <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
  <header class=\"site-header\">
    <h1>新竹市牙醫診所列表</h1>
    <p>每家診所都有獨立頁面，方便透過 GitHub Pages 分享。</p>
  </header>
  <main>
    <section class=\"card\">
      <h2>診所清單</h2>
      <div class=\"table-wrapper\">
        <table>
          <thead>
            <tr><th>診所名稱</th><th>電話</th><th>地址</th></tr>
          </thead>
          <tbody>
        {table_rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <footer class=\"site-footer\">
    <p>資料來源：Dentist_Hsinchu_City.csv</p>
  </footer>
</body>
</html>"""


def build():
    clinics = read_rows(CSV_PATH)
    DOCS_DIR.mkdir(exist_ok=True)
    CLINICS_DIR.mkdir(parents=True, exist_ok=True)

    for index, clinic in enumerate(clinics):
        slug = clinic_slug(index)
        page = render_page(clinic, slug)
        (CLINICS_DIR / f"{slug}.html").write_text(page, encoding="utf-8")

    index_html = render_index(clinics)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")


if __name__ == "__main__":
    build()
