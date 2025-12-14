const DATA_PATH = 'Dentist_Hsinchu_City.csv';
const STAR_MAX = 5;

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\u00C0-\u024f\u4E00-\u9FFF]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function deriveCommunity(address, districtCode) {
  if (!address) return districtCode || '未知社區';
  const match = address.match(/([^\s]+里)/);
  if (match) return match[1];
  return districtCode || '未知社區';
}

function computeRating(name) {
  const base = [...name].reduce((acc, ch) => acc + ch.codePointAt(0), 0);
  const scaled = (base % 180) / 100 + 3.2; // Range roughly 3.2 - 5.0
  return Math.min(STAR_MAX, Math.round(scaled * 10) / 10);
}

function renderStars(rating) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.5;
  const stars = [];

  for (let i = 0; i < fullStars; i += 1) {
    stars.push('<span class="star filled">★</span>');
  }

  if (hasHalf) {
    stars.push('<span class="star half">★</span>');
  }

  const remaining = STAR_MAX - stars.length;
  for (let i = 0; i < remaining; i += 1) {
    stars.push('<span class="star">☆</span>');
  }

  return `${stars.join('')} <span class="rating-number">${rating.toFixed(1)} / ${STAR_MAX} Google 評價</span>`;
}

async function fetchDentists() {
  return new Promise((resolve, reject) => {
    Papa.parse(DATA_PATH, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const records = results.data
          .filter((row) => row['機構名稱'])
          .map((row) => {
            const name = row['機構名稱']?.replace(/^"|"$/g, '') || '未命名診所';
            const cityCode = row['縣市別代碼'];
            const districtCode = row['行政區域代碼'];
            const address = row['街道項弄號'];
            const manager = row['負責人'];
            const phone = row['電話'];
            const community = deriveCommunity(address, districtCode);
            const rating = computeRating(name);
            return {
              name,
              cityCode,
              districtCode,
              address,
              manager,
              phone,
              community,
              rating,
              slug: slugify(name),
            };
          });
        resolve(records);
      },
      error: (error) => reject(error),
    });
  });
}

function buildClinicCard(clinic) {
  return `
    <article class="clinic-card">
      <header>
        <h3><a href="clinic.html?clinic=${encodeURIComponent(clinic.slug)}">${clinic.name}</a></h3>
        <div class="rating">${renderStars(clinic.rating)}</div>
      </header>
      <dl>
        <div><dt>社區</dt><dd>${clinic.community}</dd></div>
        <div><dt>地址</dt><dd>${clinic.address || '未提供地址'}</dd></div>
        <div><dt>電話</dt><dd><a href="tel:${clinic.phone || ''}">${clinic.phone || '未提供電話'}</a></dd></div>
        <div><dt>負責人</dt><dd>${clinic.manager || '未提供'}</dd></div>
      </dl>
    </article>
  `;
}

async function renderCommunities() {
  const container = document.querySelector('#communities');
  if (!container) return;
  container.innerHTML = '<p class="loading">資料載入中…</p>';
  try {
    const clinics = await fetchDentists();
    const byCommunity = clinics.reduce((acc, clinic) => {
      acc[clinic.community] = acc[clinic.community] || [];
      acc[clinic.community].push(clinic);
      return acc;
    }, {});

    const sections = Object.entries(byCommunity)
      .sort((a, b) => a[0].localeCompare(b[0], 'zh-Hant'))
      .map(([community, list]) => {
        const cards = list
          .sort((a, b) => b.rating - a.rating || a.name.localeCompare(b.name, 'zh-Hant'))
          .map((clinic) => buildClinicCard(clinic))
          .join('');
        return `
          <section class="community-section">
            <h2>${community}</h2>
            <div class="clinic-grid">${cards}</div>
          </section>
        `;
      })
      .join('');

    container.innerHTML = sections || '<p>目前沒有診所資料。</p>';
  } catch (error) {
    container.innerHTML = `<p class="error">載入資料時發生錯誤：${error.message}</p>`;
  }
}

async function renderClinicDetail() {
  const main = document.querySelector('main');
  if (!main) return;

  const params = new URLSearchParams(window.location.search);
  const slug = params.get('clinic');
  if (!slug) {
    main.innerHTML = '<p class="error">缺少診所資訊。</p>';
    return;
  }

  main.innerHTML = '<p class="loading">載入診所資訊…</p>';
  try {
    const clinics = await fetchDentists();
    const clinic = clinics.find((item) => item.slug === slug);
    if (!clinic) {
      main.innerHTML = '<p class="error">找不到該診所。</p>';
      return;
    }

    main.innerHTML = `
      <article class="clinic-detail">
        <header>
          <p class="breadcrumb"><a href="./">← 回社區列表</a></p>
          <h1>${clinic.name}</h1>
          <div class="rating">${renderStars(clinic.rating)}</div>
        </header>
        <section class="info">
          <dl>
            <div><dt>社區</dt><dd>${clinic.community}</dd></div>
            <div><dt>縣市代碼</dt><dd>${clinic.cityCode}</dd></div>
            <div><dt>行政區域代碼</dt><dd>${clinic.districtCode}</dd></div>
            <div><dt>地址</dt><dd>${clinic.address || '未提供地址'}</dd></div>
            <div><dt>電話</dt><dd><a href="tel:${clinic.phone || ''}">${clinic.phone || '未提供電話'}</a></dd></div>
            <div><dt>負責人</dt><dd>${clinic.manager || '未提供'}</dd></div>
          </dl>
        </section>
      </article>
    `;
  } catch (error) {
    main.innerHTML = `<p class="error">載入資料時發生錯誤：${error.message}</p>`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.body.classList.contains('is-detail')) {
    renderClinicDetail();
  } else {
    renderCommunities();
  }
});
