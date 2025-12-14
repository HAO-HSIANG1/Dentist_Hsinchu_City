const fs = require('fs');
const path = require('path');

const CSV_FILE = path.join(__dirname, 'Dentist_Hsinchu_City.csv');
const OUTPUT_DIR = __dirname;
const CLINIC_DIR = path.join(OUTPUT_DIR, 'clinic-pages');

function readCsv(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '');
  const lines = raw.trim().split(/\r?\n/);
  const headers = lines.shift().split(',').map((header) => header.replace(/"/g, ''));
  return lines.map((line) => {
    const cells = parseCsvLine(line);
    const record = {};
    headers.forEach((header, idx) => {
      record[header] = cells[idx] || '';
    });
    return record;
  });
}

function parseCsvLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result.map((cell) => cell.trim());
}

function extractCommunity(address) {
  const match = address.match(/([\u4e00-\u9fff]{1,6}里)/);
  if (match) return match[1];
  const alt = address.match(/([\u4e00-\u9fff]{1,6}區)/);
  if (alt) return alt[1];
  return '未分類';
}

function slugify(name) {
  return name
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[\u3000]/g, '-')
    .replace(/[^\w\u4e00-\u9fff-]+/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .toLowerCase();
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function renderStarRating(ratingText) {
  if (!ratingText || ratingText === '未提供') {
    return '<span class="rating placeholder">Google 星等：暫無評分</span>';
  }
  const value = Number(ratingText);
  if (Number.isNaN(value)) {
    return `<span class="rating">Google 星等：${ratingText}</span>`;
  }
  const fullStars = Math.round(value);
  const stars = '★'.repeat(fullStars) + '☆'.repeat(5 - fullStars);
  return `<span class="rating">Google 星等：${value} ${stars}</span>`;
}

function buildClinicPages(clinics) {
  ensureDir(CLINIC_DIR);
  clinics.forEach((clinic) => {
    const mapQuery = encodeURIComponent(`${clinic['機構名稱']} ${clinic['街道項弄號']}`);
    const mapLink = `https://www.google.com/maps/search/?api=1&query=${mapQuery}`;
    const ratingSection = renderStarRating(clinic.rating || '未提供');
    const content = `<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${clinic['機構名稱']} | 新竹市牙醫診所</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body class="detail-page">
  <header class="site-header">
    <div>
      <p class="breadcrumb"><a href="../index.html">← 返回社區列表</a></p>
      <h1>${clinic['機構名稱']}</h1>
      <p class="community">社區：${clinic.community}</p>
    </div>
    <a class="map-icon" href="${mapLink}" target="_blank" rel="noopener noreferrer" title="在 Google 地圖開啟">
      🗺️
    </a>
  </header>
  <main class="detail-content">
    <section class="info-block">
      <h2>診所資訊</h2>
      <dl>
        <div><dt>地址</dt><dd>${clinic['街道項弄號']}</dd></div>
        <div><dt>電話</dt><dd><a href="tel:${clinic['電話']}">${clinic['電話']}</a></dd></div>
        <div><dt>負責人</dt><dd>${clinic['負責人']}</dd></div>
        <div><dt>Google 星等</dt><dd>${ratingSection}</dd></div>
      </dl>
    </section>
    <section class="cta">
      <a class="button primary" href="${mapLink}" target="_blank" rel="noopener noreferrer">在地圖查看位置</a>
      <a class="button" href="../index.html">返回列表</a>
    </section>
  </main>
</body>
</html>`;
    const filePath = path.join(CLINIC_DIR, `${clinic.slug}.html`);
    fs.writeFileSync(filePath, content, 'utf8');
  });
}

function buildIndexPage(grouped) {
  const communitySections = Object.keys(grouped)
    .sort((a, b) => a.localeCompare(b, 'zh-Hant'))
    .map((community) => {
      const cards = grouped[community]
        .sort((a, b) => a['機構名稱'].localeCompare(b['機構名稱'], 'zh-Hant'))
        .map((clinic) => {
          const mapQuery = encodeURIComponent(`${clinic['機構名稱']} ${clinic['街道項弄號']}`);
          const mapLink = `https://www.google.com/maps/search/?api=1&query=${mapQuery}`;
          return `<article class="card">
  <header>
    <div>
      <h3>${clinic['機構名稱']}</h3>
      <p class="address">${clinic['街道項弄號']}</p>
    </div>
    <a class="map-icon" href="${mapLink}" target="_blank" rel="noopener noreferrer" title="在 Google 地圖開啟">🗺️</a>
  </header>
  <p class="rating">Google 星等：暫無評分</p>
  <p class="meta">負責人：${clinic['負責人']}｜電話：<a href="tel:${clinic['電話']}">${clinic['電話']}</a></p>
  <div class="actions">
    <a class="button primary" href="clinic-pages/${clinic.slug}.html">前往診所頁面</a>
  </div>
</article>`;
        })
        .join('\n');
      return `<section class="community-section" id="${community}">
  <h2>${community}</h2>
  <div class="card-grid">${cards}</div>
</section>`;
    })
    .join('\n');

  const content = `<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>新竹市牙醫診所地圖</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="site-header">
    <div>
      <p class="eyebrow">GitHub Pages 靜態網站</p>
      <h1>新竹市牙醫診所目錄</h1>
      <p class="lead">依社區分類的牙醫診所清單，點擊地圖或診所頁面即可查看詳細資訊與地圖位置。</p>
    </div>
  </header>
  <main>
    ${communitySections}
  </main>
</body>
</html>`;

  fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), content, 'utf8');
}

