# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
 
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

WIKI_DIR = Path("wiki")
RAW_DIR = Path("raw")
REQUIRED_FRONTMATTER = {"title", "type", "created", "updated", "tags", "sources"}
VALID_TYPES = {"source", "concept", "entity", "analysis"}
TYPE_TO_DIR = {"source": "sources", "concept": "concepts", "entity": "entities", "analysis": "analyses"}
EXEMPT_FILES = {"index.md", "log.md"}

# --- Parsing helpers ---

def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_wikilinks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # Match [[target]] or [[target|display]], extract target only
    return [m.split("|")[0] for m in re.findall(r"\[\[([^\]]+)\]\]", text)]


IGNORE_TERMS = {
    "raw-file", "author", "authors", "venue", "arxiv", "source", "summary",
    "key-findings", "methodology", "results", "limitations", "relevance",
    "see-also", "how-it-works", "strengths", "overview", "conclusion",
    "references", "table", "figure", "note", "example", "important",
}


def extract_bold_terms(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # Skip frontmatter
    text = re.sub(r"^---\n.*?\n---", "", text, count=1, flags=re.DOTALL)
    # Extract **bold terms** and `backtick terms`
    bold = re.findall(r"\*\*([A-Z][A-Za-z0-9 \-/()]+)\*\*", text)
    backtick = re.findall(r"`([A-Z][A-Za-z0-9 \-]+)`", text)
    # Filter out common non-concept terms
    return [t for t in bold + backtick if stem(t) not in IGNORE_TERMS]


def stem(name: str) -> str:
    """Normalise a page name for matching: lowercase, hyphens for spaces, strip .md"""
    return name.lower().replace(" ", "-").removesuffix(".md")


# --- Collect all wiki pages ---

def collect_pages(wiki_dir: Path) -> dict[str, Path]:
    """Return {stem_name: path} for all .md files in the wiki."""
    pages = {}
    for p in wiki_dir.rglob("*.md"):
        # Skip obsidian internals
        if ".obsidian" in p.parts:
            continue
        pages[stem(p.stem)] = p
    return pages


# --- Checks ---

def check_broken_links(pages: dict[str, Path]) -> list[dict]:
    issues = []
    for name, path in pages.items():
        for target in extract_wikilinks(path):
            if stem(target) not in pages:
                issues.append({"source": str(path.relative_to(WIKI_DIR)), "target": target})
    return issues


def check_orphan_pages(pages: dict[str, Path]) -> list[str]:
    inbound: dict[str, int] = defaultdict(int)
    for name in pages:
        inbound[name] = 0

    for name, path in pages.items():
        for target in extract_wikilinks(path):
            s = stem(target)
            if s in inbound:
                inbound[s] += 1

    orphans = []
    for name, count in inbound.items():
        rel = str(pages[name].relative_to(WIKI_DIR))
        if count == 0 and pages[name].name not in EXEMPT_FILES:
            orphans.append(rel)
    return orphans


def check_frontmatter(pages: dict[str, Path]) -> list[dict]:
    issues = []
    for name, path in pages.items():
        if path.name in EXEMPT_FILES:
            continue
        fm = parse_frontmatter(path)
        if fm is None:
            issues.append({"page": str(path.relative_to(WIKI_DIR)), "issue": "no frontmatter found"})
            continue
        for field in REQUIRED_FRONTMATTER:
            if field not in fm:
                issues.append({"page": str(path.relative_to(WIKI_DIR)), "issue": f"missing field: {field}"})
        page_type = fm.get("type")
        if page_type and page_type not in VALID_TYPES:
            issues.append({"page": str(path.relative_to(WIKI_DIR)), "issue": f"invalid type: {page_type}"})
        if page_type and page_type in TYPE_TO_DIR:
            expected_dir = TYPE_TO_DIR[page_type]
            if expected_dir not in path.parts:
                issues.append({"page": str(path.relative_to(WIKI_DIR)), "issue": f"type is '{page_type}' but file is not in {expected_dir}/"})
    return issues


def check_tag_singletons(pages: dict[str, Path]) -> list[str]:
    tag_counts: Counter = Counter()
    for name, path in pages.items():
        if path.name in EXEMPT_FILES:
            continue
        fm = parse_frontmatter(path)
        if fm and "tags" in fm and isinstance(fm["tags"], list):
            tag_counts.update(fm["tags"])
    return [tag for tag, count in tag_counts.items() if count == 1]


def check_index_coverage(pages: dict[str, Path]) -> list[str]:
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return ["index.md not found"]
    index_links = {stem(t) for t in extract_wikilinks(index_path)}
    missing = []
    for name, path in pages.items():
        if path.name in EXEMPT_FILES:
            continue
        if name not in index_links:
            missing.append(str(path.relative_to(WIKI_DIR)))
    return missing


def check_source_refs(pages: dict[str, Path], raw_dir: Path) -> list[dict]:
    raw_items = set()
    if raw_dir.exists():
        for p in raw_dir.iterdir():
            raw_items.add(p.name)
    issues = []
    for name, path in pages.items():
        if path.name in EXEMPT_FILES:
            continue
        fm = parse_frontmatter(path)
        if fm and "sources" in fm and isinstance(fm["sources"], list):
            for src in fm["sources"]:
                if src not in raw_items:
                    issues.append({"page": str(path.relative_to(WIKI_DIR)), "invalid_source": src})
    return issues


def compute_link_density(pages: dict[str, Path]) -> dict:
    outbound: dict[str, int] = {}
    inbound: dict[str, int] = defaultdict(int)
    for name, path in pages.items():
        links = extract_wikilinks(path)
        outbound[str(path.relative_to(WIKI_DIR))] = len(links)
        for target in links:
            s = stem(target)
            if s in pages:
                inbound[str(pages[s].relative_to(WIKI_DIR))] += 1
    return {
        "outbound": outbound,
        "inbound": dict(inbound),
    }


def find_missing_concept_candidates(pages: dict[str, Path]) -> list[dict]:
    """Find bold/backtick terms that appear 3+ times across pages but have no wiki page."""
    term_counts: Counter = Counter()
    term_pages: dict[str, list[str]] = defaultdict(list)

    for name, path in pages.items():
        if path.name in EXEMPT_FILES:
            continue
        terms = extract_bold_terms(path)
        seen = set()
        for t in terms:
            s = stem(t)
            if s not in seen:
                term_counts[s] += 1
                term_pages[s].append(str(path.relative_to(WIKI_DIR)))
                seen.add(s)

    candidates = []
    for term_stem, count in term_counts.most_common():
        if count >= 3 and term_stem not in pages:
            candidates.append({
                "term": term_stem,
                "occurrences": count,
                "in_pages": term_pages[term_stem],
            })
    return candidates


def compute_stats(pages: dict[str, Path]) -> dict:
    type_counts: Counter = Counter()
    total_tags = set()
    total_links = 0
    for name, path in pages.items():
        if path.name in EXEMPT_FILES:
            continue
        fm = parse_frontmatter(path)
        if fm:
            type_counts[fm.get("type", "unknown")] += 1
            if isinstance(fm.get("tags"), list):
                total_tags.update(fm["tags"])
        total_links += len(extract_wikilinks(path))
    return {
        "total_pages": len(pages) - len([p for p in pages.values() if p.name in EXEMPT_FILES]),
        "total_links": total_links,
        "total_unique_tags": len(total_tags),
        "pages_by_type": dict(type_counts),
    }


# --- Main ---

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Wiki health check")
    parser.add_argument("--wiki-dir", default="wiki", help="Path to wiki directory")
    parser.add_argument("--raw-dir", default="raw", help="Path to raw sources directory")
    args = parser.parse_args()

    global WIKI_DIR, RAW_DIR
    WIKI_DIR = Path(args.wiki_dir)
    RAW_DIR = Path(args.raw_dir)

    if not WIKI_DIR.exists():
        print(json.dumps({"error": f"Wiki directory not found: {WIKI_DIR}"}))
        sys.exit(1)

    pages = collect_pages(WIKI_DIR)

    report = {
        "checks": {
            "broken_links": check_broken_links(pages),
            "orphan_pages": check_orphan_pages(pages),
            "frontmatter_issues": check_frontmatter(pages),
            "tag_singletons": check_tag_singletons(pages),
            "missing_from_index": check_index_coverage(pages),
            "invalid_source_refs": check_source_refs(pages, RAW_DIR),
        },
        "stats": compute_stats(pages),
        "link_density": compute_link_density(pages),
        "candidates_for_llm_review": {
            "frequently_mentioned_terms_without_pages": find_missing_concept_candidates(pages),
        },
    }

    has_issues = any(
        bool(v) for v in report["checks"].values()
    )

    print(json.dumps(report, indent=2))
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
