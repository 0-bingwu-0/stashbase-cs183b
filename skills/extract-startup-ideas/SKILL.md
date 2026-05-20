---
name: extract-startup-ideas
description: Read the CS183B lecture transcripts in transcripts/ and extract the startup ideas / company case studies discussed, rendered into notes/ using the template at template/index.html.
---

You read the CS183B "How to Start a Startup" lecture transcripts and extract the startup ideas / company case studies that the speakers (Sam Altman, YC partners, founders of Airbnb, Stripe, Facebook, a16z, Peter Thiel, etc.) use as teaching examples.

## Goal

Turn the 20 lectures into a clean, browsable atlas of startup case studies. Each card is one company, with five fixed fields, rendered into a polished HTML page using the shared template.

Use the HTML template in:

template/index.html

Do not invent a new layout. Only replace the top-level placeholders and repeat the case card block.

---

## INPUT

Source transcripts:

transcripts/Lecture01-*.md … transcripts/Lecture20-*.md

Twenty files, ~150 KB total. Plain Markdown, one lecture per file.

If the user passes a scope argument when invoking the skill (e.g. "Airbnb only", "Lecture 4 only", "just the manual-work pattern"), treat it as a filter on which companies to extract. With no scope, extract every company that gets a real narrative (not just a name-drop).

---

## OUTPUT FILE

Write the rendered HTML to:

notes/startup-ideas-{scope_slug}.html

Rules:
- `scope_slug`: short lowercased slug describing the scope. For the default "all companies, all lectures" output, use `cs183b-all`. For a filter, derive a short kebab-case slug (e.g. "Airbnb only" → `airbnb`, "Lecture 4" → `lecture-04`, "manual work pattern" → `manual-work`).
- Create the `notes/` directory if it doesn't exist.

Example: `notes/startup-ideas-cs183b-all.html`

Do NOT paste HTML into chat. The chat response should only say:

Created notes/{filename} — {N} companies across {L} lectures.

---

## CARD SELECTION

A company qualifies as a card when the speaker uses it as a **story** — describing what the company did early, why it worked, or what lesson it teaches.

Include:
- Companies whose founding story, early scrappiness, or specific tactic is described
- Companies used to illustrate a named principle (e.g. "do things that don't scale")
- Companies whose later outcome the speaker explicitly references

Skip:
- Generic name-drops ("...like Google") with no narrative behind them
- Companies mentioned only in passing as competitors or examples of a category
- Companies that are only mentioned as part of a list

Merge across lectures: if Airbnb is discussed in Lecture 4 and Lecture 8, produce **one** card and list both lectures.

---

## CARD FIELD RULES

Every card has exactly these five fields, in this order:

**Company Name**
The company name, no qualifiers ("Inc.", "the company", etc.). Use the canonical capitalization (Airbnb, not airbnb; Y Combinator, not YC, unless that's the speaker's actual usage).

**Mentioned in**
Comma-separated list of lecture numbers, e.g. `Lecture 4, Lecture 8`. Use lecture numbers, not file names. Order them ascending.

**Context at the time**
2–4 sentences. What the company looked like **when the speaker is describing them** — usually early, scrappy, pre-traction. Capture the specific weird / manual / unscalable thing they were doing or the skepticism they faced. Do NOT describe the present-day company here. Stay faithful to the transcript — don't fabricate metrics or quotes.

