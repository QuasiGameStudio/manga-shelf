# MangaShelf

A manga / webtoon reader web app. Library of series → chapter list → vertical
scroll reader (long strip made of multiple page images).

**All page content is currently DUMMY art** (generated SVG placeholders).

## Structure

- `index.html` / `style.css` / `app.js` — the app (vanilla JS, no build step)
- `assets/manga/data.js` — manifest: series → chapters → pages (GENERATED)
- `assets/manga/<series>/cover.svg` — dummy cover
- `assets/manga/<series>/c<N>/p<NNN>.svg` — dummy pages (one file per page)
- `tools/gen_dummy.py` — regenerates all dummy content + data.js

## Features

- Library: search, tag filter, continue-reading shortcuts, per-series progress %
- Series page: synopsis, chapter list with read/progress states
- Reader: webtoon-style vertical strip of page images, lazy loading,
  reserved page heights (no layout jump), page indicator, top progress bar,
  auto-hiding bars, tap to toggle bars, end-of-chapter next/prev navigation,
  resume-where-you-left-off (localStorage) and library "Continue" badges.

## Swap in real art later

Replace the SVGs under `assets/manga/<series>/c<N>/` with real page images
(PNG/JPG/WebP) and update `assets/manga/data.js` (paths + w/h). The reader
treats every page as an independent `<img>` in a vertical strip.

## Run locally

```
cd manga-shelf
python -m http.server 8931
# open http://localhost:8931/
```

## Deploy

Mirrored into the gameorchestrator-workspace repo as `apps/manga-shelf/` with a
`games/manga-shelf/gradlew` shim (copies the app into `html/build/dist/`), then
shipped by the repo's WebGL workflow to
`https://storage.googleapis.com/game-list/games/manga-shelf/index.html`.
