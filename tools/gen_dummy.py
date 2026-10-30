#!/usr/bin/env python
"""Generate the dummy manga content: per-page SVG placeholder art + data.js manifest.

Run from the app root:  python tools/gen_dummy.py
Outputs:
  assets/manga/<series_id>/cover.svg
  assets/manga/<series_id>/c<N>/p<NNN>.svg
  assets/manga/data.js   (window.MANGA_DATA)
"""
import os
import random
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manga")

PAGE_W = 800

SERIES = [
    dict(
        id="moon-blade", title="Moon Blade Chronicles", author="K. Arisaka",
        tags=["Action", "Fantasy"],
        bg="#12172b", ink="#e8ecff", accent="#7c8cff", accent2="#b8a1ff",
        synopsis=("Every full moon, the blade on Rin's back hums a name. "
                  "Tonight it hummed hers."),
        chapters=[
            ("The Humming Blade", 11),
            ("Wolves of the Third Ward", 10),
            ("Moonrise Duel", 12),
            ("What the Blade Remembers", 10),
        ],
    ),
    dict(
        id="cafe-magica", title="Café Magica", author="Mika Todoroki",
        tags=["Slice of Life", "Fantasy"],
        bg="#2a1b2d", ink="#ffeef6", accent="#ff8fb8", accent2="#ffd36e",
        synopsis=("A tiny café at the end of the shopping street serves tea to witches, "
                  "spirits and one very tired salaryman."),
        chapters=[
            ("Tuesday Regulars", 9),
            ("The Sugar Witch", 10),
            ("Closing Time Spell", 8),
        ],
    ),
    dict(
        id="neon-ronin", title="Neon Ronin", author="J. Watanabe",
        tags=["Sci-Fi", "Action"],
        bg="#101820", ink="#d9fbff", accent="#31e0d0", accent2="#ffe14d",
        synopsis=("In Neo-Kanda, a masterless cyborg sells his sword to the highest bidder. "
                  "His newest job: protect a courier who carries a memory worth killing for."),
        chapters=[
            ("Rain Circuit", 10),
            ("The Memory Courier", 11),
            ("Dead Sector", 10),
        ],
    ),
    dict(
        id="garden-keeper", title="The Garden Keeper", author="Hana Mori",
        tags=["Healing", "Drama"],
        bg="#1b2418", ink="#eefbe6", accent="#7fd069", accent2="#ffe08a",
        synopsis=("Grandpa left Sora one thing: an overgrown garden and a notebook of seeds "
                  "that should not exist."),
        chapters=[
            ("The Overgrown Gate", 9),
            ("Seeds From Nowhere", 9),
        ],
    ),
    dict(
        id="star-diner", title="Star Diner Days", author="Rio Sakamoto",
        tags=["Comedy", "Slice of Life"],
        bg="#2b1c10", ink="#fff3e0", accent="#ffa64d", accent2="#ff6f61",
        synopsis=("The graveyard shift at Star Diner: one burnt coffee away from a new legend."),
        chapters=[
            ("The Burnt Coffee Incident", 8),
            ("Pancake Wars", 8),
        ],
    ),
    dict(
        id="silent-peak", title="Silent Peak", author="A. Kurogane",
        tags=["Mystery", "Thriller"],
        bg="#191423", ink="#ece7ff", accent="#9a7bff", accent2="#5ad1ff",
        synopsis=("The cable car to Silent Peak stopped running years ago. "
                  "So why is the station light on?"),
        chapters=[
            ("Station Light", 11),
            ("Snowfall Records", 10),
            ("The 3 A.M. Car", 11),
        ],
    ),
]


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def panel_art(rng, x, y, w, h, s):
    """Simple decorative contents for one panel."""
    kind = rng.choice(["figures", "skyline", "speed", "bubble", "landscape"])
    parts = []
    cx, cy = x + w / 2, y + h / 2
    if kind == "figures":
        for i in range(rng.randint(2, 3)):
            fx = x + w * (0.25 + 0.25 * i) + rng.randint(-15, 15)
            fy = y + h * rng.uniform(0.55, 0.8)
            r = min(w, h) * rng.uniform(0.10, 0.16)
            parts.append(f'<circle cx="{fx:.0f}" cy="{fy - r * 1.6:.0f}" r="{r:.0f}" fill="{s["accent2"]}" opacity="0.85"/>')
            parts.append(f'<path d="M {fx - r * 1.3:.0f} {y + h - 8:.0f} Q {fx:.0f} {fy - r:.0f} {fx + r * 1.3:.0f} {y + h - 8:.0f} Z" fill="{s["accent"]}" opacity="0.85"/>')
    elif kind == "skyline":
        n = max(3, int(w / 70))
        bw = w / n
        for i in range(n):
            bh = h * rng.uniform(0.25, 0.62)
            parts.append(f'<rect x="{x + i * bw + 2:.0f}" y="{y + h - bh:.0f}" width="{bw - 4:.0f}" height="{bh:.0f}" fill="{s["accent2"]}" opacity="0.55"/>')
            parts.append(f'<rect x="{x + i * bw + bw * 0.3:.0f}" y="{y + h - bh * 0.8:.0f}" width="{bw * 0.14:.0f}" height="{bh * 0.1:.0f}" fill="{s["ink"]}" opacity="0.7"/>')
    elif kind == "speed":
        for i in range(rng.randint(6, 10)):
            ly = y + h * rng.random()
            parts.append(f'<line x1="{x + 6}" y1="{ly:.0f}" x2="{x + w - 6}" y2="{ly + rng.uniform(-8, 8):.0f}" stroke="{s["accent"]}" stroke-width="{rng.randint(2, 5)}" opacity="0.5"/>')
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{min(w, h) * 0.22:.0f}" fill="none" stroke="{s["accent2"]}" stroke-width="6"/>')
    elif kind == "bubble":
        r = min(w, h) * 0.28
        parts.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{r * 1.35:.0f}" ry="{r:.0f}" fill="none" stroke="{s["ink"]}" stroke-width="4"/>')
        words = ["DUMMY", "TALK", "HEY!", "Zzz", "WOW", "SFX", "OK."]
        parts.append(f'<text x="{cx:.0f}" y="{cy + 8:.0f}" font-family="Verdana,sans-serif" font-size="{r * 0.5:.0f}" font-weight="bold" text-anchor="middle" fill="{s["ink"]}">{words[rng.randrange(len(words))]}</text>')
        for i in range(3):
            parts.append(f'<circle cx="{cx + r * 1.5 + i * 14:.0f}" cy="{cy + r * 0.9 + i * 12:.0f}" r="{5 + i * 3}" fill="{s["ink"]}" opacity="0.8"/>')
    else:  # landscape
        parts.append(f'<circle cx="{x + w * 0.75:.0f}" cy="{y + h * 0.28:.0f}" r="{min(w, h) * 0.12:.0f}" fill="{s["accent2"]}"/>')
        parts.append(f'<path d="M {x} {y + h:.0f} L {x + w * 0.3:.0f} {y + h * 0.42:.0f} L {x + w * 0.52:.0f} {y + h * 0.75:.0f} L {x + w * 0.72:.0f} {y + h * 0.36:.0f} L {x + w} {y + h:.0f} Z" fill="{s["accent"]}" opacity="0.8"/>')
    return "".join(parts)


