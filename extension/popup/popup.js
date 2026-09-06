const BASE_URL = 'http://localhost:8000';

const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');

async function fetchRelatedArticles({ url, title, description }) {
  const response = await fetch(`${BASE_URL}/articles/related`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, title, description }),
  });

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`);
  }

  return response.json(); // expected shape: { related: [{ title, url, source, bias, confidence }, ...] }
}

function renderEmpty(message) {
  resultsEl.innerHTML = '';
  const li = document.createElement('li');
  li.className = 'empty';
  li.textContent = message;
  resultsEl.appendChild(li);
}

function renderResults(articles) {
  resultsEl.innerHTML = '';

  articles.forEach((a) => {
    const bias = (a.bias || 'center').toLowerCase(); // "left" | "center" | "right"
    const confidencePct = a.confidence != null ? Math.round(a.confidence * 100) : null;

    const li = document.createElement('li');

    const link = document.createElement('a');
    link.className = 'result';
    link.href = a.url;
    link.target = '_blank';

    link.innerHTML = `
      <div class="result__top">
        <span class="chip chip--${bias}">${capitalize(bias)}</span>
        <span class="result__outlet">${a.source}</span>
      </div>
      <div class="result__title">${a.title}</div>
      ${confidencePct != null ? `
        <div class="confidence">
          <div class="confidence__track">
            <div class="confidence__fill confidence__fill--${bias}" style="width: ${confidencePct}%"></div>
          </div>
          <span class="confidence__label">${confidencePct}%</span>
        </div>
      ` : ''}
    `;

    li.appendChild(link);
    resultsEl.appendChild(li);
  });
}

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

// --- Entry point ---
chrome.runtime.sendMessage({ type: 'GET_CURRENT_ARTICLE' }, async (article) => {
  if (!article) {
    statusEl.textContent = "This doesn't look like a news article.";
    return;
  }

  statusEl.textContent = `Other coverage of "${article.title}"`;

  try {
    const { related } = await fetchRelatedArticles(article);
    if (!related || related.length === 0) {
      renderEmpty('No alternate coverage found yet.');
      return;
    }
    renderResults(related);
  } catch (err) {
    statusEl.textContent = 'Reading the page…';
    renderEmpty('Could not reach the backend. Is it running?');
    console.error(err);
  }
});