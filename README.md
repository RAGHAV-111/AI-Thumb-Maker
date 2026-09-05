<img width="1930" height="614" alt="image" src="https://github.com/user-attachments/assets/9bdec982-63a4-4e77-8286-27d8652f05d5" />
<img width="1118" height="1024" alt="image" src="https://github.com/user-attachments/assets/b8699041-5ec7-4081-b68d-b629c8a7f503" />

Here's how ThumbMaker works — it's a small full-stack app: vanilla HTML/JS frontend + FastAPI (Python) backend, with SQLite for storage and ImageKit as the image host.

Architecture
Frontend (index.html, script.js): plain HTML/CSS/JS, no framework, talking to the backend at http://localhost:8000.
Backend (main.py): FastAPI app with CORS wide open (allow_origins=["*"]).
Database: SQLite file thumbnailbuilder.db via SQLAlchemy (database.py, models.py) — one table thumbnails (id, title, prompt, image_url, created_at).
Image storage: ImageKit — a hosted image CDN — configured via a private key in .env/config.py.
The "generate thumbnail" flow (main.py:47-86)
User fills in Title + Prompt in the form and submits.
Frontend POSTs {title, prompt} to /thumbnails/generate.
Backend calls Pollinations.ai (https://image.pollinations.ai/prompt/<url-encoded-prompt>) — a free public text-to-image AI API — requesting a 1024×1024 image. This is the actual "AI" step: diffusion-model image generation from your text prompt, no API key needed.
The returned image bytes are uploaded to ImageKit under /thumbmaker/<random-uuid>.jpg, which returns a public CDN URL.
A Thumbnail row is saved to SQLite with title, prompt, and that image URL, and returned to the frontend.
Frontend re-fetches /thumbnails and renders the gallery (each card: image, title, Edit/Download/Delete buttons).
The in-browser photo editor (client-side only, in script.js)
Clicking Edit opens a <canvas>-based editor — no AI involved here:
