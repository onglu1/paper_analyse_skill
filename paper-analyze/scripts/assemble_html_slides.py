#!/usr/bin/env python3
"""Assemble HTML slides from template + sections fragment."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Assemble HTML slides")
    parser.add_argument("--template", required=True, help="Path to slides.html template")
    parser.add_argument("--sections", required=True, help="Path to sections HTML fragment")
    parser.add_argument("--title", required=True, help="Paper title")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")
    sections = Path(args.sections).read_text(encoding="utf-8")

    html = template
    html = html.replace("{{TITLE}}", args.title)
    html = html.replace("{{SLIDES}}", sections)

    Path(args.output).write_text(html, encoding="utf-8")
    print(f"Assembled: {args.output} ({Path(args.output).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
