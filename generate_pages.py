import csv
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import quote

DATA_FILE = Path("Dentist_Hsinchu_City.csv")
OUTPUT_DIR = Path("docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
CLINIC_DIR = OUTPUT_DIR / "clinics"

PAGE_TITLE_SUFFIX = "新竹市牙醫診所"


def extract_community(address: str) -> str:
    match = re.search(r"([^里]+里)", address)
    if match:
        return match.group(1)
    return "其他"


def slugify(name: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|#%{}]+", "", name)
    cleaned = re.sub(r"\s+", "-", cleaned.strip())
    cleaned = re.sub(r"-+", "-", cleaned)
    if cleaned:
        return cleaned
    return hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]


def star_markup(rating: float | None) -> str:
    if rating is None:
        return (
            '<div class="rating">'
            "<span class=\"rating-label\">Google 星等：</span>"
            "<span class=\"rating-na\">尚未提供</span>"
            "</div>"
        )
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half
    return (
        '<div class="rating">'
        "<span class=\"rating-label\">Google 星等：</span>"
        f"<span class=\"rating-value\">{rating:.1f}</span>"
        + "<span class=\"stars\">"
        + "★" * full
        + ("☆" if half else "")
        + "☆" * empty
        + "</span>"
        + "</div>"
    )


def ensure_assets():
    OUTPUT_DIR.mkdir(exist_ok=True)
    CLINIC_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    css = ASSETS_DIR / "style.css"
    if not css.exists():
        css.write_text(
            """
:root {
  --bg: #f8fafc;
  --card: #ffffff;
  --accent: #0ea5e9;
  --text: #0f172a;
  --muted: #475569;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Noto Sans TC", "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
}
header {
  background: linear-gradient(120deg, #22d3ee, #6366f1);
  color: #fff;
  padding: 2.5rem 1.5rem 2rem;
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}
header h1 { margin: 0 0 0.35rem; font-size: 2rem; }
header p { margin: 0; color: rgba(255,255,255,0.9); }
main { max-width: 1100px; margin: -2rem auto 3rem; padding: 0 1.25rem; }
.section { margin-bottom: 2rem; }
.community {
  background: var(--card);
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.18);
}
.community h2 {
  margin-top: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.community h2 .chip {
  background: rgba(14, 165, 233, 0.12);
  color: #0369a1;
  padding: 0.15rem 0.6rem;
  border-radius: 12px;
  font-size: 0.9rem;
  border: 1px solid rgba(14, 165, 233, 0.25);
}
.clinic-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin: 1rem 0 0;
}
.card {
  background: linear-gradient(180deg, #fff, #f8fafc);
  border-radius: 14px;
  padding: 1rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.card h3 { margin: 0; font-size: 1.05rem; }
.meta { color: var(--muted); font-size: 0.95rem; }
.meta strong { color: var(--text); }
.rating { display: flex; align-items: center; gap: 0.35rem; font-weight: 600; color: #f59e0b; }
.rating-label { color: var(--text); font-weight: 600; }
.rating-na { color: var(--muted); font-weight: 500; }
.rating-value { color: #d97706; }
.stars { letter-spacing: 0.1rem; }
.link-row {
  margin-top: auto;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 0.8rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  color: #0b3c5d;
  background: rgba(14, 165, 233, 0.15);
  border: 1px solid rgba(14, 165, 233, 0.3);
}
.btn:hover { background: rgba(14, 165, 233, 0.25); }
.icon { width: 18px; height: 18px; }
.footer { text-align: center; color: var(--muted); padding: 1rem 0 2rem; font-size: 0.9rem; }
.page { max-width: 850px; margin: 0 auto; padding: 1.5rem; }
.hero-card {
  background: var(--card);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 12px 30px rgba(15,23,42,0.12);
  border: 1px solid rgba(148, 163, 184, 0.18);
  display: grid;
  gap: 0.75rem;
}
.breadcrumbs { margin-bottom: 1rem; }
.breadcrumbs a { color: #0ea5e9; text-decoration: none; font-weight: 600; }
.hero-title { margin: 0; font-size: 1.6rem; }
.detail { color: var(--muted); }
.grid { display: grid; gap: 0.7rem; }
.badge { background: rgba(94, 234, 212, 0.2); color: #0f766e; padding: 0.3rem 0.7rem; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.35); width: fit-content; }

@media (max-width: 600px) {
  .card { padding: 0.85rem; }
  header { padding: 2rem 1.2rem 1.5rem; }
  main { padding: 0 1rem; }
}
""",
            encoding="utf-8",
        )


def load_clinics():
    clinics = []
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            name = row["機構名稱"].strip()
            address = row["街道項弄號"].strip()
            community = extract_community(address)
            clinic = {
                "name": name,
                "city_code": row["縣市別代碼"].strip(),
                "district_code": row["行政區域代碼"].strip(),
                "address": address,
                "principal": row["負責人"].strip(),
                "phone": row["電話"].strip(),
                "community": community,
                "slug": slugify(name),
                "rating": None,
            }
            clinics.append(clinic)
    return clinics


def write_clinic_page(clinic: dict):
    filename = CLINIC_DIR / f"{clinic['slug']}.html"
    title = f"{html.escape(clinic['name'])} | {PAGE_TITLE_SUFFIX}"
    address = html.escape(clinic["address"])
    phone_link = f"tel:{clinic['phone'].replace(' ', '')}"
    map_url = f"https://www.google.com/maps/search/?api=1&query={quote(clinic['address'])}"
    content = f"""
<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"../assets/style.css\">
</head>
<body>
  <div class=\"page\">
    <div class=\"breadcrumbs\"><a href=\"../index.html\">牙醫診所地圖</a></div>
    <div class=\"hero-card\">
      <div>
        <p class=\"badge\">{html.escape(clinic['community'])}</p>
        <h1 class=\"hero-title\">{html.escape(clinic['name'])}</h1>
        <div class=\"detail\">負責人：{html.escape(clinic['principal'])}</div>
        {star_markup(clinic['rating'])}
      </div>
      <div class=\"grid\">
        <div><strong>地址：</strong>{address}</div>
        <div><strong>電話：</strong><a href=\"{phone_link}\">{html.escape(clinic['phone'])}</a></div>
      </div>
      <div class=\"link-row\">
        <a class=\"btn\" href=\"{map_url}\" target=\"_blank\" rel=\"noreferrer noopener\">🗺️ 在 Google 地圖開啟</a>
        <a class=\"btn\" href=\"../index.html#community-{quote(clinic['community'])}\">⬅️ 回社區清單</a>
      </div>
    </div>
  </div>
</body>
</html>
"""
    filename.write_text(content, encoding="utf-8")


def write_index(communities: dict[str, list[dict]]):
    header = """
<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>新竹市牙醫診所地圖</title>
  <link rel=\"stylesheet\" href=\"assets/style.css\">
</head>
<body>
  <header>
    <h1>新竹市牙醫診所地圖</h1>
    <p>依社區分組的牙醫診所清單，點擊即可查看獨立網站與 Google 地圖連結。</p>
  </header>
  <main>
"""
    sections = []
    for community, clinics in communities.items():
        cards = []
        for clinic in clinics:
            map_url = f"https://www.google.com/maps/search/?api=1&query={quote(clinic['address'])}"
            cards.append(
                f"""
        <article class=\"card\">
          <h3><a href=\"clinics/{clinic['slug']}.html\">{html.escape(clinic['name'])}</a></h3>
          {star_markup(clinic['rating'])}
          <div class=\"meta\"><strong>地址：</strong>{html.escape(clinic['address'])}</div>
          <div class=\"meta\"><strong>電話：</strong><a href=\"tel:{clinic['phone']}\">{html.escape(clinic['phone'])}</a></div>
          <div class=\"link-row\">
            <a class=\"btn\" href=\"clinics/{clinic['slug']}.html\">🔍 診所網站</a>
            <a class=\"btn\" href=\"{map_url}\" target=\"_blank\" rel=\"noreferrer noopener\">🗺️ Google 地圖</a>
          </div>
        </article>
                """
            )
        section = f"""
    <section id=\"community-{quote(community)}\" class=\"section community\">
      <h2>{html.escape(community)} <span class=\"chip\">{len(clinics)} 間</span></h2>
      <div class=\"clinic-list\">
        {''.join(cards)}
      </div>
    </section>
        """
        sections.append(section)
    footer = """
    <div class=\"footer\">資料來源：Dentist_Hsinchu_City.csv。若有 Google 評分更新可在 generate_pages.py 中填入。</div>
  </main>
</body>
</html>
"""
    (OUTPUT_DIR / "index.html").write_text(header + "\n".join(sections) + footer, encoding="utf-8")


def main():
    ensure_assets()
    clinics = load_clinics()
    communities: dict[str, list[dict]] = {}
    for clinic in clinics:
        communities.setdefault(clinic["community"], []).append(clinic)
        write_clinic_page(clinic)
    communities = dict(sorted(communities.items(), key=lambda kv: kv[0]))
    for community in communities.values():
        community.sort(key=lambda c: c["name"])
    write_index(communities)
    generated_path = CLINIC_DIR.resolve()
    print(f"Generated {len(clinics)} clinic pages in {generated_path.relative_to(Path.cwd().resolve())}")


if __name__ == "__main__":
    main()
