import mwclient
import time
import logging
import re
import os  # For environment variables

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connect to Simple English Wikipedia
site = mwclient.Site("simple.wikipedia.org")

USERNAME = os.getenv("WIKI_USERNAME")
PASSWORD = os.getenv("WIKI_PASSWORD")

try:
    site.login(USERNAME, PASSWORD)
    logging.info("CactusIsMeBot logged in successfully.")
except mwclient.LoginError as e:
    logging.error(f"Login failed: {e}")
    exit(1)

def remove_redlinked_templates(page):
    """Remove red-linked templates from the given page."""
    try:
        # Retrieve the page text
        page_text = page.text()

        # Regular expression to find red-linked templates (e.g., {{TemplateName}})
        templates = re.findall(r"{{([^}|]+?)(?:\|[^}]*?)?}}", page_text)
        cleaned_text = page_text

        for template in templates:
            if not site.pages[f"Template:{template}"].exists:
                # Remove the red-linked template
                logging.info(f"Removing red-linked template: {template}")
                cleaned_text = re.sub(rf"{{{{{template}.*?}}}}", "", cleaned_text)

        # Save the changes if the text was modified
        if cleaned_text != page_text:
            page.edit(cleaned_text, summary="Removing red-linked templates")
            logging.info(f"Updated page: {page.name}")
        else:
            logging.info(f"No red-linked templates found on page: {page.name}")

    except Exception as e:
        logging.error(f"Error processing page {page.name}: {e}")

def process_all_pages():
    """Process all pages in Simple Wikipedia to remove red-linked templates."""
    try:
        for page in site.allpages(namespace=0):  # Namespace 0 is for main article pages
            logging.info(f"Processing page: {page.name}")
            remove_redlinked_templates(page)
    except Exception as e:
        logging.error(f"Error processing pages: {e}")

# Run the bot periodically
while True:
    process_all_pages()
    time.sleep(3600)  # Run every hour
