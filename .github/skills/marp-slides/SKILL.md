---
description: Generate a Marp slide deck in the project's standard style
argument-hint: <topic or wiki page to turn into slides>
allowed-tools: [Read, Write, Glob, Grep]
---

# Generate Marp Slides

The user wants a Marp slide deck about: $ARGUMENTS

## Instructions

1. **Research**: Read relevant wiki pages and/or raw sources to gather content for the slides.
2. **Generate**: Create a `.md` file in `wiki/slides/` using the exact template and style below.
3. **Structure**: Keep slides high-level and visual. Use `<div class="box">` and `<div class="row">` for layout. Use mermaid code blocks for diagrams where they add clarity. Use ionicons SVGs for visual accents.
4. **Length**: Aim for 5–10 slides. One idea per slide. Prefer tables and bullet points over dense paragraphs.

## Required Marp template

Every slide deck MUST use this exact frontmatter and style block:

```markdown
---
marp: true
theme: default
paginate: true
style: |
  section {
    background: #fff;
    color: #1a1a1a;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  }
  h1 {
    color: #e30613;
    font-size: 2em;
  }
  h2 {
    color: #e30613;
    border-bottom: 2px solid #e30613;
    padding-bottom: 0.2em;
  }
  .muted {
    color: #888;
    font-size: 0.9em;
  }
  .box {
    border: 2px solid #e30613;
    border-radius: 16px;
    padding: 16px;
    background: #fff5f5;
    margin: 8px 0;
  }
  .row {
    display: flex;
    gap: 16px;
  }
  .row .box {
    flex: 1;
  }
  table {
    width: 100%;
    font-size: 0.85em;
  }
  th {
    background: #e30613;
    color: #fff;
  }
  td, th {
    padding: 8px 12px;
  }
  code {
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 4px;
  }
  img[src*="ionicons"] {
    vertical-align: middle;
  }
---
```

## Slide structure conventions

### Title slide (always first)

```markdown
# **Topic Title**

<span class="muted">Subtitle or one-line intro</span>
```

### Agenda slide (second slide for decks with 6+ slides)

```markdown
## Agenda

<div class="row">
  <div class="box">
    <img src="https://unpkg.com/ionicons/dist/svg/compass-outline.svg" width="24">
    <strong> Context</strong>
  </div>
  <div class="box">
    <img src="https://unpkg.com/ionicons/dist/svg/bulb-outline.svg" width="24">
    <strong> Core Concepts</strong>
  </div>
  <div class="box">
    <img src="https://unpkg.com/ionicons/dist/svg/flag-outline.svg" width="24">
    <strong> Takeaways</strong>
  </div>
</div>
```

### Content slides — use these patterns as appropriate

**Single key insight:**
```markdown
## Slide Title

<div class="box">
  <strong>Key insight</strong><br>
  Short explanation in one or two lines.
</div>
```

**Process / comparison (row of boxes):**
```markdown
## How It Works

<div class="row">
  <div class="box">
    <strong>Input</strong><br>
    What goes in.
  </div>
  <div class="box">
    <strong>Process</strong><br>
    What happens.
  </div>
  <div class="box">
    <strong>Output</strong><br>
    What comes out.
  </div>
</div>
```

**Bullet points:**
```markdown
## Key Takeaways

- First takeaway with **bolded** key term
- Second takeaway
- Third takeaway
```

**Mermaid diagrams** — use when showing flows, hierarchies, or pipelines. Always use **rounded node shapes** (`(text)` instead of `[text]`) and smooth (**basis**) edge curves via an init directive:
```markdown
## Architecture

` ` `mermaid
%%{init: {'flowchart': {'curve': 'basis'}, 'themeVariables': {'primaryColor': '#fff5f5', 'primaryBorderColor': '#e30613', 'lineColor': '#e30613'}}}%%
flowchart LR
    A("Step 1") --> B("Step 2") --> C("Step 3")
` ` `
```

- Prefer `(rounded rectangle)` over `[square]`; use `([stadium])` for start/end nodes.
- The `themeVariables` block keeps diagrams visually consistent with the red-accent slide theme.

**Tables** — use for comparisons or structured data.

### Ionicons reference

Use SVGs from `https://unpkg.com/ionicons/dist/svg/` for visual accents. Common useful icons:
- `rocket-outline.svg` — launch, overview
- `compass-outline.svg` — context, navigation
- `bulb-outline.svg` — ideas, concepts
- `flag-outline.svg` — takeaways, goals
- `warning-outline.svg` — caveats, limitations
- `checkmark-circle-outline.svg` — conclusions, pros
- `close-circle-outline.svg` — cons, don'ts
- `git-branch-outline.svg` — branching, alternatives
- `analytics-outline.svg` — data, metrics
- `code-slash-outline.svg` — implementation

## Output location

Always save the final slide deck to `wiki/slides/` inside the wiki directory. Use kebab-case for the filename: `wiki/slides/<topic-in-kebab-case>.md`. Create the `wiki/slides/` directory if it does not exist.
