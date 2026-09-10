import json
import logging
import sys
from playwright.sync_api import sync_playwright

# ==============================================================================
# ENTERPRISE CONFIGURATION & PARAMETER HANDLING (ZERO HARDCODING)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

if len(sys.argv) < 4:
    logging.error("PARAMETER ERROR: Argumen wajib tidak lengkap!")
    logging.error("Penggunaan: python scraper_playwright.py <EMAIL> <PASSWORD> <OUTPUT_JSON_FILE>")
    sys.exit(1)

ACME_EMAIL = sys.argv[1]
ACME_PASSWORD = sys.argv[2]
OUTPUT_JSON_FILE = sys.argv[3]

HEADLESS_MODE = True  # Production Headless Execution
# ==============================================================================


def run_playwright_scraper(email: str, password: str, output_file: str) -> str:
    """
    Enterprise Playwright Engine untuk ekstraksi data ACME System 1 dengan Full Dynamic Pagination.
    """
    scraped_data = []
    logging.info("Memulai Playwright Scraping Engine (Clean Enterprise Mode)...")

    base_domain = "https://acme-test.uipath.com"
    login_url = f"{base_domain}/login"
    work_items_url = f"{base_domain}/work-items"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        try:
            # 1. Authentication Stage
            logging.info(f"Navigasi ke Login Page: {login_url}")
            page.goto(login_url, wait_until="networkidle")

            page.fill("input[name='email']", email)
            page.fill("input[name='password']", password)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")

            if "login" in page.url.lower():
                raise Exception("Authentication Failed! Periksa kredensial pada Orchestrator Asset.")

            # 2. Data Extraction Stage (Dynamic Multi-Page Scraping)
            logging.info(f"Navigasi ke Work Items: {work_items_url}")
            page.goto(work_items_url, wait_until="networkidle")
            
            current_page = 1
            while True:
                logging.info(f"Scraping halaman {current_page}...")
                page.wait_for_selector("table.table")
                rows = page.query_selector_all("table.table tbody tr")

                for row in rows:
                    cols = row.query_selector_all("td")
                    if len(cols) >= 6:
                        status = cols[4].inner_text().strip()

                        if status.lower() == "open":
                            item_data = {
                                "WIID": cols[1].inner_text().strip(),
                                "Description": cols[2].inner_text().strip(),
                                "Type": cols[3].inner_text().strip(),
                                "Status": status,
                                "Date": cols[5].inner_text().strip(),
                                "Source": "Playwright_Python_Scraper"
                            }
                            scraped_data.append(item_data)

                # Robust Pagination Handler untuk ACME System 1
                # Mencari tombol Next berupa link '>' atau '>>'
                next_button = (
                    page.query_selector("a.page-numbers:has-text('>')") or 
                    page.query_selector("a:has-text('>')") or 
                    page.query_selector("ul.pagination li:last-child a")
                )

                if next_button:
                    # Evaluasi apakah tombol Next/parent 'li' memiliki class 'disabled'
                    is_disabled = page.evaluate(
                        "(el) => el.classList.contains('disabled') || (el.parentElement && el.parentElement.classList.contains('disabled'))", 
                        next_button
                    )
                    
                    if is_disabled:
                        logging.info("Telah mencapai halaman terakhir.")
                        break
                    
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                    current_page += 1
                else:
                    logging.info("Tidak ditemukan tombol Next, scraping selesai.")
                    break

            logging.info(f"Scraping Selesai! Total item 'Open' dari seluruh halaman: {len(scraped_data)}")

            # 3. Data Export Stage
            json_output_string = json.dumps(scraped_data, indent=4)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_output_string)
            
            logging.info(f"Data berhasil diekspor ke {output_file}")
            return json_output_string

        except Exception as e:
            logging.error(f"Execution Error pada Playwright Engine: {str(e)}")
            raise e
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        run_playwright_scraper(ACME_EMAIL, ACME_PASSWORD, OUTPUT_JSON_FILE)
        sys.exit(0)
    except Exception:
        sys.exit(1)