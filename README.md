# stashbase-cs183b

A ready-to-clone [StashBase](https://github.com/liliu-z/stashbase) starter
space. Drop it into StashBase and you've got an indexed knowledge base to
poke at without having to seed your own notes first.

## What's in here

`transcripts/` — full transcripts of all 20 lectures from Stanford **CS183B:
How to Start a Startup**, the Y Combinator / Sam Altman course (Airbnb,
Stripe, Facebook, a16z, Peter Thiel, etc. as guest speakers). One Markdown
file per lecture, ~150 KB of text total.

`.stashbase/` — pre-built embedding + index sidecar. Ships in the repo,
so retrieval works immediately, no first-pass indexing wait.

Topics range from product, growth, hiring, fundraising, sales, enterprise,
and culture — i.e. enough overlap between files that semantic search
actually has to disambiguate, which is the whole point of bringing this in
as a demo corpus.

## Using it

1. In StashBase, open a workspace from this folder (or use **Clone repo as
   space** with `https://github.com/0-bingwu-0/stashbase-cs183b`). The
   index is already built — skip straight to querying.
2. Open Claude (Desktop / Code), Codex, or any MCP-compatible client and
   ask `@stashbase <question>` to retrieve across lectures. The in-app
   terminal has `@stashbase` pre-wired; for external clients, configure
   the MCP server per the [main README](https://github.com/liliu-z/stashbase#mcp-integration).

Some queries that exercise different parts of the index:

- *"How does Sam Altman think about pivots?"* — touches L1, L4, L20.
- *"Founder relationships and co-founder breakups"* — L2, L10, L13.
- *"When should I hire a VP of sales?"* — L12, L19.

## Source

Transcripts are the publicly available course materials from Stanford
CS183B (Fall 2014). Original course site: <https://startupclass.samaltman.com/>.
No edits beyond light formatting for Markdown.
