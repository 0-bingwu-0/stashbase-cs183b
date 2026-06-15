#!/usr/bin/env python3
# Renders founder_playbook.md into a single self-contained static HTML "console".
# Content is mapped verbatim into presentation components; no text is rewritten.

import re, html, pathlib

SRC = pathlib.Path("/Users/bingwu/Downloads/stashbase-cs183b/notes/founder_playbook.md")
OUT = pathlib.Path("/Users/bingwu/Downloads/stashbase-cs183b/notes/founder_playbook.html")

lines = SRC.read_text(encoding="utf-8").split("\n")

# ---------- inline + helpers ----------
def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

def slug(s):
    s = s.lower().strip().rstrip("?")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def norm(s):
    s = s.lower().strip().rstrip("?")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s

def bullets(lns):
    return [ln.strip()[2:] for ln in lns if ln.strip().startswith("- ")]

def paragraphs(lns):
    out, buf = [], []
    for ln in lns:
        if ln.strip():
            buf.append(ln.strip())
        else:
            if buf: out.append(" ".join(buf)); buf = []
    if buf: out.append(" ".join(buf))
    return out

# ---------- parse ----------
title = lines[0][2:].strip()
i = 1
lead_paras, doctrine, howto = [], [], ""
while i < len(lines) and lines[i].strip() != "## Table of Contents":
    st = lines[i].strip()
    if st and st != "---":
        m = re.match(r"^\d+\.\s+(.*)", st)
        if m:
            doctrine.append(m.group(1))
        elif st.startswith("**How to use this:**"):
            howto = st
        elif st.startswith("**The five things"):
            pass
        else:
            lead_paras.append(st)
    i += 1

i += 1  # skip "## Table of Contents"
toc = {}
while i < len(lines) and not lines[i].startswith("# "):
    m = re.match(r"^- \*\*(.+?)\*\*\s+—\s+(.*)$", lines[i].strip())
    if m:
        toc[m.group(1).strip()] = m.group(2).strip()
    i += 1

chapters, cur_ch, cur_q, cur_sec, colophon = [], None, None, None, ""
while i < len(lines):
    ln = lines[i]; st = ln.strip()
    if ln.startswith("# "):
        name = ln[2:].strip()
        cur_ch = {"name": name, "desc": toc.get(name, ""), "questions": []}
        chapters.append(cur_ch); cur_q = cur_sec = None
    elif ln.startswith("## "):
        qt = ln[3:].strip()
        cur_q = {"title": qt, "slug": slug(qt), "sections": []}
        cur_ch["questions"].append(cur_q); cur_sec = None
    elif ln.startswith("### "):
        cur_sec = {"label": ln[4:].strip(), "lines": []}
        cur_q["sections"].append(cur_sec)
    elif st.startswith("*End of playbook"):
        colophon = st.strip("*").strip()
    elif st == "---":
        pass
    elif cur_sec is not None:
        cur_sec["lines"].append(ln)
    i += 1

# cross-link lookup
qindex = []
for ch in chapters:
    for q in ch["questions"]:
        qindex.append((norm(q["title"]), q["slug"]))
qmap = {n: s for n, s in qindex}

def match_related(text):
    rn = norm(text)
    if rn in qmap:
        return qmap[rn]
    rt = set(rn.split()); best, bs = None, 0.0
    for n, s in qindex:
        nt = set(n.split())
        if not nt: continue
        j = len(rt & nt) / len(rt | nt)
        if j > bs: bs, best = j, s
    return best if bs >= 0.6 else None

# ---------- short labels (for chip-style block headers) ----------
LABELMAP = {
    "Key Principles": "Principles",
    "Framework": "Decision Framework",
    "Checklist": "Field Checklist",
    "Common Mistakes": "Traps to Avoid",
    "Related Questions": "See Also",
    "Sources": "Drawn From",
}
LABELCLS = {
    "Key Principles": "blk-principles",
    "Framework": "blk-framework",
    "Checklist": "blk-checklist",
    "Common Mistakes": "blk-traps",
    "Related Questions": "blk-related",
    "Sources": "blk-sources",
}

def r_short(lns):
    return "".join(f"<p>{inline(p)}</p>" for p in paragraphs(lns))

