const BASE_URL = 'http://localhost:8000';

const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');
const refreshEl = document.getElementById('refresh');

async function fetchRelatedArticles({ url, title, description, content, published_at, publisher }) {
  const response = await fetch(`${BASE_URL}/articles/related`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, title, description, content, published_at, publisher }),
  });

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`);
  }

  return response.json(); // expected shape: { related: [{ title, url, source, bias, confidence }, ...] }
}

function renderEmpty(message) {
  statusEl.dataset.state = 'empty';
  resultsEl.innerHTML = '';
  const li = document.createElement('li');
  li.className = 'empty';
  li.textContent = message;
  resultsEl.appendChild(li);
}

function renderResults(articles) {
  statusEl.dataset.state = 'results';
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

function setLoading() {
  statusEl.dataset.state = 'loading';
  statusEl.textContent = 'Finding coverage from other perspectives…';
  resultsEl.innerHTML = '<li class="loading" aria-label="Loading results"><span></span><span></span><span></span></li>';
}

async function load() {
  setLoading();
  chrome.runtime.sendMessage({ type: 'GET_CURRENT_ARTICLE' }, async (article) => {
    if (chrome.runtime.lastError || !article) {
      statusEl.dataset.state = 'empty';
      statusEl.textContent = "No article detected on this page.";
      renderEmpty('Open a news article, then try again.');
      return;
    }
    statusEl.textContent = `Coverage for “${article.title}”`;
    try {
      const { related = [] } = await fetchRelatedArticles(article);
      if (!related.length) {
        renderEmpty('No contrasting coverage found yet.');
        return;
      }
      renderResults(related);
    } catch (error) {
      statusEl.dataset.state = 'error';
      statusEl.textContent = 'Kaleido is unavailable.';
      renderEmpty('Start the local backend and try again.');
      console.error(error);
    }
  });
}

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

refreshEl.addEventListener('click', load);
load();