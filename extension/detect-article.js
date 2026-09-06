// Runs automatically on every page, once the page has mostly finished loading
// (see "run_at": "document_idle" in manifest.json).
// Job: cheaply decide "is this a news article?", and if so, send its
// title/url/description to the background service worker.
//
// Keep this file fast — it runs on every single page you visit, even ones
// that have nothing to do with news.

function isLikelyArticle() {
  // 1. Check for schema.org NewsArticle markup.
  // Most major news sites embed this as JSON inside a <script type="application/ld+json"> tag,
  // specifically so that search engines / tools like this can identify article pages.
  const ldJsonBlocks = document.querySelectorAll('script[type="application/ld+json"]');
  for (const block of ldJsonBlocks) {
    try {
      const data = JSON.parse(block.textContent);
      const type = data['@type'] || (Array.isArray(data) && data[0]?.['@type']);
      if (type && String(type).toLowerCase().includes('article')) {
        return true;
      }
    } catch (e) {
      // Malformed JSON-LD on the page — ignore it and keep checking other signals.
    }
  }

  // 2. Check the og:type meta tag (used for link previews on social media).
  const ogType = document.querySelector('meta[property="og:type"]');
  if (ogType && ogType.content === 'article') {
    return true;
  }

  // 3. Fallback: an <article> tag with a substantial amount of text.
  // This catches sites that don't bother with the metadata above.
  const articleEl = document.querySelector('article');
  if (articleEl && articleEl.innerText.length > 500) {
    return true;
  }

  return false;
}

function extractArticleMeta() {
  const title =
    document.querySelector('meta[property="og:title"]')?.content ||
    document.title;

  const description =
    document.querySelector('meta[property="og:description"]')?.content ||
    document.querySelector('meta[name="description"]')?.content ||
    '';

  return {
    url: window.location.href,
    title,
    description,
  };
}

// Entry point: only do the extraction work if this actually looks like an article.
if (isLikelyArticle()) {
  const meta = extractArticleMeta();
  console.log('[Kaleido] Article detected:', meta); // helpful while testing — remove later
  chrome.runtime.sendMessage({ type: 'ARTICLE_DETECTED', payload: meta });
}