def r_principles(lns):
    items = "".join(f"<li>{inline(b)}</li>" for b in bullets(lns))
    return f'<ul class="principles">{items}</ul>'

def r_framework(lns):
    para = [ln.strip() for ln in lns if ln.strip() and not ln.strip().startswith("- ")]
    flow = bullets(lns)
    out = ""
    for p in para:
        out += f'<p class="fw-intro">{inline(p)}</p>'
    if flow:
        out += '<div class="framework">'
        for f in flow:
            if "→" in f:
                left, right = f.split("→", 1)
                out += ('<div class="fw-row">'
                        f'<span class="fw-if">{inline(left.strip())}</span>'
                        '<span class="fw-arrow" aria-hidden="true">→</span>'
                        f'<span class="fw-then">{inline(right.strip())}</span></div>')
            else:
                out += f'<div class="fw-row fw-row-plain">{inline(f)}</div>'
        out += '</div>'
    return out

def r_checklist(lns, qslug):
    out = '<ul class="checklist">'
    n = 0
    for ln in lns:
        m = re.match(r"^- \[ \]\s+(.*)$", ln.strip())
        if m:
            out += (f'<li><label><input type="checkbox" data-k="{qslug}-{n}">'
                    f'<span class="cb"></span><span class="ck-text">{inline(m.group(1))}</span></label></li>')
            n += 1
    return out + '</ul>'

def r_traps(lns):
    out = '<div class="traps">'
    for b in bullets(lns):
        m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", b)
        lead = m.group(1) if m else ""
        rest = (m.group(2) if m else b).strip()
        parts = re.split(r"\bBetter:\s*", rest, maxsplit=1)
        why = parts[0].strip()
        better = parts[1].strip() if len(parts) == 2 else ""
        why = re.sub(r"^\s*Why[^:]*:\s*", "", why).strip()
        out += '<div class="trap">'
        out += f'<div class="trap-lead">{inline(lead)}</div>'
        if why:
            out += f'<div class="trap-line"><span class="tk tk-why">Why</span><span>{inline(why)}</span></div>'
        if better:
            out += f'<div class="trap-line"><span class="tk tk-fix">Fix</span><span>{inline(better)}</span></div>'
        if not why and not better:
            out += f'<div class="trap-line"><span>{inline(rest)}</span></div>'
        out += '</div>'
    return out + '</div>'

def r_related(lns):
    out = '<div class="related">'
    for b in bullets(lns):
        href = match_related(b)
        label = inline(b.rstrip("?"))
        if href:
            out += f'<a class="rel-chip" href="#{href}">{label}</a>'
        else:
            out += f'<span class="rel-chip rel-dead">{label}</span>'
    return out + '</div>'

def r_sources(lns):
    out = '<div class="sources">'
    for b in bullets(lns):
        m = re.match(r"Lecture\s+(\d+)\s*[—-]\s*(.*)$", b)
        if m:
            out += (f'<span class="src-pill"><b>L{m.group(1)}</b>'
                    f'<span>{html.escape(m.group(2).strip())}</span></span>')
        else:
            out += f'<span class="src-pill"><span>{inline(b)}</span></span>'
    return out + '</div>'

def render_question(q, idx):
    secs = {s["label"]: s for s in q["sections"]}
    short = r_short(secs["Short Answer"]["lines"]) if "Short Answer" in secs else ""
    inner = ""
    order = [("Key Principles", r_principles), ("Framework", r_framework),
             ("Checklist", None), ("Common Mistakes", r_traps),
             ("Sources", r_sources)]
    for lab, fn in order:
        if lab not in secs:
            continue
        body = secs[lab]["lines"]
        if lab == "Checklist":
            h = r_checklist(body, q["slug"])
        elif lab == "Related Questions":
            h = r_related(body)
        else:
            h = fn(body)
        inner += (f'<section class="blk {LABELCLS[lab]}">'
                  f'<h4 class="blk-h">{LABELMAP[lab]}</h4>{h}</section>')
    return f'''<article class="qcard" id="{q['slug']}">
  <div class="q-head">
    <span class="q-index">{idx}</span>
    <h3 class="q-title">{inline(q['title'])}</h3>
  </div>
  <div class="lede">{short}</div>
  <details class="more">
    <summary aria-label="Expand entry"><span class="q-caret" aria-hidden="true"></span></summary>
    <div class="more-body">{inner}</div>
  </details>
</article>'''

