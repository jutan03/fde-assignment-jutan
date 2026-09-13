const MODE_LABELS = {
  embeddings: "Ranked with live embeddings",
  keyword: "Keyword match (AI gateway not configured)",
  "keyword-fallback": "Keyword match (AI gateway call failed)",
  empty: "Showing full catalogue",
};

const QNA_MODE_LABELS = {
  live: "Answered live by the model",
  simulated: "Simulated — gateway not configured",
  error: "Gateway error — see console",
};

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function cardHtml(item) {
  return `<a class="card" href="/item/${escapeHtml(item.id)}">
    <div class="card-emoji">${item.emoji}</div>
    <div class="card-title">${escapeHtml(item.title)}</div>
    <div class="card-meta">${escapeHtml(item.category)} · ${escapeHtml(item.condition)} · ${escapeHtml(item.location)}</div>
    <div class="card-price">$${item.price}</div>
  </a>`;
}

function renderResults(items) {
  const resultsEl = document.getElementById("results");
  if (!items.length) {
    resultsEl.innerHTML = '<div class="empty-state">No listings matched that search.</div>';
    return;
  }
  resultsEl.innerHTML = `<div class="grid">${items.map(cardHtml).join("")}</div>`;
}

async function runSearch(e) {
  e.preventDefault();
  const input = document.getElementById("search-input");
  const query = input.value.trim();
  const badge = document.getElementById("mode-badge");
  const btn = document.getElementById("search-btn");

  if (!query) {
    location.reload();
    return;
  }

  btn.disabled = true;
  btn.textContent = "Searching…";
  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    renderResults(data.results || []);
    badge.textContent = MODE_LABELS[data.mode] || data.mode;
    badge.style.display = "inline-block";
  } catch (err) {
    console.error(err);
  } finally {
    btn.disabled = false;
    btn.textContent = "Search";
  }
}

function turnHtml(question, answer, mode) {
  return `<div class="qna-turn">
    <div class="qna-question">Q: ${escapeHtml(question)}</div>
    <div class="qna-answer">${escapeHtml(answer)}</div>
    <div class="qna-tag">${QNA_MODE_LABELS[mode] || mode}</div>
  </div>`;
}

async function runQna(e) {
  e.preventDefault();
  const input = document.getElementById("qna-input");
  const question = input.value.trim();
  if (!question) return;
  input.value = "";

  const btn = document.getElementById("qna-btn");
  const thread = document.getElementById("qna-thread");
  btn.disabled = true;
  btn.textContent = "Thinking…";

  try {
    const res = await fetch("/api/qna", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    thread.insertAdjacentHTML("beforeend", turnHtml(question, data.answer, data.mode));
  } catch (err) {
    console.error(err);
    thread.insertAdjacentHTML(
      "beforeend",
      turnHtml(question, "Something went wrong reaching the assistant.", "error")
    );
  } finally {
    btn.disabled = false;
    btn.textContent = "Ask";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.getElementById("search-form");
  if (searchForm) searchForm.addEventListener("submit", runSearch);

  const qnaForm = document.getElementById("qna-form");
  if (qnaForm) qnaForm.addEventListener("submit", runQna);
});
