import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "Dentist_Hsinchu_City.csv"
DOCS_DIR = ROOT / "docs"
CLINICS_DIR = DOCS_DIR / "clinics"

DOCS_DIR.mkdir(exist_ok=True)
CLINICS_DIR.mkdir(parents=True, exist_ok=True)


def slugify(name: str, index: int) -> str:
    # Keep ASCII letters/digits, replace others with hyphen
    safe = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    safe = safe or "clinic"
    return f"{index:03d}-{safe}"


def read_clinics():
    clinics = []
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            name = row.get("機構名稱", "").strip()
            clinic = {
                "id": idx,
                "name": name,
                "city_code": row.get("縣市別代碼", "").strip(),
                "district_code": row.get("行政區域代碼", "").strip(),
                "address": row.get("街道項弄號", "").strip(),
                "owner": row.get("負責人", "").strip(),
                "phone": row.get("電話", "").strip(),
            }
            clinic["slug"] = slugify(name, idx)
            clinics.append(clinic)
    return clinics


def render_layout(title: str, body: str, back_link: str | None = None) -> str:
    nav = "" if not back_link else f'<a class="back-link" href="{back_link}">⬅ 返回列表</a>'
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <link rel=\"stylesheet\" href=\"../styles.css\" />
</head>
<body>
  <header>
    <div class=\"brand\">新竹市牙醫診所地圖</div>
    {nav}
  </header>
  <main>
    {body}
  </main>
  <footer>資料來源：Dentist_Hsinchu_City.csv</footer>
</body>
</html>"""


def render_index(clinics):
    cards = []
    for clinic in clinics:
        cards.append(
            f"""<article class=\"card\">
  <div class=\"card-title\">{html.escape(clinic['name'])}</div>
  <div class=\"card-meta\">負責人：{html.escape(clinic['owner'] or '未提供')}</div>
  <div class=\"card-meta\">電話：{html.escape(clinic['phone'] or '未提供')}</div>
  <div class=\"card-meta\">地址：{html.escape(clinic['address'] or '未提供')}</div>
  <a class=\"button\" href=\"clinics/{clinic['slug']}.html\">進入診所頁面</a>
</article>"""
        )

    body = f"""
    <section class=\"intro\">
      <h1>新竹市牙醫診所一覽</h1>
      <p>共收錄 {len(clinics)} 家牙醫診所。點擊下方卡片即可查看各診所的專屬頁面。</p>
    </section>
    <section class=\"grid\">{''.join(cards)}</section>
    """
    return render_layout("新竹市牙醫診所一覽", body, back_link=None).replace("../styles.css", "styles.css")


def render_clinic_page(clinic):
    body = f"""
    <section class=\"clinic-hero\">
      <h1>{html.escape(clinic['name'])}</h1>
      <p class=\"subtitle\">用心守護您的牙齒健康</p>
    </section>
    <section class=\"clinic-details\">
      <dl>
        <div><dt>負責人</dt><dd>{html.escape(clinic['owner'] or '未提供')}</dd></div>
        <div><dt>電話</dt><dd>{html.escape(clinic['phone'] or '未提供')}</dd></div>
        <div><dt>地址</dt><dd>{html.escape(clinic['address'] or '未提供')}</dd></div>
        <div><dt>縣市代碼</dt><dd>{html.escape(clinic['city_code'] or '未提供')}</dd></div>
        <div><dt>行政區域代碼</dt><dd>{html.escape(clinic['district_code'] or '未提供')}</dd></div>
      </dl>
    </section>
    <section class=\"cta\">
      <p>如需預約或諮詢，請直接撥打電話與診所聯絡。</p>
      <a class=\"button\" href=\"tel:{html.escape(clinic['phone'])}\">立即致電</a>
    </section>
    """
    return render_layout(clinic["name"], body, back_link="../index.html")


def write_files(clinics):
    (DOCS_DIR / "styles.css").write_text(STYLES, encoding="utf-8")
    (DOCS_DIR / "index.html").write_text(render_index(clinics), encoding="utf-8")
    for clinic in clinics:
        content = render_clinic_page(clinic)
        (CLINICS_DIR / f"{clinic['slug']}.html").write_text(content, encoding="utf-8")


STYLES = """
:root {
  --bg: #0f172a;
  --card: #111827;
  --accent: #a855f7;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --border: #1f2937;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Noto Sans TC', 'Inter', system-ui, -apple-system, sans-serif;
  background: radial-gradient(circle at 20% 20%, #1e293b 0, #0f172a 40%),
              radial-gradient(circle at 80% 0%, rgba(168,85,247,0.1), #0f172a 45%),
              #0f172a;
  color: var(--text);
  min-height: 100vh;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  position: sticky;
  top: 0;
  backdrop-filter: blur(10px);
  background: rgba(15,23,42,0.8);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}
.brand {
  font-weight: 700;
  letter-spacing: 0.05em;
}
.back-link {
  color: var(--text);
  text-decoration: none;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all .2s ease;
}
.back-link:hover { border-color: var(--accent); color: var(--accent); }
main { padding: 32px; max-width: 1200px; margin: 0 auto; }
.intro h1 { margin: 0 0 8px; font-size: 32px; }
.intro p { color: var(--muted); margin: 0 0 24px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.card {
  background: linear-gradient(145deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border: 1px solid var(--border);
  padding: 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.35);
}
.card-title { font-weight: 700; font-size: 18px; }
.card-meta { color: var(--muted); font-size: 14px; }
.button {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 12px;
  background: linear-gradient(120deg, #a855f7, #6366f1);
  color: #fff;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 10px 30px rgba(99,102,241,0.35);
  transition: transform .15s ease, box-shadow .2s ease;
}
.button:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(99,102,241,0.45); }
.button:active { transform: translateY(0); }
.clinic-hero {
  background: radial-gradient(circle at 15% 20%, rgba(99,102,241,0.2), transparent 45%),
              radial-gradient(circle at 85% 15%, rgba(168,85,247,0.2), transparent 40%),
              linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
  border: 1px solid var(--border);
  padding: 32px;
  border-radius: 18px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.4);
}
.clinic-hero h1 { margin: 0; font-size: 32px; }
.clinic-hero .subtitle { color: var(--muted); margin-top: 6px; }
.clinic-details { margin-top: 24px; padding: 24px; border: 1px solid var(--border); border-radius: 16px; background: rgba(255,255,255,0.02); }
.clinic-details dl { margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px 12px; }
.clinic-details dt { font-weight: 600; color: var(--muted); }
.clinic-details dd { margin: 4px 0 0; font-size: 16px; color: var(--text); }
.cta { margin-top: 24px; padding: 20px; border-radius: 14px; border: 1px dashed var(--border); background: rgba(255,255,255,0.02); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
footer { margin: 40px auto 20px; max-width: 1200px; color: var(--muted); font-size: 13px; text-align: center; }
@media (max-width: 640px) { main { padding: 20px; } header { flex-direction: column; gap: 12px; } .cta { flex-direction: column; align-items: flex-start; } }
"""


def main():
    clinics = read_clinics()
    write_files(clinics)
    print(json.dumps({"count": len(clinics)}))


if __name__ == "__main__":
    main()
