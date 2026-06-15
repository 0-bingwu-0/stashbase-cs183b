# Space rules — CS183B founder knowledge base

## What this space is

A demo knowledge base built from Stanford **CS183B: How to Start a Startup**.

- `transcripts/` — the **source**: full transcripts of all 20 lectures, one
  Markdown file per lecture. Treat these as read-only ground truth.
- `founder_playbook.html` — a **derived** notebook distilled from those 20
  transcripts: ~60 founder questions, each answered as
  Principles → Decision Framework → Field Checklist → Traps to Avoid →
  Drawn From. It is the curated layer on top of the source, not a separate
  source.

## Adding or changing content

1. **New source material** (a lecture, an interview, an essay) goes into
   `transcripts/` as its own Markdown file. Don't paste it into the playbook.
2. **After adding a source, reconcile the playbook.** If the new material
   changes or extends an answer, update `founder_playbook.html` to match —
   keep every question's five-block structure (Principles, Decision
   Framework, Field Checklist, Traps to Avoid, Drawn From), and cite the
   lecture under **Drawn From**. If it raises a genuinely new question, add a
   new `q-title` block in the right chapter rather than overloading an
   existing one.
3. **Keep the two layers consistent.** The playbook must never assert
   something the transcripts don't support — source wins.
4. **Reindex after any write.** There is no file watcher; a change isn't
   searchable until the index is rebuilt.

## Conventions

- When an agent regenerates `founder_playbook.html`, add
  `<meta name="generated_by" content="stashbase-agent">` to its `<head>` so
  generated output stays identifiable.
- This is a public starter space — keep edits self-contained and free of
  anything you wouldn't ship in a demo repo.