# ---------- assemble ----------
total_entries = sum(len(c["questions"]) for c in chapters)

# top S-metro map: stations on a snaking route with rounded U-turns
PXW, PXH, COLS = 960, 300, 4
n_rows = (len(chapters) + COLS - 1) // COLS
col_w, row_h = PXW / COLS, PXH / n_rows
cx = [(c + 0.5) * col_w for c in range(COLS)]
cy = [(r + 0.5) * row_h for r in range(n_rows)]
xpct = [(c + 0.5) * 100.0 / COLS for c in range(COLS)]
ypct = [(r + 0.5) * 100.0 / n_rows for r in range(n_rows)]
xR, xL, R = PXW - 40, 40, 24
_last = len(chapters) - 1
_lr, _lpos = _last // COLS, _last % COLS
_lcol = _lpos if _lr % 2 == 0 else COLS - 1 - _lpos
end_x = cx[_lcol]
d = [f"M{cx[0]:.1f},{cy[0]:.1f}"]
for r in range(n_rows):
    y = cy[r]
    if r == n_rows - 1:
        d.append(f"L{end_x:.1f},{y:.1f}")
    else:
        ny = cy[r + 1]
        if r % 2 == 0:  # row goes left->right, U-turn on the right
            d += [f"L{xR-R:.1f},{y:.1f}", f"Q{xR:.1f},{y:.1f} {xR:.1f},{y+R:.1f}",
                  f"L{xR:.1f},{ny-R:.1f}", f"Q{xR:.1f},{ny:.1f} {xR-R:.1f},{ny:.1f}"]
        else:           # row goes right->left, U-turn on the left
            d += [f"L{xL+R:.1f},{y:.1f}", f"Q{xL:.1f},{y:.1f} {xL:.1f},{y+R:.1f}",
                  f"L{xL:.1f},{ny-R:.1f}", f"Q{xL:.1f},{ny:.1f} {xL+R:.1f},{ny:.1f}"]
path_d = " ".join(d)
_stations = ""
for i, ch in enumerate(chapters):
    r, pos = i // COLS, i % COLS
    col = pos if r % 2 == 0 else COLS - 1 - pos
    _stations += (f'<a class="mstation" href="#ch-{i+1}" style="left:{cx[col]:.1f}px;top:{cy[r]:.1f}px" '
                  f'title="{html.escape(ch["name"])}">'
                  f'<span class="ms-node">{i+1:02d}</span>'
                  f'<span class="ms-label">{html.escape(ch["name"])}</span></a>')
metro_html = (f'<div class="metro-wrap"><div class="metro">'
              f'<svg class="metro-line" viewBox="0 0 {PXW} {PXH}" preserveAspectRatio="none" aria-hidden="true">'
              f'<defs><linearGradient id="mline" x1="0" y1="0" x2="0" y2="1">'
              f'<stop offset="0" stop-color="#9B2D1F"/><stop offset="1" stop-color="#C2603F"/>'
              f'</linearGradient></defs>'
              f'<path d="{path_d}" fill="none" stroke="url(#mline)" stroke-width="3" '
              f'stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="9 8" '
              f'vector-effect="non-scaling-stroke"/>'
              f'</svg>{_stations}</div></div>')

pipeline_steps = ["20 Lectures", "Distilled", "Structured", "Cross-linked", "Playbook"]
pipeline = ""
for k, step in enumerate(pipeline_steps):
    pipeline += f'<span class="pl-step{" pl-last" if k == len(pipeline_steps)-1 else ""}">{step}</span>'
    if k < len(pipeline_steps) - 1:
        pipeline += '<span class="pl-arrow" aria-hidden="true">→</span>'

doctrine_html = ""
for k, d in enumerate(doctrine, 1):
    _dp = d.split(". ")
    _lead = _dp[0].strip()
    _rest = ". ".join(_dp[1:]).strip()
    if _rest:
        _lead += "."
    _item = f'<strong>{inline(_lead)}</strong>'
    if _rest:
        _item += f' {inline(_rest)}'
    doctrine_html += f'<li><span class="dn">{k}</span><p class="d-text">{_item}</p></li>'

