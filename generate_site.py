from __future__ import annotations
import csv
import json
import re
import urllib.parse
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).parent
DATA_FILE = REPO_ROOT / "Dentist_Hsinchu_City.csv"
DOCS_DIR = REPO_ROOT / "docs"
DATA_DIR = DOCS_DIR / "data"
CLINIC_DIR = DOCS_DIR / "clinics"

DISTRICT_MAP: Dict[str, str] = {
    "10018010": "東區",
    "10018020": "北區",
    "10018030": "香山區",
}


def slugify(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "clinic"


def load_records() -> List[dict]:
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        records = []
        for row in reader:
            name = row.get("機構名稱") or row.get("\ufeff機構名稱") or "未知名稱"
            district_code = row.get("行政區域代碼", "").strip()
            district = DISTRICT_MAP.get(district_code, district_code or "其他")
            address = row.get("街道項弄號", "")
            director = row.get("負責人", "")
            phone = row.get("電話", "")
            slug = slugify(name)
            map_query = urllib.parse.quote_plus(f"{name} {address}")
            map_url = f"https://www.google.com/maps/search/?api=1&query={map_query}"
            records.append(
                {
                    "name": name,
                    "districtCode": district_code,
                    "district": district,
                    "address": address,
                    "director": director,
                    "phone": phone,
                    "slug": slug,
                    "mapUrl": map_url,
                }
            )
    return records


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CLINIC_DIR.mkdir(parents=True, exist_ok=True)


def write_json(records: List[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "dentists.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_ratings_template(records: List[dict]) -> None:
    ratings_path = DOCS_DIR / "ratings.json"
    existing = {}
    if ratings_path.exists():
        try:
            existing = json.loads(ratings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    for record in records:
        existing.setdefault(
            record["slug"],
            {"rating": None, "note": "尚未提供星等，請點擊地圖查看最新評論"},
        )

    ratings_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def build_clinic_page(record: dict) -> str:
    rating_placeholder = "尚未提供星等，請點擊地圖查看最新評論"
    return f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{record['name']} | 新竹市牙醫診所</title>
  <link rel=\"stylesheet\" href=\"../style.css\" />
</head>
<body class=\"clinic-page\">
  <header class=\"hero\">
    <div class=\"hero__content\">
      <a class=\"back-link\" href=\"../index.html\">← 返回診所列表</a>
      <p class=\"eyebrow\">{record['district']} · 社區牙醫</p>
      <h1>{record['name']}</h1>
      <p class=\"rating\" data-slug=\"{record['slug']}\">Google 星等：<span class=\"rating__value\">{rating_placeholder}</span></p>
    </div>
  </header>

  <main class=\"content\">
    <section class=\"card\">
      <h2>診所資訊</h2>
      <dl class=\"definition-list\">
        <div><dt>社區</dt><dd>{record['district']}</dd></div>
        <div><dt>地址</dt><dd>{record['address']}</dd></div>
        <div><dt>電話</dt><dd><a href=\"tel:{record['phone']}\">{record['phone']}</a></dd></div>
        <div><dt>負責人</dt><dd>{record['director']}</dd></div>
      </dl>
      <div class=\"actions\">
        <a class=\"button\" href=\"tel:{record['phone']}\">撥打電話</a>
        <a class=\"button button--ghost\" href=\"{record['mapUrl']}\" target=\"_blank\" rel=\"noreferrer\">
          <span class=\"icon\" aria-hidden=\"true\">📍</span> 開啟 Google 地圖
        </a>
      </div>
    </section>

    <section class=\"card\">
      <h2>如何取得最新評價？</h2>
      <p>Google 星星數會隨時間更新。若要查看最新的 Google 評分與評論，請點擊上方的地圖按鈕，直接於 Google 地圖查看。</p>
    </section>
  </main>
  <script src=\"../rating.js\"></script>
</body>
</html>
"""


def write_clinic_pages(records: List[dict]) -> None:
    for record in records:
        path = CLINIC_DIR / f"{record['slug']}.html"
        path.write_text(build_clinic_page(record), encoding="utf-8")


def main() -> None:
    ensure_directories()
    records = load_records()
    write_json(records)
    write_ratings_template(records)
    write_clinic_pages(records)
    print(f"Generated {len(records)} clinic pages.")


if __name__ == "__main__":
    main()
