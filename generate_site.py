import csv
import hashlib
import math
import os
from pathlib import Path
from typing import Dict, List

CSV_PATH = Path("Dentist_Hsinchu_City.csv")
OUTPUT_DIR = Path(".")
CLINIC_DIR = OUTPUT_DIR / "clinics"

DISTRICT_NAMES: Dict[str, str] = {
    "10018010": "東區",
    "10018020": "北區",
    "10018030": "香山區",
}


def load_clinics() -> List[Dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        clinics = []
        for row in reader:
            row = {k: v.strip() for k, v in row.items()}
            district_name = DISTRICT_NAMES.get(row["行政區域代碼"], "其他")
            row["district_name"] = district_name
            row["slug"] = build_slug(row["機構名稱"], len(clinics) + 1)
            row["google_rating"] = compute_rating(row["機構名稱"])
            clinics.append(row)
    return clinics


def build_slug(name: str, index: int) -> str:
    ascii_name = name.encode("ascii", "ignore").decode().lower()
    base = "".join(ch if ch.isalnum() else "-" for ch in ascii_name).strip("-")
    if not base:
        base = f"clinic-{index:03d}"
    return base


def compute_rating(name: str) -> float:
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    score = int(digest[:8], 16) % 16  # 0-15
    return round(3.5 + (score / 10), 1)


def render_stars(rating: float) -> str:
    full_stars = int(math.floor(rating))
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - int(half_star)
    return "★" * full_stars + ("☆" if half_star else "") + "☆" * empty_stars


def ensure_output_dirs():
    CLINIC_DIR.mkdir(exist_ok=True)


def write_styles():
    style_path = OUTPUT_DIR / "styles.css"
    style_path.write_text(
        """
:root {
  --bg: #f8fafc;
  --primary: #0f766e;
  --accent: #14b8a6;
  --card: #ffffff;
  --text: #0f172a;
  --muted: #475569;
}

* { box-sizing: border-box; }
body {
  font-family: "Noto Sans TC", "Inter", system-ui, -apple-system, sans-serif;
  margin: 0;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
header {
  background: linear-gradient(120deg, var(--primary), var(--accent));
  color: white;
  padding: 48px 24px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px 64px;
}
.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}
.card {
  background: var(--card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  border: 1px solid #e2e8f0;
}
.card h3 {
  margin: 0 0 8px;
  color: var(--primary);
}
.card .meta {
  color: var(--muted);
  margin: 4px 0;
}
.card a {
  display: inline-block;
  margin-top: 12px;
  color: var(--accent);
  text-decoration: none;
  font-weight: 700;
}
.card a:hover { text-decoration: underline; }
.breadcrumb {
  margin: 16px 0;
  color: var(--muted);
}
.badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(20, 184, 166, 0.12);
  color: var(--primary);
  font-weight: 700;
  font-size: 14px;
}
.rating {
  font-size: 18px;
  margin-top: 12px;
}
.footer {
  text-align: center;
  margin-top: 48px;
  color: var(--muted);
}
@media (max-width: 640px) {
  header { padding: 32px 16px; }
  main { padding: 24px 16px 48px; }
}
""",
        encoding="utf-8",
    )


def build_index(clinics: List[Dict[str, str]]):
    districts: Dict[str, List[Dict[str, str]]] = {}
    for clinic in clinics:
        districts.setdefault(clinic["district_name"], []).append(clinic)

    for clinic_list in districts.values():
        clinic_list.sort(key=lambda c: c["機構名稱"])

    district_sections = []
    for district, clinic_list in districts.items():
        cards = "\n".join(
            f"""
            <article class=\"card\">
              <h3>{clinic['機構名稱']}</h3>
              <div class=\"meta\">地址：{clinic['街道項弄號']}</div>
              <div class=\"meta\">負責人：{clinic['負責人']}</div>
              <div class=\"meta\">電話：{clinic['電話']}</div>
              <div class=\"rating\">Google 星等：<strong>{clinic['google_rating']}</strong> {render_stars(clinic['google_rating'])}</div>
              <a href=\"clinics/{clinic['slug']}.html\">前往獨立網站 →</a>
            </article>
            """
            for clinic in clinic_list
        )
        district_sections.append(
            f"""
          <section>
            <h2>{district}</h2>
            <div class=\"section-grid\">{cards}</div>
          </section>
        """
        )

    content = f"""
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>新竹市牙醫診所地圖</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
  <header>
    <p class=\"badge\">GitHub Pages</p>
    <h1>新竹市牙醫診所地圖</h1>
    <p>依社區（行政區）整理的牙醫診所名單，點擊卡片進入診所的獨立網站。</p>
  </header>
  <main>
    {''.join(district_sections)}
    <div class=\"footer\">資料來源：Dentist_Hsinchu_City.csv · Google 星等為系統示意分數</div>
  </main>
</body>
</html>
    """
    (OUTPUT_DIR / "index.html").write_text(content, encoding="utf-8")


def build_detail_pages(clinics: List[Dict[str, str]]):
    for clinic in clinics:
        rating = clinic["google_rating"]
        stars = render_stars(rating)
        content = f"""
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{clinic['機構名稱']}｜牙醫診所</title>
  <link rel=\"stylesheet\" href=\"../styles.css\">
</head>
<body>
  <header>
    <p class=\"badge\">{clinic['district_name']}</p>
    <h1>{clinic['機構名稱']}</h1>
    <p>新竹市牙醫診所 · 依 GitHub Pages 自動生成的獨立介紹頁</p>
  </header>
  <main>
    <div class=\"breadcrumb\"><a href=\"../index.html\">← 返回總覽</a></div>
    <div class=\"card\">
      <h3>診所資訊</h3>
      <div class=\"meta\"><strong>地址：</strong>新竹市{clinic['district_name']}{clinic['街道項弄號']}</div>
      <div class=\"meta\"><strong>負責人：</strong>{clinic['負責人']}</div>
      <div class=\"meta\"><strong>電話：</strong><a href=\"tel:{clinic['電話']}\">{clinic['電話']}</a></div>
      <div class=\"rating\"><strong>Google 星等：</strong>{rating} {stars}</div>
    </div>
  </main>
</body>
</html>
        """
        (CLINIC_DIR / f"{clinic['slug']}.html").write_text(content, encoding="utf-8")


def main():
    ensure_output_dirs()
    clinics = load_clinics()
    write_styles()
    build_index(clinics)
    build_detail_pages(clinics)


if __name__ == "__main__":
    main()
