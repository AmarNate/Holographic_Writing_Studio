# The Push&Pull — Holographic Writing Studio (`a1.6`)

A zero-dependency, single-file holographic writing environment built for crafting multi-chamber personal essays and audio-synced reviews—created around **_The Push&Pull, Glitches, and the Shrouded Guardian_** by **Nate** ([@IZ.NENAD.AN](https://www.instagram.com/reel/DgB-TvyIf9D/?lqvp=MWF0cXRsNGN5emoxaQ==)).

---

## Architecture & Highlights

- **Single-File Portability (`index.html`):** All markup, styling, spatial particle canvas, SVG orbital geometry, and state logic live inside one self-contained HTML file—no build step, bundler, or external CDN required.
- **RGB Triple-Shield Hologram UI:** Custom CSS token matrix (`--rgb-r`, `--rgb-g`, `--rgb-b`, `--holo`, `--veil`) with mood-reactive chapter states, slice-glitch bursts, and a live skin switcher.
- **Multi-Chamber & Multi-Piece Vault:**
  - Dedicated **Cover & Title** chamber (`0. Cover & Title`) with customizable hero artwork, external reel links, and an interactive Table of Contents.
  - Structured chapters and sub-chambers with latched formatting relays (**Bold**, **Italic**, **Blockquote**, **Serif / Sans / Mono**), **Typewriter Flow**, **Echo Check**, and per-chamber **Unsaid Pockets**.
  - Separate **Piece** switcher and **+ New** piece creator backed by browser `localStorage`.
- **KAIA — 22hrs Audio Dome:** Local MP3 loader with live timecode scrubbing, synced lyric sheet, and one-click timestamp cue chips (`Ctrl+Shift+K`) stamped straight into your draft.
- **Rich Media & Multi-Format Export:**
  - Drag-and-drop, clipboard paste, or `+Pic` insertion for visual frames with saved caption presets and width toggles (`100%` / `72%` / `48%`).
  - Export to **Standalone Holographic HTML** (with an interactive left-rail TOC and page-by-page navigation), **Holographic Print PDF**, **Markdown (`.md`)**, or full **Vault Backup (`.json`)**.

---

## Running Locally

Because the studio has zero external dependencies, you can run it immediately:

1. Clone or download this repository.
2. Open `index.html` directly in any modern browser (Chrome, Edge, Firefox, Safari).

*(Optional)* To serve it locally over HTTP:

```bash
python -m http.server 8080
```

Then visit `http://localhost:8080`.

---

## Hosting on GitHub Pages

1. Push `index.html`, `README.md`, `.gitignore`, and `LICENSE` to your GitHub repository.
2. Go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**, select `main` (and `/ (root)`), and click **Save**.
4. Your studio will go live at `https://<your-username>.github.io/<repo-name>/`.

---

## Data & Privacy Note

All writing, custom skins, and embedded images are stored locally inside your browser's `localStorage`. Nothing is sent to a server. If you clear browser site data or switch devices, use **Export → Export Full Vault Backup (`.json`)** to back up your work.