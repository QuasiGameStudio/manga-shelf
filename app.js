/* MangaShelf — vanilla JS manga reader app. Hash routing:  #/  #/series/<id>  #/read/<sid>/<ch> */
(() => {
  "use strict";

  const DATA = window.MANGA_DATA;
  const app = document.getElementById("app");

  if (!DATA || !DATA.series || !DATA.series.length) {
    app.innerHTML = '<div class="boot">No manga data found (assets/manga/data.js)</div>';
    return;
  }

  /* ---------------- progress store ---------------- */
  const LS_KEY = "mangashelf.progress.v1";
  const store = {
    read() {
      try { return JSON.parse(localStorage.getItem(LS_KEY)) || {}; }
      catch (e) { return {}; }
    },
    get(sid) { return this.read()[sid] || {}; },
    setEntry(sid, ch, entry) {
      const all = this.read();
      all[sid] = all[sid] || {};
      all[sid][ch] = entry;
      try { localStorage.setItem(LS_KEY, JSON.stringify(all)); } catch (e) { /* ignore */ }
    },
    latest(sid) {
      const chs = this.get(sid);
      let best = null;
      for (const k of Object.keys(chs)) {
        const e = chs[k];
        if (!best || e.ts > best.e.ts) best = { ch: Number(k), e };
      }
      return best;
    },
  };

  const seriesById = id => DATA.series.find(s => s.id === id);
  const chapterCount = s => s.chapters.length;
  const pageCount = (s, ch) => (s.chapters[ch - 1] ? s.chapters[ch - 1].pages.length : 0);
  const chEntry = (sid, ch) => store.get(sid)[ch] || null;
  const chRead = (sid, ch) => {
    const e = chEntry(sid, ch);
    return !!e && e.p >= pageCount(seriesById(sid), ch);
  };
  const seriesProgressPct = s => {
    let total = 0, done = 0;
    s.chapters.forEach((c, i) => {
      total += c.pages.length;
      const e = chEntry(s.id, i + 1);
      done += e ? Math.min(e.p, c.pages.length) : 0;
    });
    return total ? Math.round(done / total * 100) : 0;
  };
  const esc = s => String(s).replace(/[&<>"']/g, c => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ---------------- routing ---------------- */
  function parseRoute() {
    const h = location.hash.replace(/^#\/?/, "");
    const parts = h.split("/").filter(Boolean);
    if (parts[0] === "series" && parts[1]) return { name: "series", sid: parts[1] };
    if (parts[0] === "read" && parts[1]) {
      return { name: "read", sid: parts[1], ch: Math.max(1, parseInt(parts[2], 10) || 1) };
    }
    return { name: "library" };
  }

  function go(hash) {
    if (location.hash === hash) render();
    else location.hash = hash;
  }

  window.addEventListener("hashchange", render);
  /* we manage scroll ourselves (chapter restore / top reset) — stop the browser
     from re-restoring the old offset after hash navigation */
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";

  let readerCleanup = null;

  function render() {
    const r = parseRoute();
    if (readerCleanup) { readerCleanup(); readerCleanup = null; }
    document.body.classList.toggle("reading", r.name === "read");
    app.classList.toggle("reader-mode", r.name === "read");
    if (r.name === "library") renderLibrary();
    else if (r.name === "series") renderSeries(r.sid);
    else renderReader(r.sid, r.ch);
  }

  /* ---------------- library ---------------- */
  const libState = { q: "", tag: "All" };

  function renderLibrary() {
    document.title = "MangaShelf";
    const tags = ["All"];
    DATA.series.forEach(s => s.tags.forEach(t => { if (!tags.includes(t)) tags.push(t); }));

    const contItems = DATA.series
      .map(s => ({ s, st: store.latest(s.id) }))
      .filter(x => x.st && x.st.e.p > 0)
      .slice(0, 8);

    app.innerHTML = `
      <header class="topbar">
        <span class="logo"><span class="flag">M</span>MangaShelf</span>
        <span class="spacer"></span>
        <span class="sub">${DATA.series.length} series</span>
      </header>
      <div class="search-wrap">
        <input id="q" class="search" type="search" placeholder="Search title, author, tag…"
               value="${esc(libState.q)}" autocomplete="off">
      </div>
      <div class="chips" id="chips">
        ${tags.map(t => `<button class="chip ${t === libState.tag ? "on" : ""}" data-tag="${esc(t)}">${esc(t)}</button>`).join("")}
      </div>
      <div id="cont-sec"></div>
      <div class="grid" id="grid"></div>
      <div class="empty" id="empty" hidden>Nothing matches that search.</div>
    `;

    renderContSection(contItems);
    renderGrid();

    const q = document.getElementById("q");
    q.addEventListener("input", () => {
      libState.q = q.value;
      renderGrid();
    });
    document.getElementById("chips").addEventListener("click", ev => {
      const b = ev.target.closest(".chip");
      if (!b) return;
      libState.tag = b.dataset.tag;
      render();
    });
  }

  function renderContSection(contItems) {
    const sec = document.getElementById("cont-sec");
    if (!contItems.length) { sec.innerHTML = ""; return; }
    sec.innerHTML = `
      <div class="section-label">Continue reading</div>
      <div class="chips" id="cont-chips">
        ${contItems.map(({ s, st }) => `
          <button class="chip" data-cont="${esc(s.id)}" style="padding:8px 14px;">
            ● ${esc(s.title)} · Ch ${st.ch}
          </button>`).join("")}
      </div>`;
    sec.querySelector(".chips").addEventListener("click", ev => {
      const b = ev.target.closest("[data-cont]");
      if (!b) return;
      const st = store.latest(b.dataset.cont);
      if (st) go(`#/read/${b.dataset.cont}/${st.ch}`);
    });
  }

  function renderGrid() {
    const grid = document.getElementById("grid");
    const empty = document.getElementById("empty");
    const ql = libState.q.trim().toLowerCase();
    const items = DATA.series.filter(s => {
      const tagOk = libState.tag === "All" || s.tags.includes(libState.tag);
      const qOk = !ql ||
        s.title.toLowerCase().includes(ql) ||
        s.author.toLowerCase().includes(ql) ||
        s.tags.join(" ").toLowerCase().includes(ql);
      return tagOk && qOk;
    });
    empty.hidden = items.length > 0;
    grid.innerHTML = items.map(s => {
      const pct = seriesProgressPct(s);
      const latest = store.latest(s.id);
      const badge = latest && latest.e.p > 0 && !chRead(s.id, latest.ch)
        ? `<div class="cont">Continue <b>Ch ${latest.ch}</b> · ${latest.e.p}/${pageCount(s, latest.ch)}
             <span class="pbar"><i style="width:${pct}%"></i></span></div>`
        : (pct >= 100 ? '<div class="cont">✓ Finished</div>' : "");
      return `
        <a class="mcard" href="#/series/${esc(s.id)}">
          <div class="cover-box">
            <img src="${esc(s.cover)}" alt="${esc(s.title)} cover" loading="lazy">
            ${badge}
          </div>
          <div class="meta">
            <div class="t">${esc(s.title)}</div>
            <div class="a">${esc(s.author)}</div>
            <div class="n">${chapterCount(s)} chapter${chapterCount(s) > 1 ? "s" : ""} · ${pct}% read</div>
          </div>
        </a>`;
    }).join("");
  }

  /* ---------------- series detail ---------------- */
  function renderSeries(sid) {
    const s = seriesById(sid);
    if (!s) { app.innerHTML = '<div class="boot">Unknown series. <a href="#/">Back to shelf</a></div>'; return; }
    document.title = `${s.title} — MangaShelf`;
    const latest = store.latest(sid);

    app.innerHTML = `
      <header class="topbar">
        <button class="back-btn" id="back" aria-label="Back">‹</button>
        <div style="min-width:0">
          <div class="tb-title">${esc(s.title)}</div>
          <div class="tb-sub">${chapterCount(s)} chapters</div>
        </div>
      </header>
      <div class="hero">
        <div class="cv"><img src="${esc(s.cover)}" alt=""></div>
        <div class="hi">
          <h1>${esc(s.title)}</h1>
          <div class="by">by ${esc(s.author)}</div>
          <div class="tags">${s.tags.map(t => `<span class="tag">${esc(t)}</span>`).join("")}</div>
        </div>
      </div>
      <p class="syn">${esc(s.synopsis)}</p>
      <div class="cont-btn-row" id="cont-row"></div>
      <div class="ch-list" id="ch-list"></div>
    `;

    renderContBtn(s, latest);
    renderChList(s);
    document.getElementById("back").addEventListener("click", () => go("#/"));
  }

  function renderContBtn(s, latest) {
    const row = document.getElementById("cont-row");
    let targetCh = 1;
    if (latest && latest.e.p > 0 && !chRead(s.id, latest.ch)) targetCh = latest.ch;
    else if (latest) targetCh = Math.min(latest.ch + 1, chapterCount(s));
    row.innerHTML = `<button class="cont-btn" id="cont-btn">${
      latest && latest.e.p > 0 ? `Continue — Chapter ${targetCh}` : "Start reading"
    }</button>`;
    row.querySelector("#cont-btn").addEventListener("click", () => go(`#/read/${s.id}/${targetCh}`));
  }

  function renderChList(s) {
    document.getElementById("ch-list").innerHTML = s.chapters.map((c, i) => {
      const ch = i + 1;
      const e = chEntry(s.id, ch);
      const read = chRead(s.id, ch);
      const inProg = e && !read && e.p > 0;
      const pct = e ? Math.min(100, Math.round(e.p / c.pages.length * 100)) : 0;
      return `
        <div class="ch-row ${read ? "read" : ""}" data-ch="${ch}">
          <div class="ch-num">${read ? "✓" : ch}</div>
          <div class="ch-main">
            <div class="ch-t">Ch ${ch} · ${esc(c.title)}</div>
            <div class="ch-p">${c.pages.length} pages</div>
            ${inProg ? `<div class="ch-prog"><i style="width:${pct}%"></i></div>` : ""}
          </div>
          <div class="ch-state ${read ? "rd" : ""}">${read ? "Read" : (inProg ? `${pct}%` : "")}</div>
        </div>`;
    }).join("");
    document.getElementById("ch-list").addEventListener("click", ev => {
      const row = ev.target.closest(".ch-row");
      if (row) go(`#/read/${s.id}/${row.dataset.ch}`);
    });
  }

  /* ---------------- reader ---------------- */
  function renderReader(sid, ch) {
    const s = seriesById(sid);
    if (!s) { app.innerHTML = '<div class="boot">Unknown series. <a href="#/">Back</a></div>'; return; }
    const c = s.chapters[ch - 1];
    if (!c) { app.innerHTML = '<div class="boot">No such chapter. <a href="#/">Back</a></div>'; return; }
    document.title = `${s.title} Ch ${ch} — MangaShelf`;

    const prevCh = ch > 1 ? ch - 1 : null;
    const nextCh = ch < chapterCount(s) ? ch + 1 : null;

    app.innerHTML = `
      <div class="reader">
        <div class="rprog"><i id="rp"></i></div>
        <header class="rtop" id="rtop">
          <button class="back-btn" id="rback" aria-label="Back">‹</button>
          <div class="tt">
            <div class="tb-title">${esc(s.title)}</div>
            <div class="tb-sub">Chapter ${ch} · ${esc(c.title)}</div>
          </div>
        </header>
        <div class="strip" id="strip">
          ${c.pages.map((p, i) => `
            <img src="${esc(p.src)}" alt="Page ${i + 1}"
                 style="aspect-ratio:${p.w}/${p.h}"
                 ${i > 1 ? 'loading="lazy"' : ""}>`).join("")}
          <div class="endcard">
            <div class="big">End of Chapter ${ch}</div>
            <div class="dim">${esc(s.title)}</div>
            ${nextCh ? `<button class="next-btn" id="next">Next: Chapter ${nextCh} →</button>` : ""}
            ${prevCh ? `<button class="ghost-btn" id="prev">← Chapter ${prevCh}</button>` : ""}
            <br><button class="ghost-btn" id="toseries">Back to chapter list</button>
          </div>
        </div>
        <div class="page-ind" id="pind">1 / ${c.pages.length}</div>
        <footer class="rbot" id="rbot">
          <button class="ghost-btn" style="padding:9px 16px;font-size:13px;margin:0" id="chlist">Chapters</button>
          <span class="tb-sub" style="color:#aab2c8">Ch ${ch} / ${chapterCount(s)}</span>
          <button class="next-btn" style="padding:9px 16px;font-size:13px;margin:0" id="nextb" ${nextCh ? "" : "disabled"}>
            ${nextCh ? "Next chapter" : "Last chapter"}
          </button>
        </footer>
        <div class="toast" id="toast"></div>
      </div>
    `;

    const strip = document.getElementById("strip");
    const imgs = Array.from(strip.querySelectorAll("img"));
    const pind = document.getElementById("pind");
    const rp = document.getElementById("rp");
    const rtop = document.getElementById("rtop");
    const rbot = document.getElementById("rbot");
    let barsManual = false;
    let barsVisible = true;

    /* restore last position for this chapter, else start at the top
       (same-document hash nav keeps the old scroll offset — always reset) */
    const saved = chEntry(sid, ch);
    requestAnimationFrame(() => {
      if (saved && saved.f && saved.p > 1) {
        const img = imgs[Math.min(saved.p, imgs.length) - 1];
        if (img) {
          window.scrollTo(0, Math.max(0, img.offsetTop + (img.offsetHeight || 0) * saved.f - 4));
          return;
        }
      }
      window.scrollTo(0, 0);
    });

    const backTo = () => go(`#/series/${sid}`);
    document.getElementById("rback").addEventListener("click", backTo);
    document.getElementById("chlist").addEventListener("click", backTo);
    document.getElementById("toseries").addEventListener("click", backTo);
    const nb = document.getElementById("next");
    if (nb) nb.addEventListener("click", () => go(`#/read/${sid}/${nextCh}`));
    const pb = document.getElementById("prev");
    if (pb) pb.addEventListener("click", () => go(`#/read/${sid}/${prevCh}`));
    const nb2 = document.getElementById("nextb");
    if (nb2 && nextCh) nb2.addEventListener("click", () => go(`#/read/${sid}/${nextCh}`));

    /* tap toggles bars */
    strip.addEventListener("click", ev => {
      if (ev.target.closest("button")) return;
      barsManual = true;
      setBars(!barsVisible);
    });

    function setBars(show) {
      barsVisible = show;
      rtop.classList.toggle("hide", !show);
      rbot.classList.toggle("hide", !show);
      pind.classList.toggle("hide", !show);
    }

    function onPageState(p, frac) {
      pind.textContent = `${p} / ${c.pages.length}`;
      rp.style.width = `${Math.round(((p - 1 + frac) / c.pages.length) * 100)}%`;
      store.setEntry(sid, ch, { p, f: Math.round(frac * 1000) / 1000, ts: Date.now() });
    }

    let lastY = window.scrollY;
    function onScroll() {
      const y = window.scrollY;
      setBars(barsManual ? barsVisible : (y <= lastY || y < 80));
      barsManual = false;
      lastY = y;

      /* current page = one containing the viewport midpoint */
      const mid = y + window.innerHeight * 0.5;
      let cur = 1, frac = 0;
      for (let i = 0; i < imgs.length; i++) {
        const top = imgs[i].offsetTop, h = imgs[i].offsetHeight || 1;
        if (mid >= top + h) { cur = i + 1; frac = 1; }
        else if (mid >= top) { cur = i + 1; frac = (mid - top) / h; break; }
        else { cur = Math.max(1, i); frac = 0; break; }
      }
      onPageState(cur, frac);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    readerCleanup = () => window.removeEventListener("scroll", onScroll);
  }

  /* first paint */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
