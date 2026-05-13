#!/usr/bin/env python3
"""Assemble HTML long-page from template + content fragments."""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Assemble HTML long-page")
    parser.add_argument("--template", required=True, help="Path to page.html template")
    parser.add_argument("--content", required=True, help="Path to content HTML fragment")
    parser.add_argument("--nav", required=True, help="Path to nav HTML fragment")
    parser.add_argument("--glossary", required=True, help="Path to glossary JSON file")
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")
    content = Path(args.content).read_text(encoding="utf-8")
    nav = Path(args.nav).read_text(encoding="utf-8")
    glossary_raw = Path(args.glossary).read_text(encoding="utf-8")

    # Validate glossary is valid JSON
    try:
        json.loads(glossary_raw)
    except json.JSONDecodeError as e:
        print(f"Error: glossary file is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    html = template
    html = html.replace("{{PAPER_TITLE}}", args.title)
    html = html.replace("{{NAV_ITEMS}}", nav)
    html = html.replace("{{CONTENT}}", content)
    html = html.replace("{{GLOSSARY_DATA}}", glossary_raw)

    Path(args.output).write_text(html, encoding="utf-8")
    print(f"Assembled: {args.output} ({Path(args.output).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
