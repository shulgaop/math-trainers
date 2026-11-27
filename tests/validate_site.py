#!/usr/bin/env python3
"""Проверка статического сайта без установки сторонних пакетов."""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REQUIRED_PAGES = ("index.html", "procenty.html", "luch.html")
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


class PageInspector(HTMLParser):
    def __init__(self, page: str) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page
        self.ids: list[str] = []
        self.references: list[tuple[str, str, str]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
        for attribute in ("href", "src", "poster"):
            value = values.get(attribute)
            if value:
                self.references.append((tag, attribute, value))
        if tag == "a" and values.get("target") == "_blank":
            rel = set((values.get("rel") or "").split())
            if "noopener" not in rel:
                self.errors.append(f"{self.page}: target=_blank без rel=noopener: {values.get('href')}")


def inspect_pages() -> tuple[dict[str, PageInspector], list[str], int]:
    pages: dict[str, PageInspector] = {}
    errors: list[str] = []
    reference_count = 0
    for name in REQUIRED_PAGES:
        path = SITE / name
        if not path.is_file():
            errors.append(f"Нет обязательной страницы: site/{name}")
            continue
        inspector = PageInspector(name)
        inspector.feed(path.read_text(encoding="utf-8"))
        inspector.close()
        duplicates = [item for item, count in Counter(inspector.ids).items() if count > 1]
        for item in duplicates:
            inspector.errors.append(f"{name}: повторяющийся id={item}")
        pages[name] = inspector
        reference_count += len(inspector.references)
        errors.extend(inspector.errors)
    return pages, errors, reference_count


def check_references(pages: dict[str, PageInspector]) -> list[str]:
    errors: list[str] = []
    for page_name, inspector in pages.items():
        for tag, attribute, reference in inspector.references:
            parsed = urlsplit(reference)
            if parsed.scheme in EXTERNAL_SCHEMES or parsed.netloc:
                continue
            if parsed.scheme:
                errors.append(f"{page_name}: неподдерживаемая ссылка {reference}")
                continue
            if reference == "#":
                continue

            raw_path = unquote(parsed.path)
            if raw_path.startswith("/"):
                errors.append(f"{page_name}: корневой путь несовместим с подпапкой GitHub Pages: {reference}")
                continue
            if raw_path:
                joined = posixpath.join(posixpath.dirname(page_name), raw_path)
                target_name = posixpath.normpath(joined)
            else:
                target_name = page_name

            if target_name == ".." or target_name.startswith("../"):
                errors.append(f"{page_name}: путь выходит за site: {reference}")
                continue
            target = SITE / target_name
            if target.is_dir():
                target = target / "index.html"
                target_name = posixpath.join(target_name, "index.html")
            if not target.is_file():
                errors.append(f"{page_name}: отсутствует локальный ресурс {reference} ({tag}[{attribute}])")
                continue

            if parsed.fragment and target_name in pages:
                fragment = unquote(parsed.fragment)
                if fragment not in pages[target_name].ids:
                    errors.append(f"{page_name}: нет якоря {reference}")
    return errors


def check_inline_javascript() -> list[str]:
    node = shutil.which("node")
    if not node:
        return []
    errors: list[str] = []
    pattern = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.IGNORECASE | re.DOTALL)
    with tempfile.TemporaryDirectory(prefix="math-site-js-") as directory:
        for page_name in REQUIRED_PAGES:
            text = (SITE / page_name).read_text(encoding="utf-8")
            for number, match in enumerate(pattern.finditer(text), start=1):
                attributes = match.group(1)
                if re.search(r"\bsrc\s*=", attributes, re.IGNORECASE):
                    continue
                script_type = re.search(r"\btype\s*=\s*['\"]([^'\"]+)", attributes, re.IGNORECASE)
                if script_type and script_type.group(1).lower() not in {"text/javascript", "application/javascript", "module"}:
                    continue
                script_path = Path(directory) / f"{page_name}-{number}.js"
                script_path.write_text(match.group(2), encoding="utf-8")
                result = subprocess.run([node, "--check", str(script_path)], capture_output=True, text=True)
                if result.returncode:
                    errors.append(f"{page_name}: синтаксическая ошибка JavaScript в блоке {number}:\n{result.stderr.strip()}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-node", action="store_true", help="Считать отсутствие Node.js ошибкой")
    args = parser.parse_args()

    if not SITE.is_dir():
        print("ОШИБКА: нет папки site", file=sys.stderr)
        return 1

    pages, errors, reference_count = inspect_pages()
    errors.extend(check_references(pages))
    if args.require_node and not shutil.which("node"):
        errors.append("Node.js не найден: невозможно проверить JavaScript")
    errors.extend(check_inline_javascript())

    if errors:
        print(f"ПРОВЕРКА НЕ ПРОЙДЕНА: {len(errors)} ошибок", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    scripts = sum(len(re.findall(r"<script\b[^>]*>", (SITE / name).read_text(encoding="utf-8"), re.IGNORECASE)) for name in pages)
    node_status = "JavaScript проверен через node --check" if shutil.which("node") else "Node.js не найден: синтаксис JavaScript пропущен"
    print(f"OK: страниц — {len(pages)}, локальных и внешних ссылок/ресурсов — {reference_count}, script-блоков — {scripts}")
    print(f"OK: обязательные страницы, уникальные id, локальные ресурсы, якоря и rel=noopener; {node_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
