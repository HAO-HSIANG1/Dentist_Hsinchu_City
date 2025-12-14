(async function attachRating() {
  const ratingElement = document.querySelector('.rating');
  if (!ratingElement) return;
  const slug = ratingElement.getAttribute('data-slug');
  try {
    const ratings = await fetch('../ratings.json').then((r) => r.json());
    const entry = ratings[slug];
    const valueElement = ratingElement.querySelector('.rating__value');
    if (!valueElement) return;

    if (entry?.rating) {
      valueElement.textContent = `${entry.rating} ★`;
      valueElement.dataset.hasRating = 'true';
    } else {
      valueElement.textContent = entry?.note || '尚未提供星等，請點擊地圖查看最新評論';
      valueElement.dataset.hasRating = 'false';
    }
  } catch (error) {
    console.error('無法載入評分資料', error);
  }
})();
