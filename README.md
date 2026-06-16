# stashbase-cs183b

A ready-to-clone [StashBase](https://github.com/liliu-z/stashbase) starter
space. Clone it, import it, and you have a real knowledge base to query in
under a minute — no notes of your own to seed first.

## What's in here

- **`transcripts/`** — full transcripts of all 20 lectures from Stanford
  **CS183B: How to Start a Startup** (the Y Combinator / Sam Altman course;
  Airbnb, Stripe, Facebook, a16z, Peter Thiel, etc. as guest speakers). One
  Markdown file per lecture.
- **`founder_playbook.html`** — a single HTML notebook distilled from those
  20 lectures: ~60 founder questions, each answered with principles, a
  decision framework, a field checklist, and the traps to avoid.

That's the whole corpus — the lecture source plus the playbook built on top
of it.

The repo also ships prebuilt embeddings (under `.stashbase/`), so importing
reuses them instead of re-embedding the whole course. Search and the built-in
agent run on an OpenAI key — add one in Settings if you haven't.

## Get started in 4 steps

1. **Clone** this repo:
   ```
   git clone https://github.com/0-bingwu-0/stashbase-cs183b
   ```
2. **Import** the folder into StashBase as a space — use **Import folder** on
   the Welcome screen and pick the cloned directory.
3. **View** `founder_playbook.html` — open it in StashBase to read the
   playbook rendered inline.
4. **Ask the built-in Claude agent.** Open the agent panel and put a
   question to it — it searches across the playbook and all 20 transcripts
   to answer. Three to start with, straight from the playbook:

   - *"How do I find a startup idea?"*
   - *"How do I know if I have product-market fit?"*
   - *"Should I worry about competitors and being copied?"*

## Source

Transcripts are the publicly available course materials from Stanford
CS183B (Fall 2014). Course materials: <https://genius.com/albums/Sam-altman/How-to-start-a-startup-cs183b>.
No edits beyond light formatting for Markdown.
