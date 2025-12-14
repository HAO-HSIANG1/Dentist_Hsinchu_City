async function loadClinics() {
  const res = await fetch('data/clinics.json');
  if (!res.ok) throw new Error('無法載入診所資料');
  const clinics = await res.json();
  return clinics.map((clinic, index) => ({
    ...clinic,
    id: index,
    googleRating: clinic.googleRating ?? null,
  }));
}

function groupByCommunity(clinics) {
  return clinics.reduce((map, clinic) => {
    const community = clinic.community || '未分類';
    if (!map.has(community)) map.set(community, []);
    map.get(community).push(clinic);
    return map;
  }, new Map());
}

function createStarText(rating) {
  if (!rating) return { text: '請至 Google 地圖查看', stars: '☆☆☆☆☆' };
  const rounded = Math.round(rating);
  const stars = '★★★★★'.slice(0, rounded) + '☆☆☆☆☆'.slice(rounded);
  return { text: `${rating.toFixed(1)} / 5`, stars };
}

function applyCover(card, index) {
  const hue = (index * 47) % 360;
  card.querySelector('.cover').style.background = `linear-gradient(135deg, hsl(${hue}, 75%, 90%), hsl(${hue}, 85%, 82%))`;
}

function buildClinicCard(clinic, index) {
  const template = document.getElementById('clinic-card-template');
  const fragment = template.content.cloneNode(true);
  fragment.querySelector('.clinic-name').textContent = clinic.name;
  fragment.querySelector('.clinic-owner').textContent = `負責人：${clinic.owner}`;
  fragment.querySelector('.clinic-address').textContent = clinic.address;
  fragment.querySelector('.phone').textContent = clinic.phone;
  fragment.querySelector('.clinic-community').textContent = clinic.community;
  fragment.querySelector('.button[href^="tel:"]').setAttribute('href', `tel:${clinic.phone.replace(/[^0-9+]/g, '')}`);

  const mapLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(clinic.name + ' ' + clinic.address)}`;
  fragment.querySelector('[data-map-link]').setAttribute('href', mapLink);

  const { text, stars } = createStarText(clinic.googleRating);
  fragment.querySelector('.rating-value').textContent = text;
  fragment.querySelector('.rating-stars').textContent = stars;

  const card = fragment.querySelector('.clinic-card');
  applyCover(card, index);
  return fragment;
}

function renderCommunities(grouped) {
  const container = document.getElementById('communities');
  container.innerHTML = '';

  const communities = Array.from(grouped.keys()).sort();
  communities.forEach((community) => {
    const clinics = grouped.get(community) || [];
    const panel = document.createElement('section');
    panel.className = 'community-panel';

    const header = document.createElement('div');
    header.className = 'community-header';
    const title = document.createElement('h2');
    title.textContent = community;
    const count = document.createElement('span');
    count.className = 'community-count';
    count.textContent = `${clinics.length} 間診所`;
    header.append(title, count);
    panel.appendChild(header);

    const list = document.createElement('div');
    list.className = 'clinic-list';
    clinics.forEach((clinic, index) => list.appendChild(buildClinicCard(clinic, index)));
    panel.appendChild(list);

    container.appendChild(panel);
  });
}

function populateSelect(grouped) {
  const select = document.getElementById('communityFilter');
  select.innerHTML = '';
  const allOption = document.createElement('option');
  allOption.value = 'all';
  allOption.textContent = '全部社區';
  select.appendChild(allOption);

  Array.from(grouped.keys())
    .sort()
    .forEach((community) => {
      const option = document.createElement('option');
      option.value = community;
      option.textContent = community;
      select.appendChild(option);
    });
}

function filterCommunities(originalGrouped, selected) {
  if (selected === 'all') return originalGrouped;
  const map = new Map();
  if (originalGrouped.has(selected)) {
    map.set(selected, originalGrouped.get(selected));
  }
  return map;
}

async function init() {
  try {
    const clinics = await loadClinics();
    const grouped = groupByCommunity(clinics);
    populateSelect(grouped);
    renderCommunities(grouped);

    document.getElementById('communityFilter').addEventListener('change', (event) => {
      const filtered = filterCommunities(grouped, event.target.value);
      renderCommunities(filtered);
    });
  } catch (err) {
    const container = document.getElementById('communities');
    container.textContent = err.message;
  }
}

init();