def page_svg(s, rng, n, total):
    h = rng.randint(1150, 1750)
    pad = 36
    gut = 18
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{h}" viewBox="0 0 {PAGE_W} {h}">')
    p.append(f'<rect width="{PAGE_W}" height="{h}" fill="{s["bg"]}"/>')
    # 2-4 stacked panels with side-gutter variation
    rows = rng.choice([2, 3, 3, 4])
    avail = h - pad * 2 - gut * (rows - 1)
    weights = [rng.uniform(0.7, 1.5) for _ in range(rows)]
    y = pad
    for i in range(rows):
        ph = avail * weights[i] / sum(weights)
        px = pad + rng.choice([0, 0, 26])
        pw = PAGE_W - 2 * pad - (26 if px != pad else 0)
        p.append(f'<rect x="{px}" y="{y:.0f}" width="{pw}" height="{ph:.0f}" rx="6" fill="{s["bg"]}" stroke="{s["accent"]}" stroke-width="3"/>')
        # clip art to panel
        p.append(f'<g clip-path="url(#clip{n}_{i})">')
        p.append(f'<clipPath id="clip{n}_{i}"><rect x="{px}" y="{y:.0f}" width="{pw}" height="{ph:.0f}" rx="6"/></clipPath>')
        p.append(panel_art(rng, px, y, pw, ph, s))
        p.append('</g>')
        y += ph + gut
    p.append(f'<text x="{PAGE_W / 2}" y="{h - 14}" font-family="Verdana,sans-serif" font-size="20" text-anchor="middle" fill="{s["ink"]}" opacity="0.75">{n} / {total} — dummy page, replace with real art</text>')
    p.append('</svg>')
    return "\n".join(p), h


