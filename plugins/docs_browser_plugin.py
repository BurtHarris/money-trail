from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

import markdown
from airflow.plugins_manager import AirflowPlugin
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse


REPO_ROOT = Path(__file__).resolve().parents[1]
CURATED_ROOT_FILES = [REPO_ROOT / "README.md", REPO_ROOT / "CONTEXT.md"]
DOCS_ROOT = REPO_ROOT / "docs"
DOCS_PREFIX = "/docs-browser"


@dataclass(frozen=True)
class Document:
    rel_path: str
    path: Path
    section: str
    title: str
    summary: str
    content: str


def curated_markdown_files() -> list[Path]:
    files = [path for path in CURATED_ROOT_FILES if path.is_file()]
    if DOCS_ROOT.is_dir():
        files.extend(sorted(path for path in DOCS_ROOT.rglob("*.md") if path.is_file()))
    return files


def document_section(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT).as_posix()
    if relative in {"README.md", "CONTEXT.md"}:
        return "Repository"
    parts = path.relative_to(DOCS_ROOT).parts
    if not parts:
        return "docs"
    if len(parts) == 1:
        return "docs"
    return "docs/" + "/".join(parts[:-1])


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def extract_summary(content: str) -> str:
    heading_seen = False
    paragraph_lines: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            if heading_seen and paragraph_lines:
                break
            continue
        if stripped.startswith("# ") and not heading_seen:
            heading_seen = True
            continue
        if stripped.startswith("# ") and heading_seen and paragraph_lines:
            break
        if heading_seen:
            paragraph_lines.append(stripped)
    summary = " ".join(paragraph_lines).strip()
    if len(summary) > 220:
        summary = summary[:217].rsplit(" ", 1)[0] + "..."
    return summary


def collect_documents() -> list[Document]:
    documents: list[Document] = []
    for path in curated_markdown_files():
        content = path.read_text(encoding="utf-8")
        rel_path = path.relative_to(REPO_ROOT).as_posix()
        documents.append(
            Document(
                rel_path=rel_path,
                path=path,
                section=document_section(path),
                title=extract_title(content, path.stem),
                summary=extract_summary(content),
                content=content,
            )
        )
    documents.sort(key=lambda doc: (doc.section, doc.title.lower(), doc.rel_path.lower()))
    return documents


def doc_lookup() -> dict[str, Document]:
    return {doc.rel_path: doc for doc in collect_documents()}


def search_documents(documents: Iterable[Document], query: str) -> list[tuple[Document, int, str]]:
    terms = [term for term in re.split(r"\s+", query.strip().lower()) if term]
    if not terms:
        return [(doc, 0, "") for doc in documents]

    results: list[tuple[Document, int, str]] = []
    for doc in documents:
        haystack = f"{doc.title}\n{doc.summary}\n{doc.content}".lower()
        score = sum(haystack.count(term) for term in terms)
        if score <= 0:
            continue
        snippet = document_snippet(doc.content, terms)
        results.append((doc, score, snippet))

    results.sort(key=lambda item: (-item[1], item[0].section, item[0].title.lower()))
    return results


def document_snippet(content: str, terms: list[str], width: int = 220) -> str:
    lines = content.splitlines()
    lowered_lines = [line.lower() for line in lines]
    for index, line in enumerate(lowered_lines):
        if any(term in line for term in terms):
            start = max(0, index - 1)
            end = min(len(lines), index + 2)
            snippet = " ".join(segment.strip() for segment in lines[start:end] if segment.strip())
            if len(snippet) > width:
                snippet = snippet[: width - 3].rsplit(" ", 1)[0] + "..."
            return snippet
    summary = " ".join(segment.strip() for segment in lines if segment.strip())
    if len(summary) > width:
        summary = summary[: width - 3].rsplit(" ", 1)[0] + "..."
    return summary


def markdown_to_html(content: str) -> str:
    return markdown.markdown(
        content,
        extensions=["fenced_code", "tables", "toc"],
        output_format="html5",
    )