chapters_html = ""
for n, ch in enumerate(chapters, 1):
    cards = ""
    for j, q in enumerate(ch["questions"], 1):
        cards += render_question(q, f"{n}.{j}")
    chapters_html += f'''<section class="chapter" id="ch-{n}" data-ch="{n}">
  <div class="ch-head">
    <span class="ch-num">{n:02d}</span>
    <h2 class="ch-title">{html.escape(ch["name"])}</h2>
    <span class="ch-count">{len(ch["questions"])} entries</span>
    <p class="ch-desc">{html.escape(ch["desc"])}</p>
  </div>
  {cards}
</section>'''

lead_raw = lead_paras[0] if lead_paras else ""
_parts = lead_raw.split(". ")
_first = (_parts[0].strip() + ".") if lead_raw else ""
_course_m = re.search(r"\(\*?(.+?)\*?\)", _first)
course_name_html = html.escape(_course_m.group(1).strip()) if _course_m else "How to Start a Startup"
intro_desc_html = html.escape(_first.split(",")[0].strip()) if _first else ""
cover_sub = inline(". ".join(_parts[1:]).strip()) if len(_parts) > 1 else inline(lead_raw)
howto_html = inline(howto) if howto else ""
colophon_html = inline(colophon) if colophon else ""

CSS = r"""
:root{
  --paper:#F6F3EC; --paper2:#FCFAF4; --panel:#FBF8F1; --rail:#F1ECE1;
  --ink:#1C1B19; --ink-soft:#524E46; --muted:#857E72;
  --accent:#9B2D1F; --accent-2:#7C2417; --accent-tint:#F0E3DD;
  --rule:#DED6C7; --rule-soft:#E8E1D4;
  --warn:#B0341D; --warn-bg:#F4E7E1; --good:#4E6A3E;
  --serif:"Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,Georgia,"Times New Roman",serif;
  --sans:"Helvetica Neue",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  --mono:"SF Mono","JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;
  --bar:54px; --railw:340px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);
  font-size:18px;line-height:1.62;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
::selection{background:var(--accent-tint)}
a{color:var(--accent);text-decoration:none}
[hidden]{display:none!important}
code{font-family:var(--mono);font-size:.85em;background:var(--accent-tint);padding:.05em .35em;border-radius:3px}

/* ===== command bar ===== */
.cmd{position:sticky;top:0;z-index:60;background:rgba(246,243,236,.94);
  backdrop-filter:saturate(150%) blur(8px);border-bottom:1px solid var(--ink)}
.cmd-inner{display:flex;align-items:center;gap:16px;height:var(--bar);max-width:1180px;margin:0 auto;padding:0 40px}
.cmd-brand{display:flex;align-items:baseline;gap:10px;font-family:var(--sans);font-weight:800;
  font-size:13px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink);white-space:nowrap;flex:none}
.cmd-tag{font-weight:600;font-size:9.5px;letter-spacing:.18em;color:#fff;background:var(--accent);
  padding:3px 7px;border-radius:4px}
.cmd-divider{width:1px;height:22px;background:var(--rule);flex:none}
.cmd-meta{flex:1;min-width:0;margin:0;display:flex;align-items:center;gap:9px;white-space:nowrap;overflow:hidden}
.cmd-maplink{flex:none;font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;color:var(--accent);border:1px solid var(--accent);border-radius:6px;
  padding:7px 13px;transition:.15s}
.cmd-maplink:hover{background:var(--accent);color:#fff}
.ci-from{font-family:var(--sans);font-size:9.5px;letter-spacing:.15em;text-transform:uppercase;
  font-weight:700;color:var(--accent);flex:none}
.ci-course{font-family:var(--serif);font-style:italic;font-size:15px;color:var(--ink);font-weight:600;flex:none}
.ci-dot{color:var(--muted);flex:none}
.ci-sub{font-family:var(--sans);font-size:12.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;min-width:0}
.progress{height:2px;background:transparent}
.progress-fill{height:2px;width:0;background:var(--accent);transition:width .08s linear}

/* ===== page ===== */
.page{padding:0 0 60px}

/* ===== decision map (top overview) ===== */
.map{background:var(--paper2);border-bottom:1px solid var(--rule);scroll-margin-top:var(--bar)}
.map-in{max-width:1180px;margin:0 auto;padding:32px 40px 36px}
.metro-wrap{overflow:hidden;display:flex;justify-content:center;margin:6px 0 0}
.metro{position:relative;width:960px;height:336px;flex:none;transform-origin:top center}
.metro-line{position:absolute;top:0;left:0;width:960px;height:300px;overflow:visible}
.mstation{position:absolute;transform:translate(-50%,-50%);width:44px;height:44px;text-decoration:none}
.ms-node{position:relative;z-index:1;width:44px;height:44px;border-radius:50%;
  border:2px solid var(--accent);background:var(--paper2);color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-family:var(--mono);
  font-size:13px;font-weight:700;transition:transform .18s,background .18s,color .18s}
.mstation:hover .ms-node{background:var(--accent);color:#fff;transform:scale(1.12)}
.mstation:first-of-type .ms-node,.mstation:last-of-type .ms-node{background:var(--accent);color:#fff}
.ms-label{position:absolute;top:52px;left:50%;transform:translateX(-50%);width:160px;text-align:center;
  font-family:var(--sans);font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--ink-soft);line-height:1.3;transition:color .12s}
.mstation:hover .ms-label{color:var(--accent)}

/* doctrine (warm editorial band — opens the manual) */
.doctrine{background:var(--paper);border-bottom:1px solid var(--rule);scroll-margin-top:var(--bar)}
.doctrine-in{max-width:880px;margin:0 auto;padding:26px 40px 30px}
.doctrine-head{display:flex;align-items:baseline;gap:14px;margin-bottom:14px;flex-wrap:wrap}
.doctrine-head .k{font-family:var(--sans);text-transform:uppercase;letter-spacing:.2em;font-size:10px;
  font-weight:800;color:var(--accent)}
.doctrine-head .t{font-family:var(--serif);font-size:23px;color:var(--ink);font-weight:700;letter-spacing:-.01em}
.doctrine-list{list-style:none;margin:0;padding:0}
.doctrine-list li{display:grid;grid-template-columns:28px 1fr;gap:0 18px;align-items:center;
  padding:10px 0;border-top:1px solid var(--rule)}
.doctrine-list li:first-child{border-top:0;padding-top:2px}
.dn{color:var(--accent);font-family:var(--serif);font-size:17px;font-weight:700;line-height:1.45}
.d-text{margin:0;font-size:17px;line-height:1.45;color:var(--ink-soft)}
.d-text strong{font-weight:700;color:var(--ink)}
.doctrine-list em{font-style:normal}

/* chapter */
.chapter{scroll-margin-top:var(--bar)}
.ch-head{max-width:880px;margin:0 auto;padding:44px 40px 16px;
  display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:baseline;
  border-bottom:2px solid var(--ink);position:relative}
.ch-num{font-family:var(--mono);font-size:13px;color:var(--accent);font-weight:700;letter-spacing:.1em}
.ch-title{font-size:clamp(26px,4vw,36px);line-height:1;margin:0;letter-spacing:-.02em}
.ch-count{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.04em}
.ch-desc{grid-column:1/-1;font-family:var(--sans);font-size:12.5px;color:var(--muted);margin:6px 0 0;
  text-transform:uppercase;letter-spacing:.05em}

/* question card */
.qcard{position:relative;max-width:880px;margin:0 auto;padding:24px 40px;border-bottom:1px solid var(--rule);
  scroll-margin-top:var(--bar);transition:background .15s}
.qcard:target{background:var(--paper2)}
.q-head{display:flex;align-items:baseline;gap:12px;margin-bottom:12px;padding-right:38px}
.q-index{font-family:var(--mono);font-size:12px;color:var(--accent);font-weight:700;flex:none}
.q-title{font-size:clamp(20px,2.6vw,25px);line-height:1.15;margin:0;letter-spacing:-.01em}
.lede{font-size:16.5px;line-height:1.55;color:var(--ink);border-left:3px solid var(--accent);
  padding:1px 0 1px 18px}
.lede p{margin:0}
.lede strong{font-weight:700}

/* expand control */
.more{margin:0}
.more>summary{list-style:none;cursor:pointer;position:absolute;top:22px;right:40px;
  width:30px;height:30px;display:flex;align-items:center;justify-content:center;
  border:1px solid var(--rule);border-radius:7px;background:var(--paper2);transition:.15s}
.more>summary::-webkit-details-marker{display:none}
.more>summary:hover{border-color:var(--accent);background:var(--accent-tint)}
.q-caret{width:7px;height:7px;border-top:2px solid var(--accent);border-right:2px solid var(--accent);
  transform:rotate(45deg);transition:transform .2s}
.more>summary:hover .q-caret{border-color:var(--accent)}
.more[open]>summary{background:var(--accent);border-color:var(--accent)}
.more[open]>summary .q-caret{transform:rotate(135deg);border-color:#fff}
.more-body{margin-top:22px;display:grid;gap:24px;animation:fade .2s ease}
@keyframes fade{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}

/* blocks */
.blk{margin:0}
.blk-h{font-family:var(--sans);font-size:10px;letter-spacing:.18em;text-transform:uppercase;font-weight:800;
  color:var(--accent);margin:0 0 13px;padding-bottom:7px;border-bottom:1px solid var(--rule-soft);
  display:flex;align-items:center;gap:8px}
.blk-h::after{content:"";flex:1;height:1px;background:var(--rule-soft)}

.principles{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.principles li{position:relative;padding:11px 14px 11px 34px;background:var(--panel);
  border:1px solid var(--rule-soft);border-radius:7px;font-size:15.5px;line-height:1.5}
.principles li::before{content:"◆";position:absolute;left:14px;top:12px;color:var(--accent);font-size:10px}
.principles strong{font-weight:700}

.fw-intro{font-size:15px;color:var(--ink-soft);margin:0 0 12px;font-style:italic}
.framework{border-left:2px solid var(--accent);display:grid;gap:0}
.fw-row{display:grid;grid-template-columns:1fr auto 1.1fr;gap:13px;align-items:center;
  padding:11px 16px;background:var(--panel);border:1px solid var(--rule-soft);border-left:0;
  font-size:14.5px;line-height:1.4}
.fw-row+.fw-row{margin-top:-1px}
.fw-if{color:var(--ink-soft)}
.fw-then{color:var(--ink);font-weight:600}
.fw-arrow{color:var(--accent);font-size:16px;font-weight:700}
.fw-row-plain{display:block}
.fw-row-plain strong{color:var(--accent);font-weight:700}

.checklist{list-style:none;margin:0;padding:0;display:grid;gap:7px}
.checklist label{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:start;cursor:pointer;
  font-size:15px;line-height:1.45}
.checklist input{position:absolute;opacity:0;width:0;height:0}
.cb{width:19px;height:19px;border:1.5px solid var(--muted);border-radius:5px;margin-top:2px;flex:none;
  display:inline-flex;align-items:center;justify-content:center;transition:.15s}
.cb::after{content:"";width:10px;height:5px;border-left:2.5px solid #fff;border-bottom:2.5px solid #fff;
  transform:rotate(-45deg) scale(0);margin-top:-2px;transition:transform .15s}
.checklist input:checked+.cb{background:var(--good);border-color:var(--good)}
.checklist input:checked+.cb::after{transform:rotate(-45deg) scale(1)}
.checklist input:checked~.ck-text{color:var(--muted);text-decoration:line-through;text-decoration-color:var(--rule)}
.checklist input:focus-visible+.cb{outline:2px solid var(--accent);outline-offset:2px}

.traps{display:grid;gap:11px}
.trap{background:var(--warn-bg);border:1px solid #E6CFC5;border-left:3px solid var(--warn);
  border-radius:7px;padding:13px 15px}
.trap-lead{font-weight:700;font-size:15.5px;margin-bottom:7px;color:var(--accent-2)}
.trap-line{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;font-size:14px;
  line-height:1.45;color:var(--ink-soft);margin-top:4px}
.tk{font-family:var(--sans);font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  padding:3px 7px;border-radius:4px;margin-top:2px;white-space:nowrap}
.tk-why{background:#E4D2CA;color:var(--accent-2)}
.tk-fix{background:var(--good);color:#fff}

.related{display:flex;flex-wrap:wrap;gap:8px}
.rel-chip{font-family:var(--sans);font-size:12.5px;line-height:1.3;padding:8px 13px;border:1px solid var(--rule);
  border-radius:999px;color:var(--ink-soft);background:var(--paper2);transition:.15s}
a.rel-chip:hover{border-color:var(--accent);color:var(--accent);background:#fff}
.rel-dead{opacity:.6}

.sources{display:flex;flex-wrap:wrap;gap:8px}
.src-pill{display:inline-flex;align-items:center;gap:8px;font-family:var(--sans);font-size:12px;
  color:var(--ink-soft);background:var(--panel);border:1px solid var(--rule-soft);border-radius:6px;
  padding:5px 10px 5px 5px}
.src-pill b{font-family:var(--mono);font-size:10.5px;font-weight:700;background:var(--ink);color:var(--paper);
  padding:4px 6px;border-radius:4px}

/* colophon */
.colophon{max-width:840px;margin:0 auto;padding:48px 40px 30px;text-align:center}
.colophon-rule{width:44px;height:2px;background:var(--accent);margin:0 auto 18px}
.colophon p{font-family:var(--sans);font-size:13px;line-height:1.6;color:var(--muted);max-width:46ch;margin:0 auto}

@media(max-width:980px){
  .map-in,.doctrine-in,.ch-head,.qcard,.colophon{padding-left:24px;padding-right:24px}
  .cmd-inner{padding-left:22px;padding-right:22px}
  .more>summary{right:24px}
}
@media(max-width:560px){
  body{font-size:17px}
  .fw-row{grid-template-columns:1fr;gap:5px}
  .fw-arrow{display:none}
  .ci-sub,.ci-dot{display:none}
}
"""

