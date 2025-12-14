import { buildMapLink, loadClinics, renderRatingElement } from './utils.js';

const communityListEl = document.getElementById('community-list');
const searchInput = document.getElementById('search');
let clinics = [];

function createClinicCard(clinic) {
  const card = document.createElement('article');
  card.className = 'card';
  card.innerHTML = `
    <img src="${clinic.cover}" alt="${clinic.name} 封面" class="clinic-cover" loading="lazy" />
    <div class="badge-group">
      <span class="badge">${clinic.community}</span>
      <span class="badge secondary">行政區域代碼 ${clinic.areaCode}</span>
    </div>
    <h3>${clinic.name}</h3>
    <div class="meta">
      <div class="meta-row"><span class="icon">📍</span>${clinic.street}</div>
      <div class="meta-row"><span class="icon">📞</span>${clinic.phone}</div>
      <div class="meta-row"><span class="icon">👤</span>${clinic.principal}</div>
      <div class="meta-row rating-row">載入 Google 星等中...</div>
    </div>
    <div class="actions">
      <a class="button" href="${buildMapLink(clinic.name, clinic.street)}" target="_blank" rel="noopener">🗺️ Google 地圖</a>
      <a class="button primary" href="./clinic.html?slug=${clinic.slug}">📄 獨立頁面</a>
    </div>
  `;

  const ratingRow = card.querySelector('.rating-row');
  fetchRating(clinic, ratingRow);

  return card;
}

async function fetchRating(clinic, ratingEl) {
  try {
    const ratingData = await window.fetchGoogleRating?.(clinic.name, clinic.street);
    renderRatingElement(ratingEl, ratingData);
  } catch (error) {
    console.error('Rating fetch failed', error);
    renderRatingElement(ratingEl, null);
  }
}

function renderCommunities(list) {
  communityListEl.innerHTML = '';
  const grouped = list.reduce((acc, clinic) => {
    acc[clinic.community] = acc[clinic.community] || [];
    acc[clinic.community].push(clinic);
    return acc;
  }, {});

  Object.entries(grouped)
    .sort(([a], [b]) => a.localeCompare(b, 'zh-Hant'))
    .forEach(([community, clinics]) => {
      const section = document.createElement('section');
      section.className = 'community-section';
      section.innerHTML = `
        <div class="community-header">
          <h3>${community}</h3>
          <span class="badge">${clinics.length} 間診所</span>
        </div>
        <div class="community-grid"></div>
      `;
      const grid = section.querySelector('.community-grid');
      clinics.forEach((clinic) => grid.appendChild(createClinicCard(clinic)));
      communityListEl.appendChild(section);
    });
}

function handleSearch(event) {
  const keyword = event.target.value.trim();
  const filtered = clinics.filter((clinic) =>
    [clinic.name, clinic.community, clinic.street].some((field) => field.includes(keyword))
  );
  renderCommunities(filtered);
}

async function init() {
  clinics = await loadClinics();
  renderCommunities(clinics);
  searchInput.addEventListener('input', handleSearch);
}

init();
