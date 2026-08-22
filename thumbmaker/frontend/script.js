const API_BASE = "http://localhost:8000";

const form = document.getElementById("generate-form");
const statusEl = document.getElementById("status");
const gallery = document.getElementById("gallery");

function renderThumbnails(thumbnails) {
  gallery.innerHTML = "";
  for (const t of thumbnails) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <img src="${t.image_url}" alt="${t.title}" />
      <div class="card-body">
        <h3>${t.title}</h3>
      </div>
    `;
    gallery.appendChild(card);
  }
}

async function loadThumbnails() {
  try {
    const res = await fetch(`${API_BASE}/thumbnails`);
    if (!res.ok) throw new Error(await res.text());
    renderThumbnails(await res.json());
  } catch (err) {
    statusEl.textContent = `Failed to load thumbnails: ${err.message}`;
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("title").value;
  const prompt = document.getElementById("prompt").value;
  const button = form.querySelector("button");

  button.disabled = true;
  statusEl.textContent = "Generating thumbnail...";

  try {
    const res = await fetch(`${API_BASE}/thumbnails/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, prompt }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    statusEl.textContent = "Done!";
    form.reset();
    await loadThumbnails();
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  } finally {
    button.disabled = false;
  }
});

loadThumbnails();
