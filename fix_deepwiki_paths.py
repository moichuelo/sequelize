#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
import shutil
from urllib.parse import urlparse, urlunparse

# Matches Markdown links/images and captures the URL part (either http(s) or path-only starting with '/')
MD_LINK_RE = re.compile(r'(!?\[.*?\]\()(?P<url>(?:https?://[^)\s]+)|(?:/[^)\s]+))(\))')
# Matches bare http(s) URLs in text
PLAIN_URL_RE = re.compile(r'(?P<url>https?://[^)\s<>"\]]+)')

def clean_slug(segment: str) -> str:
    # Remove numeric prefixes like "2.1-" or "10-"
    return re.sub(r'^[\d][\d\.-]*-?', '', segment)

def rewrite_path(path: str) -> str:
    # Keep fragment
    if "#" in path:
        path_part, frag = path.split("#", 1)
        frag = "#" + frag
    else:
        path_part, frag = path, ""
    without_trailing = path_part.rstrip("/")
    last = without_trailing.rsplit("/", 1)[-1] if "/" in without_trailing else without_trailing
    if not last:
        return path  # nothing to do
    slug = clean_slug(last) or last
    return f"/{slug}/{frag}"

def rewrite_value(value: str, base_netloc: str) -> str:
    # If it's an http(s) URL, only rewrite if host matches base
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        if parsed.netloc != base_netloc:
            return value
        new_path = rewrite_path(parsed.path + (("#" + parsed.fragment) if parsed.fragment else ""))
        new_parsed = parsed._replace(path=new_path.split("#",1)[0], fragment=new_path.split("#",1)[1] if "#" in new_path else "")
        return urlunparse(new_parsed)
    # If it is a site-absolute path
    if value.startswith("/"):
        return rewrite_path(value)
    return value

def process_text(text: str, base_netloc: str, changed_counter: list) -> str:
    def repl_md(m):
        url = m.group('url')
        new_url = rewrite_value(url, base_netloc)
        if new_url != url:
            changed_counter[0] += 1
        return f"{m.group(1)}{new_url}{m.group(3)}"
    text = MD_LINK_RE.sub(repl_md, text)

    def repl_plain(m):
        url = m.group('url')
        new_url = rewrite_value(url, base_netloc)
        if new_url != url:
            changed_counter[0] += 1
        return new_url
    text = PLAIN_URL_RE.sub(repl_plain, text)
    return text

def process_file(path: Path, base_netloc: str, dry_run: bool, backup: bool) -> int:
    text = path.read_text(encoding='utf-8')
    changed = [0]
    new_text = process_text(text, base_netloc, changed)
    if changed[0] and not dry_run:
        if backup:
            shutil.copy2(path, path.with_suffix(path.suffix + '.bak'))
        path.write_text(new_text, encoding='utf-8')
    return changed[0]

def main():
    parser = argparse.ArgumentParser(description="Reescribe URLs de deepwiki a formato /<slug>/, incluyendo rutas absolutas en Markdown.")
    parser.add_argument('--docs-dir', default='docs', help='Carpeta con Markdown (por defecto: docs)')
    parser.add_argument('--host', default='127.0.0.1:8000', help='Host/puerto a tratar como base (por defecto: 127.0.0.1:8000)')
    parser.add_argument('--dry-run', action='store_true', help='Muestra cambios sin escribir archivos')
    parser.add_argument('--no-backup', action='store_true', help='No crear backups .bak')
    args = parser.parse_args()

    base_netloc = args.host

    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.exists():
        print(f"No existe la carpeta: {docs_dir}")
        return

    total_files = 0
    total_changes = 0
    for md in docs_dir.rglob('*.md'):
        total_files += 1
        changes = process_file(md, base_netloc, dry_run=args.dry_run, backup=not args.no_backup)
        if changes:
            print(f"{md.relative_to(docs_dir)}: {changes} enlace(s) corregido(s)")
            total_changes += changes

    print(f"\nProcesados {total_files} archivos.")
    if args.dry_run:
        print(f"Se corregirían {total_changes} enlaces.")
    else:
        print(f"Se corrigieron {total_changes} enlaces.")

if __name__ == '__main__':
    main()
