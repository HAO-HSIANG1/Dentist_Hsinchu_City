import { buildMapLink, loadClinics, renderRatingElement } from './utils.js';

const params = new URLSearchParams(window.location.search);
const slug = params.get('slug');

const nameEl = document.getElementById('clinic-name');
const addressEl = document.getElementById('address');
const principalEl = document.getElementById('principal');
const phoneEl = document.getElementById('phone');
const communityEl = document.getElementById('community');
const areaEl = document.getElementById('area');
const coverEl = document.getElementById('cover');
const mapLinkEl = document.getElementById('map-link');
const ratingEl = document.getElementById('rating');

function showNotFound() {
  nameEl.textContent = '找不到診所資料';
  document.querySelector('.meta').style.display = 'none';
  document.querySelector('.actions').style.display = 'none';
}

async function fetchRating(clinic) {
  try {
    const ratingData = await window.fetchGoogleRating?.(clinic.name, clinic.street);
    renderRatingElement(ratingEl, ratingData);
  } catch (error) {
    console.error('Rating fetch failed', error);
    renderRatingElement(ratingEl, null);
  }
}

async function init() {
  const clinics = await loadClinics();
  const clinic = clinics.find((item) => item.slug === slug);
  if (!clinic) return showNotFound();

  nameEl.textContent = clinic.name;
  addressEl.textContent = clinic.street;
  principalEl.textContent = clinic.principal;
  phoneEl.textContent = clinic.phone;
  communityEl.textContent = clinic.community;
  areaEl.textContent = `行政區域代碼 ${clinic.areaCode}`;
  coverEl.src = clinic.cover;
  mapLinkEl.href = buildMapLink(clinic.name, clinic.street);

  await fetchRating(clinic);
}

init();