def strip_first_h1(content: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.lstrip().startswith("# "):
            remaining = lines[index + 1 :]
            while remaining and not remaining[0].strip():
                remaining = remaining[1:]
            return "\n".join(remaining)
        break
    return content


def render_page(
    title: str,
    body: str,
    search_value: str = "",
    search_action: str = ".",
    doc_link: str = "../",
    show_print: bool = False,
) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light dark;
    }}
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      padding: 0;
      line-height: 1.55;
      background: #f8fafc;
      color: #111827;
    }}
    .shell {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 16px;
    }}
    .toolbar {{
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-bottom: 12px;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 10px;
      background: #fff;
    }}
    .toolbar form {{
      display: flex;
      gap: 8px;
      flex: 1 1 420px;
    }}
    .toolbar input {{
      flex: 1;
      min-width: 220px;
      padding: 8px 10px;
      border: 1px solid #9ca3af;
      border-radius: 8px;
      font-size: 13px;
    }}
    .toolbar button, .toolbar a.button {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 12px;
      border: 1px solid #2563eb;
      border-radius: 8px;
      background: #2563eb;
      color: #fff;
      text-decoration: none;
      cursor: pointer;
      font-size: 13px;
    }}
    .toolbar a.secondary {{
      background: transparent;
      color: #2563eb;
    }}
    .toolbar button.secondary {{
      background: transparent;
      color: #2563eb;
    }}
    .meta {{
      color: #6b7280;
      font-size: 13px;
    }}
    .card {{
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 10px;
      box-shadow: 0 1px 1px rgba(0, 0, 0, 0.03);
    }}
    .grid {{
      display: grid;
      gap: 14px;
    }}
    .doc-list {{
      display: grid;
      gap: 8px;
    }}
    .doc-item {{
      padding: 10px 12px;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      background: #fff;
    }}
    .doc-item h3 {{
      margin: 0 0 6px;
      font-size: 16px;
    }}
    .doc-item p {{
      margin: 0;
      color: #374151;
    }}
    .section {{
      margin-top: 16px;
    }}
    .doc-body {{
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 16px;
      overflow-wrap: anywhere;
    }}
    .doc-body pre {{
      overflow-x: auto;
      padding: 14px;
      border-radius: 10px;
      background: #111827;
      color: #f9fafb;
    }}
    .doc-body code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.95em;
    }}
    .doc-body table {{
      border-collapse: collapse;
      width: 100%;
    }}
    .doc-body th, .doc-body td {{
      border: 1px solid #d1d5db;
      padding: 8px 10px;
      text-align: left;
    }}
    .doc-body img {{
      max-width: 100%;
    }}
    @media print {{
      body {{
        background: #fff;
      }}
      .toolbar, .meta, .no-print {{
        display: none !important;
      }}
      .shell {{
        max-width: none;
        padding: 0;
      }}
      .card, .doc-body {{
        border: 0;
        box-shadow: none;
        padding: 0;
      }}
      a {{
        color: inherit;
        text-decoration: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="toolbar no-print">
      <form method="get" action="{escape(search_action)}">
        <input name="q" type="search" value="{escape(search_value)}" placeholder="Search docs">
        <button type="submit">Search</button>
      </form>
      {"<button type=\"button\" class=\"secondary\" onclick=\"window.print()\">Print</button>" if show_print else ""}
      <a class="button secondary" href="{escape(doc_link)}">Home</a>
    </div>
    {body}
  </div>
</body>
</html>"""


def render_index(documents: list[Document], query: str) -> str:
    matches = search_documents(documents, query)
    sections: dict[str, list[tuple[Document, int, str]]] = {}
    for item in matches:
        sections.setdefault(item[0].section, []).append(item)

    parts = [
        '<div class="card">',
        "<h1>money-trail docs</h1>",
        "<p>Browse the repository docs in one place. Use search to jump straight to a topic, then print any page from the browser.</p>",
        f'<p class="meta">{len(documents)} documents available</p>',
        "</div>",
    ]

    if query.strip() and not matches:
        parts.append('<div class="card"><p>No documents matched that search.</p></div>')
    else:
        for section in sorted(sections, key=lambda value: (value != "Repository", value.lower())):
            parts.append(f'<div class="section"><h2>{escape(section)}</h2><div class="doc-list">')
            for doc, score, snippet in sections[section]:
                href = f"doc/{quote(doc.rel_path)}"
                parts.append(
                    "<div class=\"doc-item\">"
                    f"<h3><a href=\"{href}\">{escape(doc.title)}</a></h3>"
                    f"<p class=\"meta\">{escape(doc.rel_path)}</p>"
                    f"<p>{escape(snippet or doc.summary or 'No summary available.')}</p>"
                    "</div>"
                )
            parts.append("</div></div>")

    body = "".join(parts)
    return render_page(
        "money-trail docs",
        body,
        search_value=query,
        search_action=f"{DOCS_PREFIX}/",
        doc_link=f"{DOCS_PREFIX}/",
    )


def render_document(document: Document) -> str:
    rendered_content = markdown_to_html(strip_first_h1(document.content))
    body = (
        '<div class="card">'
        f'<p class="meta"><a href="{DOCS_PREFIX}/">Docs</a> / {escape(document.rel_path)}</p>'
        f"<h1>{escape(document.title)}</h1>"
        "</div>"
        f'<article class="doc-body">{rendered_content}</article>'
    )
    return render_page(
        document.title,
        body,
        search_action=f"{DOCS_PREFIX}/",
        doc_link=f"{DOCS_PREFIX}/",
        show_print=True,
    )


app = FastAPI(title="money-trail docs")


@app.get("/", response_class=HTMLResponse)
def docs_index(q: str = Query(default="")) -> HTMLResponse:
    return HTMLResponse(render_index(collect_documents(), q))


@app.get("/doc/{doc_path:path}", response_class=HTMLResponse)
def docs_page(doc_path: str) -> HTMLResponse:
    lookup = doc_lookup()
    document = lookup.get(doc_path)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return HTMLResponse(render_document(document))


docs_external_view = {
    "name": "money-trail docs",
    "href": f"{DOCS_PREFIX}/",
    "destination": "nav",
    "url_route": "docs-browser",
    "category": "docs",
}


docs_app = {
    "app": app,
    "url_prefix": DOCS_PREFIX,
    "name": "money-trail docs",
}


class MoneyTrailDocsPlugin(AirflowPlugin):
    name = "money_trail_docs"
    fastapi_apps = [docs_app]
    external_views = [docs_external_view]
