import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from urllib.parse import quote

DISTRICT_NAMES = {
    "10018010": "東區",
    "10018020": "北區",
    "10018030": "香山區",
}

@dataclass
class Clinic:
    name: str
    city_code: str
    district_code: str
    address: str
    manager: str
    phone: str
    slug: str

    @property
    def district_name(self) -> str:
        return DISTRICT_NAMES.get(self.district_code, self.district_code)

    @property
    def google_maps_url(self) -> str:
        query = quote(f"{self.name} {self.address}")
        return f"https://www.google.com/maps/search/?api=1&query={query}"

    @property
    def cover_image(self) -> str:
        text = quote(self.name)
        return f"https://placehold.co/900x540?text={text}"


def read_clinics(csv_path: Path) -> List[Clinic]:
    clinics: List[Clinic] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            clinics.append(
                Clinic(
                    name=row["機構名稱"],
                    city_code=row["縣市別代碼"],
                    district_code=row["行政區域代碼"],
                    address=row["街道項弄號"],
                    manager=row["負責人"],
                    phone=row["電話"],
                    slug=f"clinic-{idx:03d}",
                )
            )
    return clinics


def group_by_district(clinics: List[Clinic]) -> Dict[str, List[Clinic]]:
    grouped: Dict[str, List[Clinic]] = {}
    for clinic in clinics:
        grouped.setdefault(clinic.district_name, []).append(clinic)
    for group in grouped.values():
        group.sort(key=lambda c: c.name)
    return grouped


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def base_template(title: str, body: str, asset_prefix: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"{asset_prefix}assets/styles.css\" />
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap\" rel=\"stylesheet\" />
</head>
<body>
  <header class=\"site-header\">
    <div class=\"site-identity\">
      <span class=\"logo\">🦷</span>
      <div>
        <p class=\"eyebrow\">新竹市牙醫診所總覽</p>
        <h1>Dentist Hsinchu City</h1>
      </div>
    </div>
    <nav>
      <a href=\"index.html\">首頁</a>
    </nav>
  </header>
  <main class=\"content\">
    {body}
  </main>
  <footer class=\"site-footer\">資料來源：新竹市政府 — 若需最新評價，請至 Google Maps 查看。</footer>
</body>
</html>
"""


def render_rating_section(rating: str | None = None) -> str:
    if rating:
        try:
            value = float(rating)
            stars = "".join("★" if i < round(value) else "☆" for i in range(5))
            label = f"Google 星等：{value:.1f} {stars}"
        except ValueError:
            label = f"Google 星等：{rating}"
    else:
        label = "Google 星等：尚未提供，點擊地圖查看最新評價"
    return f"<p class=\"rating\">{label}</p>"


def render_index(grouped: Dict[str, List[Clinic]]) -> str:
    sections = []
    for district, clinics in sorted(grouped.items()):
        cards = "\n".join(
            f"""
            <article class=\"clinic-card\">
              <img src=\"{clinic.cover_image}\" alt=\"{clinic.name} 封面照\" loading=\"lazy\" />
              <div class=\"card-body\">
                <div class=\"card-header\">
                  <h3>{clinic.name}</h3>
                  <span class=\"district\">{district}</span>
                </div>
                {render_rating_section()}
                <p class=\"address\">📍 {clinic.address}</p>
                <p class=\"manager\">負責人：{clinic.manager}</p>
                <p class=\"phone\">電話：<a href=\"tel:{clinic.phone}\">{clinic.phone}</a></p>
                <div class=\"card-actions\">
                  <a class=\"button\" href=\"districts/{district}.html\">該社區更多診所</a>
                  <a class=\"button primary\" href=\"clinics/{clinic.slug}.html\">查看診所頁面</a>
                  <a class=\"icon-button\" href=\"{clinic.google_maps_url}\" aria-label=\"前往 Google Maps\">🗺️</a>
                </div>
              </div>
            </article>
            """
            for clinic in clinics
        )
        sections.append(
            f"""
            <section>
              <div class=\"section-title\">
                <h2>{district}</h2>
                <span class=\"badge\">{len(clinics)} 間診所</span>
              </div>
              <div class=\"grid\">
                {cards}
              </div>
            </section>
            """
        )
    hero = """
      <section class=\"hero\">
        <div>
          <p class=\"eyebrow\">按社區分類瀏覽</p>
          <h2>選擇社區，找到合適的牙醫診所</h2>
          <p>一鍵跳轉 Google Maps 查看即時評價，或深入診所專頁掌握詳細資訊。</p>
        </div>
      </section>
    """
    return base_template("Dentist Hsinchu City", hero + "\n".join(sections))


def render_district_page(district: str, clinics: List[Clinic]) -> str:
    cards = "\n".join(
        f"""
        <article class=\"clinic-card\">
          <img src=\"{clinic.cover_image}\" alt=\"{clinic.name} 封面照\" loading=\"lazy\" />
          <div class=\"card-body\">
            <div class=\"card-header\">
              <h3>{clinic.name}</h3>
            </div>
            {render_rating_section()}
            <p class=\"address\">📍 {clinic.address}</p>
            <p class=\"manager\">負責人：{clinic.manager}</p>
            <p class=\"phone\">電話：<a href=\"tel:{clinic.phone}\">{clinic.phone}</a></p>
            <div class=\"card-actions\">
              <a class=\"button primary\" href=\"../clinics/{clinic.slug}.html\">查看診所頁面</a>
              <a class=\"icon-button\" href=\"{clinic.google_maps_url}\" aria-label=\"前往 Google Maps\">🗺️</a>
            </div>
          </div>
        </article>
        """
        for clinic in clinics
    )
    body = f"""
      <section class=\"hero\">
        <div>
          <p class=\"eyebrow\">{district}</p>
          <h2>{district}牙醫診所</h2>
          <p>共 {len(clinics)} 間診所，點擊卡片即可前往詳細頁或 Google Maps。</p>
        </div>
      </section>
      <div class=\"grid\">{cards}</div>
    """
    return base_template(f"{district} 牙醫診所", body, asset_prefix="../")


def render_clinic_page(clinic: Clinic) -> str:
    body = f"""
      <section class=\"detail\">
        <img class=\"detail-cover\" src=\"{clinic.cover_image}\" alt=\"{clinic.name} 封面照\" />
        <div class=\"detail-body\">
          <p class=\"eyebrow\">{clinic.district_name}</p>
          <h2>{clinic.name}</h2>
          {render_rating_section()}
          <p class=\"address\">📍 {clinic.address}</p>
          <p class=\"manager\">負責人：{clinic.manager}</p>
          <p class=\"phone\">電話：<a href=\"tel:{clinic.phone}\">{clinic.phone}</a></p>
          <div class=\"detail-actions\">
            <a class=\"button primary\" href=\"{clinic.google_maps_url}\">在 Google Maps 查看</a>
            <a class=\"button\" href=\"../districts/{clinic.district_name}.html\">返回 {clinic.district_name}</a>
          </div>
        </div>
      </section>
    """
    return base_template(f"{clinic.name}｜牙醫診所", body, asset_prefix="../")


def main() -> None:
    csv_path = Path("Dentist_Hsinchu_City.csv")
    clinics = read_clinics(csv_path)
    grouped = group_by_district(clinics)

    output_dir = Path(".")

    write_file(output_dir / "index.html", render_index(grouped))

    for district, clinic_list in grouped.items():
        write_file(output_dir / "districts" / f"{district}.html", render_district_page(district, clinic_list))

    for clinic in clinics:
        write_file(output_dir / "clinics" / f"{clinic.slug}.html", render_clinic_page(clinic))

if __name__ == "__main__":
    main()