**What happened later**
1–2 sentences. The outcome the speaker references — IPO, acquisition, scale, current valuation, "still operating at scale", etc. CS183B was filmed Fall 2014, so if the lecture predates a major outcome and you have widely-known public knowledge to fill it in (Airbnb's IPO, WhatsApp acquisition, etc.), state what happened after. If neither the transcript nor widely-known public knowledge supports a claim, write `Outcome not stated in lectures.`

**Pattern**
One sentence. The generalizable startup lesson the speaker is using this company to illustrate. Should read like a quotable principle, e.g. "Great startup ideas often begin as narrow, weird, manual workflows." If the same company illustrates different lessons in different lectures, pick the dominant one.

---

## EXTRACTION STRATEGY

Don't read all 20 transcripts cover-to-cover. Work in passes:

1. **Sweep for company names** with `grep`. Seed query:
   ```
   grep -nE "\b(Airbnb|Stripe|Facebook|Google|Twitter|Pinterest|Dropbox|Uber|Reddit|Instagram|WhatsApp|PayPal|LinkedIn|YouTube|Snapchat|Tesla|SpaceX|Palantir|Amazon|Apple|Microsoft|Netflix|Square|Slack|GitHub|Y Combinator|Wufoo|Justin\.tv|Twitch|Homejoy|Heroku|MongoDB|Cloudera|Mixpanel|Optimizely|Box)\b" transcripts/*.md
   ```
   Expand the regex as you spot new companies in passing.

2. **For broad "extract everything" runs,** delegate the inventory to the **Explore** agent: "Scan all 20 transcripts in `transcripts/` and return every company that gets a narrative (not just a name-drop), with the lecture number(s) and a one-line snippet of context." Then read only the cited passages to write the cards.

3. **Read tight passages, not whole files.** Once grep tells you Lecture 4 line 287 mentions Airbnb, read a window around that line — not the whole lecture.

4. **Order cards by first appearance** across the lectures (Lecture 1's stories first), unless the user's scope implies a different order.

---

## HTML RENDERING RULES

Use the template file exactly. Replace these top-level placeholders:

- `{{title}}` — page `<title>` text, e.g. `Startup Ideas from CS183B`
- `{{eyebrow}}` — short label above the heading, e.g. `Knowledge atlas · CS183B`
- `{{heading}}` — h1, e.g. `Startup Ideas from CS183B` (can be the same as title, or a longer phrasing)
- `{{lede}}` — 1–2 sentence subtitle that frames the doc, e.g. `Every startup the lecturers used as a teaching example, with the original context, the outcome, and the pattern they were illustrating.`
- `{{section_title}}` — section label above the list, e.g. `Companies` or `Case studies`
- `{{card_count}}` — integer count of cards, e.g. `27`
- `{{footer}}` — short footer line, e.g. `Compiled from Stanford CS183B (Fall 2014).`
- `{{cards}}` — concatenated card HTML (see below)

For each company, render one card using this **exact** structure:

```html
<li>
  <article class="case">
    <div class="case-header">
      <div class="case-name-row">
        <span class="case-num" aria-hidden="true"></span>
        <h3 class="case-name">{{company_name}}</h3>
      </div>
      <span class="case-meta">{{mentioned_in}}</span>
    </div>
    <div class="case-grid">
      <div class="case-block">
        <div class="label">Context at the time</div>
        <p>{{context_at_the_time}}</p>
      </div>
      <div class="case-block">
        <div class="label">What happened later</div>
        <p>{{what_happened_later}}</p>
      </div>
      <div class="case-block pattern">
        <div class="label">Pattern</div>
        <p>{{pattern}}</p>
      </div>
    </div>
  </article>
</li>
```

Per-card field rules:

- `{{company_name}}`: company name only, no quotes, no prefix
- `{{mentioned_in}}`: e.g. `Lecture 4 · Lecture 8` (use `·` between entries — matches the mono-uppercase meta styling). Just `Lecture 4` if only one.
- `{{context_at_the_time}}`, `{{what_happened_later}}`, `{{pattern}}`: plain prose, no quote marks, no leading label
- The card number (01, 02, …) is generated automatically by CSS — do not write numbers into the HTML.
- Escape HTML-sensitive characters in all rendered text: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`. For apostrophes in names like "Lenny's", use `&rsquo;` for typographic quality.

---

## DON'T

- Don't add new fields to the card beyond the five above.
- Don't group cards by pattern (e.g. don't add intermediate `<section>` headers). The pattern is per-card; the page is a flat list.
- Don't include source quotes or transcript snippets in the rendered HTML — the Pattern field is the takeaway, not the evidence.
- Don't write the HTML to chat. Only write it to the output file.
