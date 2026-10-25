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

    const top = document.createElement('div');
    top.className = 'result__top';
    const chip = document.createElement('span');
    chip.className = `chip chip--${bias}`;
    chip.textContent = capitalize(bias);
    const outlet = document.createElement('span');
    outlet.className = 'result__outlet';
    outlet.textContent = a.source || 'Unknown source';
    top.append(chip, outlet);

    const title = document.createElement('div');
    title.className = 'result__title';
    title.textContent = a.title || 'Untitled article';
    link.appendChild(top);
    link.appendChild(title);

    if (confidencePct != null) {
      const confidence = document.createElement('div');
      confidence.className = 'confidence';
      const track = document.createElement('div');
      track.className = 'confidence__track';
      const fill = document.createElement('div');
      fill.className = `confidence__fill confidence__fill--${bias}`;
      fill.style.width = `${confidencePct}%`;
      track.appendChild(fill);
      const label = document.createElement('span');
      label.className = 'confidence__label';
      label.textContent = `${confidencePct}%`;
      confidence.append(track, label);
      link.appendChild(confidence);
    }

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