"""HTML export support."""

from __future__ import annotations

import html
import re

from reportforge.exporters.markdown import export_markdown
from reportforge.schemas import Report


def export_html(report: Report) -> str:
    """Render a report as a standalone HTML document."""

    markdown = export_markdown(report)
    body = markdown_to_html(markdown)
    return f"""<!doctype html>
<html lang="{report.language.value}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(report.title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #060b0a;
      --panel: #0d1c18;
      --panel-2: #10251f;
      --line: #1f4a3c;
      --text: #e6fff4;
      --muted: #98b9aa;
      --accent: #2ff58f;
      --warn: #ffcf5a;
      --critical: #ff5d73;
    }}
    body {{
      margin: 0;
      background:
        linear-gradient(180deg, rgba(47, 245, 143, 0.07), transparent 260px),
        var(--bg);
      color: var(--text);
      font: 15px/1.6 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 980px;
      margin: 0 auto;
      padding: 48px 24px 72px;
    }}
    main::before {{
      content: "REPORTFORGE / AUTHORIZED SECURITY REPORT";
      display: block;
      margin-bottom: 22px;
      color: var(--muted);
      font: 700 12px/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      letter-spacing: 0;
    }}
    h1, h2, h3 {{
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h1 {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      color: var(--accent);
      font-size: 34px;
    }}
    h2 {{
      margin-top: 38px;
      color: #b8ffe0;
    }}
    h3 {{
      margin-top: 30px;
      color: var(--warn);
    }}
    p, li {{
      color: var(--text);
    }}
    p {{
      max-width: 82ch;
    }}
    a {{
      color: var(--accent);
    }}
    code {{
      background: #102820;
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 1px 5px;
      color: #c9ffe6;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 24px;
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: 0 0 0 1px rgba(47, 245, 143, 0.05), 0 16px 48px rgba(0, 0, 0, 0.22);
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--accent);
      font-weight: 700;
      background: var(--panel-2);
    }}
    tr:hover td {{
      background: rgba(47, 245, 143, 0.04);
    }}
    blockquote {{
      margin: 18px 0;
      padding: 12px 16px;
      border-left: 3px solid var(--accent);
      background: var(--panel);
      color: var(--muted);
    }}
    @media print {{
      :root {{
        color-scheme: light;
        --bg: #ffffff;
        --panel: #f6faf8;
        --panel-2: #edf7f2;
        --line: #c6d8cf;
        --text: #10201a;
        --muted: #486258;
        --accent: #0d6b45;
        --warn: #735900;
      }}
      body {{
        background: #ffffff;
      }}
      main {{
        padding: 24px;
      }}
      table {{
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  <main>
{body}
  </main>
</body>
</html>
"""


def markdown_to_html(markdown: str) -> str:
    """Convert the limited ReportForge Markdown dialect to HTML."""

    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_list = False
    in_table = False

    for line in lines:
        stripped = line.strip()
        if in_table and not stripped.startswith("|"):
            html_lines.append("</tbody></table>")
            in_table = False
        if in_list and not stripped.startswith("- "):
            html_lines.append("</ul>")
            in_list = False

        if not stripped:
            continue
        if stripped.startswith("|"):
            if set(stripped.replace("|", "").replace(" ", "")) <= {"-", ":"}:
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not in_table:
                html_lines.append("<table><tbody>")
                in_table = True
                html_lines.append(_table_row(cells, header=True))
            else:
                html_lines.append(_table_row(cells))
            continue
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{_inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{_inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{_inline(stripped[4:])}</h3>")
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline(stripped[2:])}</li>")
        else:
            html_lines.append(f"<p>{_inline(stripped)}</p>")

    if in_table:
        html_lines.append("</tbody></table>")
    if in_list:
        html_lines.append("</ul>")
    return "\n".join(f"    {line}" for line in html_lines)


def _table_row(cells: list[str], header: bool = False) -> str:
    tag = "th" if header else "td"
    return "<tr>" + "".join(f"<{tag}>{_inline(cell)}</{tag}>" for cell in cells) + "</tr>"


def _inline(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped
