#!/usr/bin/env python3
"""Build Markdown reports into a dependency-free static report center."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
PUBLIC_DIR = ROOT / "public"
CONFIG_PATH = ROOT / "report-center.json"


def load_config() -> dict:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing configuration: {CONFIG_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {CONFIG_PATH}: {exc}") from exc

    required = {
        "site": ("title", "brand", "hero_kicker", "hero_title", "hero_emphasis", "hero_description"),
        "report_defaults": ("status", "category", "accent"),
        "agent": ("trigger_phrases", "default_workflow", "privacy", "publishing"),
        "preview": ("service_name", "preferred_port", "bind"),
    }
    for section, keys in required.items():
        if not isinstance(config.get(section), dict):
            raise SystemExit(f"Configuration section must be an object: {section}")
        for key in keys:
            if key not in config[section]:
                raise SystemExit(f"Missing configuration key: {section}.{key}")
    if config["preview"]["bind"] != "127.0.0.1":
        raise SystemExit("preview.bind must remain 127.0.0.1 for safe local preview")
    return config


@dataclass
class Report:
    slug: str
    meta: dict[str, str]
    body: str
    source: Path


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"\'')
    return meta, text[end + 5 :]


def inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(
        r"!\[([^\]]*)\]\(((?:https?://|\.\.?/)[^\s)]+)\)",
        r'<img class="content-image" src="\2" alt="\1" loading="lazy">',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        escaped,
    )
    return escaped


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}", line))


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{inline(cell)}</th>" for cell in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_directive(kind: str, lines: list[str], source_dir: Path) -> str:
    if kind == "csv":
        if not lines or not lines[0].strip():
            return '<p class="build-warning">CSV 路径缺失</p>'
        csv_path = (source_dir / lines[0].strip()).resolve()
        try:
            csv_path.relative_to(REPORTS_DIR.resolve())
        except ValueError:
            return '<p class="build-warning">CSV 路径必须位于 reports 目录内</p>'
        if not csv_path.is_file():
            return f'<p class="build-warning">找不到 CSV：{html.escape(lines[0].strip())}</p>'
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            csv_rows = list(csv.reader(handle))
        if not csv_rows:
            return '<p class="build-warning">CSV 文件没有数据</p>'
        return render_table(csv_rows[0], csv_rows[1:])

    rows = [split_cells(line) for line in lines if line.strip()]
    if kind == "metrics":
        cards = []
        for row in rows:
            row += [""] * (3 - len(row))
            cards.append(
                '<article class="metric-card">'
                f'<span class="metric-label">{inline(row[0])}</span>'
                f'<strong>{inline(row[1])}</strong>'
                f'<small>{inline(row[2])}</small></article>'
            )
        return '<section class="metrics" aria-label="核心指标">' + "".join(cards) + "</section>"

    if kind == "progress":
        items = []
        for row in rows:
            row += [""] * (3 - len(row))
            try:
                value = max(0, min(100, int(row[1])))
            except ValueError:
                value = 0
            items.append(
                '<div class="progress-item">'
                f'<div><strong>{inline(row[0])}</strong><span>{inline(row[2])}</span></div>'
                f'<div class="progress-track"><i style="width:{value}%"></i></div>'
                f'<small>{value}%</small></div>'
            )
        return '<section class="progress-list">' + "".join(items) + "</section>"

    if kind == "feedback":
        cards = []
        for row in rows:
            row += [""] * (3 - len(row))
            sentiment = row[0].lower() if row[0].lower() in {"positive", "neutral", "negative"} else "neutral"
            label = {"positive": "正向", "neutral": "建议", "negative": "问题"}[sentiment]
            cards.append(
                f'<blockquote class="feedback {sentiment}"><span>{label}</span>'
                f'<p>{inline(row[1])}</p><cite>{inline(row[2])}</cite></blockquote>'
            )
        return '<section class="feedback-grid">' + "".join(cards) + "</section>"

    return ""


def render_markdown(markdown: str, source_dir: Path = REPORTS_DIR) -> tuple[str, list[tuple[str, str]]]:
    lines = markdown.splitlines()
    output: list[str] = []
    toc: list[tuple[str, str]] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    index = 0
    heading_index = 0

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f'<p>{inline(" ".join(paragraph))}</p>')
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            output.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in list_items) + "</ul>")
            list_items.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith(":::"):
            flush_paragraph()
            flush_list()
            kind = stripped[3:].strip().lower()
            block: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != ":::":
                block.append(lines[index])
                index += 1
            output.append(render_directive(kind, block, source_dir))
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            language = stripped[3:].strip()
            code: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            output.append(
                f'<pre data-language="{html.escape(language)}"><code>{html.escape(chr(10).join(code))}</code></pre>'
            )
            index += 1
            continue

        if index + 1 < len(lines) and "|" in stripped and is_table_separator(lines[index + 1]):
            flush_paragraph()
            flush_list()
            headers = split_cells(line)
            index += 2
            rows = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_cells(lines[index]))
                index += 1
            output.append(render_table(headers, rows))
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            title = heading.group(2)
            if level == 1:
                index += 1
                continue
            heading_index += 1
            anchor = f"section-{heading_index}"
            if level == 2:
                toc.append((title, anchor))
            output.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
        elif stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:])
        elif stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            output.append(f'<blockquote class="callout">{inline(stripped[2:])}</blockquote>')
        elif not stripped:
            flush_paragraph()
            flush_list()
        else:
            paragraph.append(stripped)
        index += 1

    flush_paragraph()
    flush_list()
    return "\n".join(output), toc


def read_reports(config: dict | None = None) -> list[Report]:
    config = config or load_config()
    defaults = config["report_defaults"]
    reports: list[Report] = []
    for source in sorted(REPORTS_DIR.glob("*.md")):
        if source.name.startswith("_"):
            continue
        meta, body = parse_frontmatter(source.read_text(encoding="utf-8"))
        meta.setdefault("title", source.stem.replace("-", " ").title())
        meta.setdefault("date", date.today().isoformat())
        meta.setdefault("status", defaults["status"])
        meta.setdefault("category", defaults["category"])
        meta.setdefault("summary", "打开报告查看完整内容。")
        meta.setdefault("accent", defaults["accent"])
        reports.append(Report(source.stem, meta, body, source))
    return sorted(reports, key=lambda report: report.meta["date"], reverse=True)


def template(name: str) -> str:
    return (ROOT / "templates" / name).read_text(encoding="utf-8")


def build() -> int:
    config = load_config()
    reports = read_reports(config)
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    (PUBLIC_DIR / "reports").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", PUBLIC_DIR / "assets")
    images_dir = REPORTS_DIR / "images"
    if images_dir.is_dir():
        shutil.copytree(images_dir, PUBLIC_DIR / "reports" / "images")

    report_template = template("report.html")
    site = config["site"]
    report_cards = []
    manifest = []

    for report in reports:
        content, toc = render_markdown(report.body, report.source.parent)
        toc_html = "".join(f'<a href="#{anchor}">{inline(title)}</a>' for title, anchor in toc)
        meta = report.meta
        page = report_template
        replacements = {
            "{{TITLE}}": html.escape(meta["title"]),
            "{{SUBTITLE}}": html.escape(meta.get("subtitle", meta["summary"])),
            "{{DATE}}": html.escape(meta["date"]),
            "{{STATUS}}": html.escape(meta["status"]),
            "{{CATEGORY}}": html.escape(meta["category"]),
            "{{SUMMARY}}": html.escape(meta["summary"]),
            "{{ACCENT}}": html.escape(meta["accent"]),
            "{{SITE_TITLE}}": html.escape(site["title"]),
            "{{BRAND}}": html.escape(site["brand"]),
            "{{CONTENT}}": content,
            "{{TOC}}": toc_html,
        }
        for needle, value in replacements.items():
            page = page.replace(needle, value)
        destination = PUBLIC_DIR / "reports" / f"{report.slug}.html"
        destination.write_text(page, encoding="utf-8")

        report_cards.append(
            f'<a class="report-card" href="reports/{report.slug}.html" style="--report-accent:{html.escape(meta["accent"])}">'
            f'<div class="report-card-top"><span>{html.escape(meta["category"])}</span><time>{html.escape(meta["date"])}</time></div>'
            f'<h2>{html.escape(meta["title"])}</h2><p>{html.escape(meta["summary"])}</p>'
            f'<div class="report-card-bottom"><span class="status-dot"></span>{html.escape(meta["status"])}<b>查看报告 →</b></div></a>'
        )
        manifest.append({"slug": report.slug, **meta})

    index_page = template("index.html")
    index_replacements = {
        "{{SITE_TITLE}}": html.escape(site["title"]),
        "{{BRAND}}": html.escape(site["brand"]),
        "{{HERO_KICKER}}": html.escape(site["hero_kicker"]),
        "{{HERO_TITLE}}": html.escape(site["hero_title"]),
        "{{HERO_EMPHASIS}}": html.escape(site["hero_emphasis"]),
        "{{HERO_DESCRIPTION}}": html.escape(site["hero_description"]),
        "{{REPORT_CARDS}}": "\n".join(report_cards),
        "{{REPORT_COUNT}}": str(len(reports)),
    }
    for needle, value in index_replacements.items():
        index_page = index_page.replace(needle, value)
    PUBLIC_DIR.joinpath("index.html").write_text(index_page, encoding="utf-8")
    PUBLIC_DIR.joinpath("reports.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(reports)} report(s) in {PUBLIC_DIR}")
    return len(reports)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when no report was built")
    args = parser.parse_args()
    count = build()
    if args.check and not count:
        raise SystemExit("No reports found")


if __name__ == "__main__":
    main()
