"""Pretvara docs/upute_i_osvrt.html u PDF (python docs/napravi_pdf.py)."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

here = Path(__file__).resolve().parent
with sync_playwright() as p:
    exe = os.environ.get("CHROMIUM_PATH") or ("/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None)
    browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    page = browser.new_page()
    page.goto((here / "upute_i_osvrt.html").as_uri())
    page.wait_for_load_state("networkidle")
    page.pdf(path=str(here / "upute_i_osvrt.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
    browser.close()
print("docs/upute_i_osvrt.pdf")
