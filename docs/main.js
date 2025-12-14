(async function init() {
  const districtContainer = document.getElementById('district-list');
  try {
    const [dentists, ratings] = await Promise.all([
      fetch('data/dentists.json').then((r) => r.json()),
      fetch('ratings.json').then((r) => r.json()),
    ]);

    const grouped = dentists.reduce((acc, clinic) => {
      acc[clinic.district] = acc[clinic.district] || [];
      acc[clinic.district].push(clinic);
      return acc;
    }, {});

    const ratingText = (slug) => {
      const entry = ratings[slug];
      if (!entry) return '尚無資料';
      if (entry.rating) return `${entry.rating} ★`;
      return entry.note || '尚無資料';
    };

    districtContainer.innerHTML = Object.entries(grouped)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([district, clinics]) => {
        const clinicCards = clinics
          .map((clinic) => {
            const rating = ratingText(clinic.slug);
            return `
              <article class="clinic-card">
                <div class="clinic-card__header">
                  <h4>${clinic.name}</h4>
                  <span class="meta">${rating}</span>
                </div>
                <div class="meta">${clinic.address}</div>
                <div class="actions">
                  <a class="button" href="clinics/${clinic.slug}.html">拜訪專頁</a>
                  <a class="button button--ghost" href="${clinic.mapUrl}" target="_blank" rel="noreferrer">
                    <span class="icon" aria-hidden="true">📍</span> Google 地圖
                  </a>
                </div>
              </article>
            `;
          })
          .join('');

        return `
          <section class="district">
            <h3>${district}</h3>
            <div class="clinic-list">${clinicCards}</div>
          </section>
        `;
      })
      .join('');
  } catch (error) {
    console.error('無法載入診所資料', error);
    districtContainer.innerHTML = '<p>無法載入資料，請稍後再試。</p>';
  }
})();
