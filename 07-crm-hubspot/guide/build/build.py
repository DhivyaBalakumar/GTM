"""Build the HubSpot guide: Markdown chapters -> HTML -> PDF (Chromium) and DOCX (pandoc)."""
import glob, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(HERE)
OUT = GUIDE
chapters = sorted(glob.glob(os.path.join(GUIDE, "ch*.md")))
front = os.path.join(GUIDE, "00-front-matter.md")
PARTS = {
    "ch01": ("Part I", "Foundations", "What HubSpot is, how its data is shaped, and how properties work."),
    "ch04": ("Part II", "Getting Data In (and Out)", "Every way data enters HubSpot: by hand, imports, forms, tracking, integrations, the API, webhooks, an end-to-end pipeline, and keeping it clean."),
    "ch13": ("Part III", "Using Your Data", "Segments, workflows and each hub: Marketing, Sales, Service, Content, Commerce and AI."),
    "ch19": ("Part IV", "Running HubSpot", "Reporting, administration, governance, RevOps architecture, troubleshooting and interviews."),
    "ch23": ("Appendix", "Reference", "Cheat sheets and glossary."),
}
def part_div(key):
    n, t, d = PARTS[key]
    return f'\n\n```{{=html}}\n<div class="part-page"><div class="pn">{n}</div><div class="pt">{t}</div><div class="pd">{d}</div></div>\n```\n\n'

body_html, body_docx = [], []
with open(front) as f:
    fm = f.read()
for path in chapters:
    key = os.path.basename(path)[:4]
    with open(path) as f:
        txt = f.read().strip() + "\n\n"
    if key in PARTS:
        body_html.append(part_div(key))
    body_html.append(txt); body_docx.append(txt)

def write(name, parts):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        f.write(fm + "\n\n" + "".join(parts))
    return p

md_html = write("book_html.md", body_html)
md_docx = write("book_docx.md", body_docx)
html = os.path.join(HERE, "book.html")
subprocess.run(["pandoc", md_html, "-o", html, "--standalone", "--toc", "--toc-depth=2",
                "--css", "style.css", "--embed-resources", "--metadata", "toc-title=Contents",
                "--highlight-style=tango", "-f", "markdown-yaml_metadata_block+yaml_metadata_block", "--resource-path", HERE], check=True, cwd=HERE)
# custom title page
s = open(html).read()
s = re.sub(r'<header id="title-block-header">.*?</header>',
    '<div class="title-page"><div class="t">The Complete<br>HubSpot CRM Guide</div><div class="bar"></div>'
    '<div class="s">From pushing your first record to running a revenue engine: data model, imports, API, webhooks, automation, every hub, reporting, governance and RevOps playbooks.</div>'
    '<div class="d">Edition: November 2026 &middot; Running example: Northwind Analytics</div></div>', s, flags=re.S)
s = s.replace('<h2 id="toc-title">Contents</h2>', '<div class="toc-title">Contents</div>')
open(html, "w").write(s)

from playwright.sync_api import sync_playwright
pdf = os.path.join(OUT, "HubSpot-CRM-Complete-Guide.pdf")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto("file://" + html); pg.wait_for_timeout(500)
    pg.pdf(path=pdf, format="A4", print_background=True, display_header_footer=True,
           header_template="<div></div>",
           footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#888;font-family:sans-serif">The Complete HubSpot CRM Guide &middot; <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
           margin={"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
docx = os.path.join(OUT, "HubSpot-CRM-Complete-Guide.docx")
subprocess.run(["pandoc", md_docx, "-o", docx, "--toc", "--toc-depth=2", "--highlight-style=tango",
                "--metadata", "toc-title=Contents"], check=True, cwd=HERE)
print("built", pdf, docx)
