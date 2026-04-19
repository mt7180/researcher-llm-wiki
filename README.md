# researcher-llm-wiki

An LLM-maintained research wiki, compiled based on Karpathys [Idea File](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and adapted for deep research workflows.

## The idea
The human curates sources, *asks good questions*, and steers the direction of inquiry. The LLM does the rest: it *incrementally builds a persistent wiki*, reading each source in depth, integrating findings, adding cross-references, flagging contradictions, and preserving formal definitions, theorems, and algorithms. Every discussion ends with new insights folded back into the wiki — so exploration compounds into lasting knowledge.

## Architecture

```
researcher-llm-wiki/
├── raw/                      # Immutable source documents (PDFs, papers, notes)
├── wiki/                     # LLM-generated markdown pages with Obsidian [[wikilinks]]
│   ├── index.md              # Content catalog
│   ├── log.md                # Chronological activity log
│   ├── sources/              # Source summary pages
│   ├── concepts/             # Concept / method pages
│   ├── entities/             # People, organisations, tools
│   └── analyses/             # Synthesis, comparisons, query results
├── tools/
│   └── wiki-health.py        # Mechanical health checks (uv inline deps)
├── .claude/
│   └── agents/
│       ├── wiki-ingest.md    # Custom agent for ingesting new sources
│       └── wiki-health.md    # Custom agent for health checks
└── CLAUDE.md                 # The schema — conventions, workflows, page types
```

Open the repo in your editor + Obsidian side-by-side. The LLM writes, Obsidian renders the graph.

## Custom agents

Two specialised agents handle the core workflows. They are **auto-triggered** by the main Claude Code agent based on their **description**.

### `wiki-ingest`
Processes new sources added to `raw/` with a researcher mindset:
- **Depth over brevity** — captures formulas, algorithms, theorems, proofs in full
- **Surgical edits** — uses the Edit tool to add new information without rewriting existing content
- **Contradiction resolution** — flags conflicts to the user, uses web search to clarify, never silently overwrites
- Creates source summary, updates concept/entity pages, adds cross-links, updates index and log

### `wiki-health`
Verifies structural and semantic integrity after every ingest or update:
- Runs `tools/wiki-health.py` for mechanical checks: broken links, orphan pages, frontmatter validation, index coverage, tag singletons, missing concept candidates
- Adds LLM semantic analysis: contradictions between pages, cross-reference gaps, content gaps, missing concepts
- Read-only — only reports, never edits

After any ingest, the main agent delegates to `wiki-health` for verification.

## The Python health check tool

`tools/wiki-health.py` runs all deterministic checks in milliseconds using `uv` for dependency management (PEP 723 inline dependencies). Run standalone:

```bash
uv run tools/wiki-health.py
```

Outputs JSON with issues, stats, and candidates for LLM review (content & cross reference gaps, contradictions, missing concept pages).

## Conventions

- **Links**: Obsidian-style `[[wikilinks]]`
- **Frontmatter**: every page has YAML with `title`, `type`, `created`, `updated`, `tags`, `sources`
- **Page types**: `source`, `concept`, `entity`, `analysis`
- **File naming**: lowercase with hyphens
- **Citations**: inline as `(Source: [[source-page]])`

See [CLAUDE.md](CLAUDE.md) for the full schema.

## Why this works

The tedious part of a knowledge base isn't the reading — it's the bookkeeping. Cross-references, consistency, summary updates, contradiction tracking. Humans abandon wikis because maintenance grows faster than value. LLMs don't get bored, don't forget to update a backlink, and can touch 15 files in one pass. The wiki stays maintained because maintenance is near-zero cost.

## Status

Personal research project — the actual wiki content lives locally.