function buildStyles() {
  const styles = `:root {
  --bg: #f7f7fb;
  --card: #ffffff;
  --text: #1f2933;
  --muted: #52616b;
  --primary: #1d72b8;
  --border: #e5e7eb;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Noto Sans TC", "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

.site-header {
  padding: 2rem clamp(1rem, 4vw, 3rem);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid var(--border);
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.eyebrow { letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); font-weight: 700; font-size: 0.85rem; }
.lead { color: var(--muted); max-width: 60ch; }

main { padding: 1.5rem clamp(1rem, 4vw, 3rem); }

.community-section { margin-bottom: 2.5rem; }
.community-section h2 { margin-bottom: 1rem; border-left: 4px solid var(--primary); padding-left: 0.75rem; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.card {
  background: var(--card);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 10px 30px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.card header { display: flex; justify-content: space-between; gap: 0.5rem; align-items: flex-start; }
.card h3 { margin: 0 0 0.25rem 0; }
.address { color: var(--muted); margin: 0; }
.meta { color: var(--muted); margin: 0; font-size: 0.95rem; }
.rating { font-weight: 600; margin: 0; }
.rating.placeholder { color: var(--muted); font-weight: 500; }

.actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
  font-weight: 700;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}
.button:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); text-decoration: none; }
.button.primary { background: var(--primary); color: #fff; border-color: var(--primary); }

.map-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: #f0f4ff;
  font-size: 1.25rem;
  text-decoration: none;
}
.map-icon:hover { background: #e5f0ff; }

.detail-page .site-header { position: static; }
.detail-page .breadcrumb { margin: 0 0 0.25rem 0; }
.community { margin: 0; color: var(--muted); }

.detail-content { padding: 1.5rem clamp(1rem, 4vw, 3rem); display: grid; gap: 1.5rem; }
.info-block { background: var(--card); padding: 1.25rem; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 10px 30px rgba(0,0,0,0.04); }
.info-block h2 { margin-top: 0; }
.info-block dl { margin: 0; display: grid; gap: 0.75rem; }
.info-block dt { font-weight: 700; }
.info-block dd { margin: 0.1rem 0 0 0; color: var(--muted); }

.cta { display: flex; gap: 0.75rem; flex-wrap: wrap; }

@media (max-width: 640px) {
  .card-grid { grid-template-columns: 1fr; }
  .site-header { flex-direction: column; align-items: flex-start; }
}
`;
  fs.writeFileSync(path.join(OUTPUT_DIR, 'styles.css'), styles, 'utf8');
}

function main() {
  const records = readCsv(CSV_FILE);
  const clinics = records.map((record) => {
    const clinic = { ...record };
    clinic.community = extractCommunity(record['街道項弄號']);
    clinic.slug = slugify(record['機構名稱']);
    return clinic;
  });

  const grouped = clinics.reduce((acc, clinic) => {
    if (!acc[clinic.community]) acc[clinic.community] = [];
    acc[clinic.community].push(clinic);
    return acc;
  }, {});

  buildStyles();
  buildClinicPages(clinics);
  buildIndexPage(grouped);
  console.log(`Generated ${clinics.length} clinic pages across ${Object.keys(grouped).length} communities.`);
}

main();