JS = r"""
(function(){
  var pf=document.getElementById('pf');
  function prog(){var h=document.documentElement;var m=h.scrollHeight-h.clientHeight;
    pf.style.width=(m>0?(h.scrollTop/m*100):0)+'%';}
  document.addEventListener('scroll',prog,{passive:true});window.addEventListener('resize',prog);prog();

  // checklist persistence
  var KEY='fp-checks',store={};
  try{store=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
  document.querySelectorAll('.checklist input').forEach(function(b){
    var k=b.getAttribute('data-k');if(store[k])b.checked=true;
    b.addEventListener('change',function(){store[k]=b.checked;
      try{localStorage.setItem(KEY,JSON.stringify(store))}catch(e){}});
  });

  // scale the S-metro uniformly to fit width (always centered, never a column)
  var mwrap=document.querySelector('.metro-wrap'),metro=document.querySelector('.metro');
  function scaleMetro(){
    if(!mwrap||!metro)return;
    var s=Math.min(1,mwrap.clientWidth/960);
    metro.style.transform='scale('+s+')';
    mwrap.style.height=(300*s)+'px';
  }
  window.addEventListener('resize',scaleMetro);scaleMetro();
})();
"""

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Founder Playbook — Operating Console</title>
<meta name="description" content="A searchable decision console distilled from Stanford CS183B, How to Start a Startup.">
<style>{CSS}</style>
</head>
<body>
<header class="cmd">
  <div class="cmd-inner">
    <a class="cmd-brand" href="#top"><span>Founder Playbook</span><span class="cmd-tag">CS183B</span></a>
    <span class="cmd-divider" aria-hidden="true"></span>
    <p class="cmd-meta"><span class="ci-from">Distilled from</span><em class="ci-course">{course_name_html}</em><span class="ci-dot" aria-hidden="true">·</span><span class="ci-sub">{intro_desc_html}</span></p>
    <a class="cmd-maplink" href="#map">The Map</a>
  </div>
  <div class="progress"><div class="progress-fill" id="pf"></div></div>
</header>

<main class="page" id="top">
  <section class="map" id="map">
    <div class="map-in">
      {metro_html}
    </div>
  </section>

  <section class="doctrine" id="doctrine">
    <div class="doctrine-in">
      <div class="doctrine-head">
        <span class="k">Operating Doctrine</span>
        <span class="t">If you remember nothing else</span>
      </div>
      <ol class="doctrine-list">{doctrine_html}</ol>
    </div>
  </section>

  {chapters_html}

  <section class="colophon">
    <div class="colophon-rule"></div>
    <p>{colophon_html}</p>
  </section>
</main>
<script>{JS}</script>
</body>
</html>"""

OUT.write_text(page, encoding="utf-8")
print(f"Wrote {OUT}")
print(f"Chapters: {len(chapters)} | Entries: {total_entries} | Bytes: {OUT.stat().st_size}")
