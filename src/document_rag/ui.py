"""Small local-only demo UI; no stored API key, no unsafe HTML insertion."""
HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Document RAG Assistant</title>
<style>
:root { color-scheme: dark; font: 16px/1.5 system-ui, sans-serif; background: #0b1220; color: #e9eefb; }
body { max-width: 1080px; margin: 0 auto; padding: 32px 20px; }
h1 { margin-bottom: 0; font-size: 2rem; } p { color: #aec0d7; }
section { border: 1px solid #32415a; border-radius: 14px; padding: 20px; margin: 18px 0; background: #142137; }
label { display: block; margin: 8px 0; }
input, select, textarea, button { font: inherit; border-radius: 8px; padding: 10px; }
input, select, textarea { color: #fff; background: #0a172a; border: 1px solid #455875; width: 100%; box-sizing: border-box; }
button { background: #6ee7b7; color: #072017; font-weight: 700; cursor: pointer; border: 0; margin: 8px 8px 8px 0; }
button:disabled { opacity: .55; cursor: wait; } article { border-top: 1px solid #42536a; padding: 12px 0; overflow-wrap: anywhere; }
small { color: #b3c2d8; } #answer { white-space: pre-wrap; overflow-wrap: anywhere; }
#error { color: #ffbac6; min-height: 1.6rem; }
</style></head><body>
<h1>Document RAG Assistant</h1>
<p>Upload PDFs and ask questions with traceable source excerpts.
Default local mode is a deterministic lexical baseline, not a semantic LLM.</p>
<section>
<label>API key (kept only in this tab, never saved)
<input id="key" type="password" autocomplete="off" placeholder="RAG_API_KEY"></label>
<label>PDF <input id="pdf" type="file" accept=".pdf,application/pdf"></label>
<button id="upload">Upload and index</button><button id="refresh">Refresh documents</button>
<div id="documents"></div></section>
<section>
<label>Question<textarea id="question" rows="3" placeholder="What does the document say about ...?"></textarea></label>
<label>Search strategy<select id="mode"><option value="hybrid">Hybrid</option>
<option value="vector">Vector</option><option value="text">Text</option></select></label>
<button id="ask">Ask</button><button id="search">Inspect retrieval</button>
<p id="busy" aria-live="polite"></p><p id="error" role="alert"></p>
<h2>Response</h2><div id="answer"></div><h2>Sources</h2><div id="sources"></div>
</section>
<script>
const el = (id) => document.getElementById(id);
async function request(path, options = {}) {
  const headers = {"X-API-Key": el("key").value, ...(options.headers || {})};
  const response = await fetch(path, {...options, headers});
  if (!response.ok) {
    const message = await response.json().catch(() => ({}));
    throw new Error(message.detail || "Request failed (" + response.status + ")");
  }
  return response.status === 204 ? null : response.json();
}
async function run(label, operation) {
  el("error").textContent = ""; el("busy").textContent = label;
  document.querySelectorAll("button").forEach((button) => button.disabled = true);
  try { await operation(); }
  catch (error) { el("error").textContent = String(error.message || error); }
  finally {
    el("busy").textContent = "";
    document.querySelectorAll("button").forEach((button) => button.disabled = false);
  }
}
async function refresh() {
  const data = await request("/documents");
  const box = el("documents"); box.replaceChildren();
  data.forEach((doc) => {
    const item = document.createElement("article");
    item.textContent = doc.filename + " | " + doc.page_count + " pages | " + doc.status;
    box.appendChild(item);
  });
  if (!data.length) box.textContent = "No documents indexed.";
}
function showSources(sources, isSearch) {
  const box = el("sources"); box.replaceChildren();
  sources.forEach((source) => {
    const item = document.createElement("article");
    const title = document.createElement("strong");
    title.textContent = (source.source_id || "Match") + " | " + source.filename + " | page " + source.page;
    const quote = document.createElement("p");
    quote.textContent = source.excerpt || source.text;
    item.append(title, quote);
    if (isSearch) {
      const detail = document.createElement("small");
      detail.textContent = "Score: " + source.score.toFixed(4);
      item.appendChild(detail);
    }
    box.appendChild(item);
  });
}
el("refresh").onclick = () => run("Loading...", refresh);
el("upload").onclick = () => run("Indexing PDF...", async () => {
  if (!el("pdf").files.length) throw new Error("Choose a PDF first.");
  const data = new FormData(); data.append("file", el("pdf").files[0]);
  await request("/documents", {method: "POST", body: data}); await refresh();
});
async function query(isSearch) {
  const payload = {question: el("question").value, mode: el("mode").value, top_k: 5};
  const response = await request(isSearch ? "/search" : "/ask", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  el("answer").textContent = isSearch ? response.hits.length + " matching chunks" : response.answer;
  showSources(isSearch ? response.hits : response.citations, isSearch);
}
el("ask").onclick = () => run("Generating...", () => query(false));
el("search").onclick = () => run("Searching...", () => query(true));
</script></body></html>"""