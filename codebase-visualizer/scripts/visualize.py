#!/usr/bin/env python3
"""Generate an interactive collapsible HTML tree of a codebase."""

import os
import sys
import json
import argparse

IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.idea', '.vscode',
    'target', 'build', 'dist', '.gradle', '.mvn', 'out',
    '.cache', '.pytest_cache', '.mypy_cache', 'venv', '.venv',
    'coverage', '.coverage', 'htmlcov',
}

IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitkeep',
}

EXT_COLORS = {
    '.java':   '#f89820',
    '.kt':     '#7F52FF',
    '.scala':  '#DC322F',
    '.py':     '#3572A5',
    '.js':     '#F1E05A',
    '.ts':     '#2B7489',
    '.tsx':    '#2B7489',
    '.jsx':    '#F1E05A',
    '.html':   '#E44B23',
    '.css':    '#563D7C',
    '.scss':   '#C6538C',
    '.xml':    '#0060ac',
    '.json':   '#40af41',
    '.yaml':   '#CB171E',
    '.yml':    '#CB171E',
    '.md':     '#083fa1',
    '.sql':    '#e38c00',
    '.sh':     '#89E051',
    '.bat':    '#C1F12E',
    '.groovy': '#4298B8',
    '.properties': '#aaa',
    '.txt':    '#ccc',
}

def human_size(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1024
    return f'{n:.1f} TB'

def build_tree(root):
    root = os.path.abspath(root)
    def recurse(path):
        name = os.path.basename(path)
        if os.path.isfile(path):
            if name in IGNORE_FILES:
                return None
            size = os.path.getsize(path)
            ext = os.path.splitext(name)[1].lower()
            return {'type': 'file', 'name': name, 'size': size, 'ext': ext}
        elif os.path.isdir(path):
            if name in IGNORE_DIRS:
                return None
            children = []
            try:
                entries = sorted(os.scandir(path), key=lambda e: (e.is_file(), e.name.lower()))
            except PermissionError:
                return None
            for entry in entries:
                child = recurse(entry.path)
                if child is not None:
                    children.append(child)
            total = sum(c.get('size', c.get('total', 0)) for c in children)
            return {'type': 'dir', 'name': name, 'total': total, 'children': children}
        return None
    return recurse(root)

def render_html(tree, root_path):
    tree_json = json.dumps(tree, separators=(',', ':'))
    ext_colors_json = json.dumps(EXT_COLORS)
    title = os.path.basename(root_path)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title} — codebase map</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Consolas','Fira Mono','Menlo',monospace; font-size: 13px;
          background: #1e1e2e; color: #cdd6f4; padding: 16px; }}
  h1 {{ font-size: 16px; color: #cba6f7; margin-bottom: 12px; }}
  ul {{ list-style: none; padding-left: 18px; }}
  li {{ line-height: 1.7; }}
  .toggle {{ cursor: pointer; user-select: none; }}
  .toggle::before {{ content: '▶ '; font-size: 10px; color: #89b4fa; }}
  .open > .toggle::before {{ content: '▼ '; }}
  .dir-name {{ color: #89b4fa; font-weight: bold; }}
  .dir-size {{ color: #585b70; font-size: 11px; margin-left: 6px; }}
  .file-name {{ color: #cdd6f4; }}
  .file-size {{ color: #585b70; font-size: 11px; margin-left: 6px; }}
  .dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%;
           margin-right: 5px; vertical-align: middle; }}
  #search {{ background:#313244; border:1px solid #45475a; color:#cdd6f4;
              padding:6px 10px; border-radius:6px; width:300px; margin-bottom:12px; font-size:13px; }}
  #search::placeholder {{ color:#585b70; }}
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
<h1>📁 {title}</h1>
<input id="search" type="text" placeholder="Filter files…" oninput="filterTree(this.value)">
<div id="tree"></div>
<script>
const EXT_COLORS = {ext_colors_json};
const data = {tree_json};

function humanSize(n) {{
  if (n < 1024) return n + ' B';
  if (n < 1048576) return (n/1024).toFixed(1) + ' KB';
  if (n < 1073741824) return (n/1048576).toFixed(1) + ' MB';
  return (n/1073741824).toFixed(1) + ' GB';
}}

function renderNode(node) {{
  const li = document.createElement('li');
  if (node.type === 'dir') {{
    li.className = 'open';
    const toggle = document.createElement('span');
    toggle.className = 'toggle';
    toggle.innerHTML = '<span class="dir-name">📂 ' + escHtml(node.name) + '</span>'
      + '<span class="dir-size">' + humanSize(node.total) + '</span>';
    toggle.onclick = () => {{
      li.classList.toggle('open');
      const ul = li.querySelector(':scope > ul');
      if (ul) ul.style.display = li.classList.contains('open') ? '' : 'none';
    }};
    li.appendChild(toggle);
    const ul = document.createElement('ul');
    (node.children || []).forEach(child => ul.appendChild(renderNode(child)));
    li.appendChild(ul);
  }} else {{
    const ext = node.ext || '';
    const color = EXT_COLORS[ext] || '#a6adc8';
    li.innerHTML = '<span class="dot" style="background:' + color + '"></span>'
      + '<span class="file-name" data-name="' + escHtml(node.name) + '">' + escHtml(node.name) + '</span>'
      + '<span class="file-size">' + humanSize(node.size) + '</span>';
  }}
  return li;
}}

function escHtml(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function filterTree(q) {{
  q = q.trim().toLowerCase();
  document.querySelectorAll('#tree li').forEach(li => li.classList.remove('hidden'));
  if (!q) return;
  document.querySelectorAll('#tree [data-name]').forEach(span => {{
    const li = span.closest('li');
    if (!span.dataset.name.toLowerCase().includes(q)) {{
      li.classList.add('hidden');
    }}
  }});
}}

const root = document.getElementById('tree');
const ul = document.createElement('ul');
ul.appendChild(renderNode(data));
root.appendChild(ul);
</script>
</body>
</html>"""

def main():
    parser = argparse.ArgumentParser(description='Visualize codebase as interactive HTML tree.')
    parser.add_argument('root', nargs='?', default='.', help='Root directory (default: .)')
    parser.add_argument('-o', '--output', default='codebase-map.html', help='Output HTML file')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    print(f'Scanning {root} …', file=sys.stderr)
    tree = build_tree(root)
    if tree is None:
        print('Error: could not read directory.', file=sys.stderr)
        sys.exit(1)

    out = os.path.join(root, args.output)
    html = render_html(tree, root)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written: {out}', file=sys.stderr)
    print(out)

if __name__ == '__main__':
    main()
