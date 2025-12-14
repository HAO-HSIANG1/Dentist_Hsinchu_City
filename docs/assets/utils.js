function normalizeText(text) {
  return (text || '').trim().replace(/^﻿/, '');
}

function parseCSVLine(line) {
  const values = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (char === ',' && !inQuotes) {
      values.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  values.push(current);
  return values.map(normalizeText);
}

function parseCSV(text) {
  const lines = text.split(/\r?\n/).filter(Boolean);
  const [headerLine, ...rows] = lines;
  const headers = parseCSVLine(headerLine);
  return rows.map((line) => {
    const cols = parseCSVLine(line);
    return headers.reduce((obj, key, idx) => {
      obj[key] = cols[idx] || '';
      return obj;
    }, {});
  });
}

function extractCommunity(street) {
  const clean = normalizeText(street);
  const match = clean.match(/(.+?里)/);
  return match ? match[1] : '未分類';
}

function buildMapLink(name, street) {
  const query = encodeURIComponent(`${name} ${street}`);
  return `https://www.google.com/maps/search/?api=1&query=${query}`;
}

function clinicSlug(name, street) {
  const base = normalizeText(`${name}-${street}`).toLowerCase();
  let hash = 0;
  for (let i = 0; i < base.length; i++) {
    hash = (hash << 5) - hash + base.charCodeAt(i);
    hash |= 0; // force 32bit
  }
  const hex = Math.abs(hash).toString(16).slice(0, 6);
  return encodeURIComponent(normalizeText(name).replace(/\s+/g, '-')) + '-' + hex;
}

function formatPhone(phone) {
  return normalizeText(phone).replace(/[\s-]+/g, '');
}

function createStars(rating) {
  const stars = [];
  const value = Number(rating) || 0;
  for (let i = 1; i <= 5; i++) {
    const filled = value >= i - 0.5 ? '★' : '☆';
    stars.push(filled);
  }
  return stars.join(' ');
}

async function fetchGoogleRating(name, street) {
  if (!window.GOOGLE_MAPS_API_KEY) return null;
  const url = new URL('https://maps.googleapis.com/maps/api/place/findplacefromtext/json');
  url.searchParams.set('input', `${name} ${street}`);
  url.searchParams.set('inputtype', 'textquery');
  url.searchParams.set('fields', 'name,rating,user_ratings_total');
  url.searchParams.set('key', window.GOOGLE_MAPS_API_KEY);

  try {
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Network error');
    const data = await res.json();
    if (data?.candidates?.[0]) {
      return {
        rating: data.candidates[0].rating,
        total: data.candidates[0].user_ratings_total,
      };
    }
    return null;
  } catch (error) {
    console.error('Failed to load Google rating', error);
    return null;
  }
}

// Expose for optional dynamic loading without imports (used by inline scripts).
window.fetchGoogleRating = fetchGoogleRating;

function buildCoverPlaceholder(name) {
  const colors = ['#e0f2fe', '#ede9fe', '#fef3c7', '#dcfce7'];
  const color = colors[name.length % colors.length];
  const initials = normalizeText(name).slice(0, 2);
  const canvas = document.createElement('canvas');
  canvas.width = 1200;
  canvas.height = 630;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0f172a';
  ctx.font = 'bold 96px "Noto Sans TC"';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(initials, canvas.width / 2, canvas.height / 2);
  return canvas.toDataURL('image/png');
}

async function loadClinics() {
  const res = await fetch('./data/Dentist_Hsinchu_City.csv');
  const text = await res.text();
  const records = parseCSV(text);
  return records.map((row) => {
    const name = normalizeText(row['機構名稱']);
    const areaCode = normalizeText(row['行政區域代碼']);
    const street = normalizeText(row['街道項弄號']);
    const community = extractCommunity(street);
    return {
      name,
      areaCode,
      street,
      principal: normalizeText(row['負責人']),
      phone: normalizeText(row['電話']),
      cityCode: normalizeText(row['縣市別代碼']),
      community,
      slug: clinicSlug(name, street),
      cover: buildCoverPlaceholder(name),
    };
  });
}

function renderRatingElement(container, ratingData) {
  const rating = ratingData?.rating;
  const total = ratingData?.total;
  if (!rating) {
    container.textContent = 'Google 星等暫無資料';
    container.classList.add('meta-row');
    return;
  }
  const stars = createStars(rating);
  container.innerHTML = `
    <span class="icon" aria-hidden="true">⭐</span>
    <span class="rating">${Number(rating).toFixed(1)}</span>
    <span class="stars" aria-label="${rating} star rating">${stars}</span>
    <span class="meta-note">(${total || 0} 則評價)</span>
  `;
  container.classList.add('meta-row');
}

export {
  normalizeText,
  parseCSV,
  extractCommunity,
  buildMapLink,
  clinicSlug,
  formatPhone,
  createStars,
  fetchGoogleRating,
  buildCoverPlaceholder,
  loadClinics,
  renderRatingElement,
};
