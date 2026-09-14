"""
PDF rendering engine.
Transforms report data and Jinja2 HTML templates into professional multi-page PDF documents.
Uses Playwright headless Chromium with graceful fallback to WeasyPrint.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader

from src.config import REPORTS_DIR, TEMPLATES_DIR


def render_html(data: Dict[str, Any], template_name: str = "report.html") -> str:
    """Render report HTML from Jinja2 template."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template(template_name)
    now_str = datetime.now().strftime("%B %d, %Y")
    return template.render(
        generated_date=now_str,
        summary=data["summary"],
        top_5_expensive=data["top_5_expensive"],
        ratings_breakdown=data["ratings_breakdown"],
        all_books=data["all_books"],
    )


async def render_pdf_playwright(html_content: str, output_path: Path) -> Path:
    """Render PDF using Playwright headless Chromium."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={"top": "18mm", "bottom": "18mm", "left": "15mm", "right": "15mm"},
        )
        await browser.close()
    return output_path


def render_pdf_weasyprint(html_content: str, output_path: Path) -> Path:
    """Render PDF using WeasyPrint (standards-compliant CSS Paged Media renderer)."""
    from weasyprint import HTML
    HTML(string=html_content).write_pdf(target=str(output_path))
    return output_path


async def generate_pdf_report(data: Dict[str, Any], output_path: Path) -> Path:
    """
    Generate PDF report file:
    1. Compiles HTML with Jinja2.
    2. Renders PDF via Playwright (or WeasyPrint if browser sandbox / lib missing).
    3. Guarantees output file exists on disk.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_html(data)

    try:
        await render_pdf_playwright(html, output_path)
    except Exception as e:
        print(f"[RENDER FALLBACK] Playwright render encountered {e}, falling back to WeasyPrint...")
        render_pdf_weasyprint(html, output_path)

    return output_path