def cover_svg(s, title, author, chapters):
    w, h = 800, 1200
    rng = random.Random(s["id"] + "cover")
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    p.append(f'<defs><linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{s["bg"]}"/><stop offset="1" stop-color="{s["accent"]}" stop-opacity="0.55"/>'
             f'</linearGradient></defs>')
    p.append(f'<rect width="{w}" height="{h}" fill="url(#cg)"/>')
    # decorative burst lines
    for _ in range(26):
        a = rng.uniform(0, 6.283)
        r1 = 180 + rng.uniform(0, 90)
        r2 = r1 + rng.uniform(120, 420)
        cx, cy = w * 0.5, h * 0.44
        p.append(f'<line x1="{cx + r1 * __import__("math").cos(a):.0f}" y1="{cy + r1 * __import__("math").sin(a):.0f}" '
                 f'x2="{cx + r2 * __import__("math").cos(a):.0f}" y2="{cy + r2 * __import__("math").sin(a):.0f}" '
                 f'stroke="{s["accent2"]}" stroke-width="{rng.randint(3, 9)}" opacity="{rng.uniform(0.15, 0.4):.2f}"/>')
    p.append(f'<circle cx="{w * 0.5}" cy="{h * 0.44}" r="150" fill="{s["accent2"]}" opacity="0.9"/>')
    p.append(f'<circle cx="{w * 0.5}" cy="{h * 0.44}" r="150" fill="none" stroke="{s["bg"]}" stroke-width="10"/>')
    p.append(f'<text x="{w / 2}" y="{h * 0.47}" font-family="Georgia,serif" font-size="64" font-weight="bold" text-anchor="middle" fill="{s["bg"]}">DUMMY</text>')
    # title block
    p.append(f'<rect x="40" y="{h - 260}" width="{w - 80}" height="200" rx="14" fill="{s["bg"]}" opacity="0.88"/>')
    words = title.split()
    mid = (len(words) + 1) // 2
    lines = [" ".join(words[:mid]), " ".join(words[mid:])] if len(words) > 1 else words
    ty = h - 260 + (70 if len(lines) > 1 else 40)
    for ln in lines:
        if ln:
            p.append(f'<text x="{w / 2}" y="{ty}" font-family="Georgia,serif" font-size="46" font-weight="bold" text-anchor="middle" fill="{s["ink"]}">{esc(ln)}</text>')
        ty += 56
    p.append(f'<text x="{w / 2}" y="{h - 92}" font-family="Verdana,sans-serif" font-size="26" text-anchor="middle" fill="{s["accent2"]}">story &amp; art — {esc(author)}</text>')
    p.append(f'<text x="{w / 2}" y="{h - 52}" font-family="Verdana,sans-serif" font-size="20" text-anchor="middle" fill="{s["ink"]}" opacity="0.7">{len(chapters)} chapters · dummy cover</text>')
    p.append('</svg>')
    return "\n".join(p)


def main():
    rng_master = random.Random("manga-shelf-dummy")
    t0 = time.time()
    n_files = 0
    data = {"updatedAt": time.strftime("%Y-%m-%d"), "series": []}
    for s in SERIES:
        rng = random.Random(s["id"])
        sdir = os.path.join(ASSETS, s["id"])
        chapters = []
        for ci, (ctitle, npages) in enumerate(s["chapters"], start=1):
            cdir = os.path.join(sdir, f"c{ci}")
            os.makedirs(cdir, exist_ok=True)
            pages = []
            for pi in range(1, npages + 1):
                svg, ph = page_svg(s, rng, pi, npages)
                fn = f"p{pi:03d}.svg"
                with open(os.path.join(cdir, fn), "w", encoding="utf-8") as f:
                    f.write(svg)
                pages.append({"src": f"assets/manga/{s['id']}/c{ci}/{fn}", "w": PAGE_W, "h": ph})
                n_files += 1
            chapters.append({"n": ci, "title": ctitle, "pages": pages})
        with open(os.path.join(sdir, "cover.svg"), "w", encoding="utf-8") as f:
            f.write(cover_svg(s, s["title"], s["author"], s["chapters"]))
        n_files += 1
        data["series"].append({
            "id": s["id"], "title": s["title"], "author": s["author"],
            "tags": s["tags"], "synopsis": s["synopsis"],
            "colors": {"bg": s["bg"], "ink": s["ink"], "accent": s["accent"], "accent2": s["accent2"]},
            "cover": f"assets/manga/{s['id']}/cover.svg",
            "chapters": chapters,
        })
    js = "// GENERATED by tools/gen_dummy.py — do not hand-edit.\n" \
         "window.MANGA_DATA = " + _dumps(data) + ";\n"
    with open(os.path.join(ASSETS, "data.js"), "w", encoding="utf-8") as f:
        f.write(js)
    print(f"wrote {n_files} files + data.js in {time.time() - t0:.1f}s")


def _dumps(o, ind=0):
    """Compact-but-readable JSON dump (keep page entries one-per-line)."""
    sp = "  " * ind
    sp2 = "  " * (ind + 1)
    if isinstance(o, dict):
        items = list(o.items())
        if "src" in o:  # page entry: single line
            return "{" + ", ".join(f'"{k}": {_dumps(v)}' for k, v in items) + "}"
        if not items:
            return "{}"
        parts = [f'{sp2}"{k}": {_dumps(v, ind + 1)}' for k, v in items]
        return "{\n" + ",\n".join(parts) + "\n" + sp + "}"
    if isinstance(o, list):
        if not o:
            return "[]"
        one_line = all(isinstance(x, (str, int, float)) for x in o)
        if one_line:
            return "[" + ", ".join(_dumps(x) for x in o) + "]"
        if o and isinstance(o[0], dict) and "src" in o[0]:
            return "[\n" + ",\n".join(sp2 + _dumps(x, ind + 1) for x in o) + "\n" + sp + "]"
        return "[\n" + ",\n".join(sp2 + _dumps(x, ind + 1) for x in o) + "\n" + sp + "]"
    import json as _j
    return _j.dumps(o, ensure_ascii=False)


if __name__ == "__main__":
    main()
