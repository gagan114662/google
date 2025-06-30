import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def fetch_html(url: str, timeout: int = 10) -> str | None:
    """
    Fetches HTML content from a given URL.
    Returns the HTML content as a string, or None if an error occurs.
    """
    print(f"  [WebScraper] Fetching HTML from: {url}")
    try:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"  [WebScraper] Error fetching URL {url}: {e}")
        return None

def parse_html_to_text(html_content: str) -> str:
    """
    Parses HTML content and extracts readable text.
    """
    if not html_content:
        return ""
    print("  [WebScraper] Parsing HTML to text...")
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    print("  [WebScraper] HTML parsing complete.")
    return text

def search_google(query: str, num_results: int = 5) -> list[dict]:
    """
    Simulates a Google search and extracts links and titles.
    NOTE: This is a very basic simulation. Real Google scraping is complex
    and often blocked. For robust search, a proper search API (like Google Custom Search API)
    or more advanced scraping techniques (e.g., using headless browsers that can handle JS
    and anti-bot measures) would be needed. This version is for local testing and
    demonstrates the intended functionality.
    """
    print(f"  [WebScraper] Performing Google search for: '{query}' (requesting {num_results} results - simulated)")

    # This is a simplified approach that directly constructs a search URL.
    # Google's actual search results page is dynamic and hard to parse reliably this way.
    # We will try to fetch the page but parsing might be fragile.

    search_url = f"https://www.google.com/search?{urlencode({'q': query, 'num': num_results})}"
    print(f"  [WebScraper] Search URL: {search_url}")

    html_content = fetch_html(search_url)
    if not html_content:
        print("  [WebScraper] Failed to fetch Google search results page.")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []

    # Google's structure changes. This is a common selector pattern but might break.
    # It looks for <a> tags within <h3> tags that are themselves within a div structure
    # often used for search results.
    # Example selectors that have worked at various times:
    # 'div.g a > h3', 'div.tF2Cxc a', 'a h3.LC20lb'
    # For a more reliable approach, one would inspect the current Google SERP structure.

    # Trying a relatively common pattern for organic results.
    # Google often wraps search results in divs with class 'g' or similar.
    # Inside these, there's usually an <a> tag whose href is the result link,
    # and an <h3> tag containing the title.

    # Attempt 1: Common structure (div class="g" -> a -> h3)
    # Note: Google often uses obfuscated or rapidly changing class names.
    # This is a best-effort for a simple scraper.

    # Let's try to find all <a> tags that have an <h3> child, as titles are often in <h3>
    # and the whole item is clickable (is an <a>).

    # A more modern approach might involve looking for specific data attributes if Google uses them.
    # For now, we'll try a few common CSS selectors.

    # Selectors to try (these are examples and might need adjustment):
    # 1. `div.g a[href^="http"] > h3` (traditional structure)
    # 2. `a[jsname][href^="http"] > h3` (some newer structures use jsname attributes)
    # 3. `div[data-sokoban-container] a[href^="http"] > h3` (another pattern seen)

    # Simpler: find all links, then filter ones that look like search results.
    # This is very naive.

    # Let's try finding divs that seem to contain search results.
    # Google often uses class names like 'g', 'Gx5Zad', ' υπάρχει', etc.
    # This is highly unreliable.

    # A more robust method for local testing without complex browser automation
    # would be to use a library that interfaces with a search engine API,
    # or a simpler search engine that's easier to scrape.
    # For this example, we'll stick to a very basic attempt on Google.

    # Example: find <a> tags with an href attribute that starts with /url?q= (Google's redirect)
    # and also have an <h3> child for the title.

    # Let's try a simpler approach: Find all <a> tags with <h3> inside.
    # This is very generic.

    # A common pattern for search result links is an `<a>` tag
    # with an `<h3>` tag inside it for the title.

    # We'll try to find `div` elements that seem to encapsulate a single search result.
    # Google's class names are volatile. `div.g` used to be common.
    # Let's try to find `<a>` tags with `<h3>` as direct children,
    # as these are often titles.

    # A simple approach that might work for some basic Google layouts:
    for link_tag in soup.find_all('a'):
        href = link_tag.get('href')
        h3_tag = link_tag.find('h3') # Check for an h3 inside the link

        if href and h3_tag:
            title = h3_tag.get_text(strip=True)
            # Filter out internal Google links and ensure it's an absolute URL
            if href.startswith("http") and "google.com" not in href:
                results.append({"title": title, "link": href})
            elif href.startswith("/url?q="): # Google redirect URL
                # Extract the actual URL from the query parameters
                from urllib.parse import parse_qs, urlparse
                parsed_href = urlparse(href)
                qs_params = parse_qs(parsed_href.query)
                if 'q' in qs_params and qs_params['q'][0].startswith("http"):
                    actual_link = qs_params['q'][0]
                    results.append({"title": title, "link": actual_link})

        if len(results) >= num_results:
            break

    if not results:
        print("  [WebScraper] Could not parse search results using the primary method. Trying generic link search.")
        # Fallback: very basic, just find links with some text if the above fails.
        # This is less accurate.
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            title = link_tag.get_text(strip=True)
            if href.startswith("http") and "google.com" not in href and title:
                 results.append({"title": title, "link": href})
            elif href.startswith("/url?q="):
                 from urllib.parse import parse_qs, urlparse
                 parsed_href = urlparse(href)
                 qs_params = parse_qs(parsed_href.query)
                 if 'q' in qs_params and qs_params['q'][0].startswith("http") and title:
                    actual_link = qs_params['q'][0]
                    results.append({"title": title, "link": actual_link})
            if len(results) >= num_results:
                break

    print(f"  [WebScraper] Found {len(results)} results (simulated/parsed).")
    return results[:num_results]


# --- Botasaurus Integration for Dynamic Scraping ---
from botasaurus.browser import browser, Driver as BotasaurusDriver
import os

# WORKSPACE_DIR should align with other tools and run_task.py
# However, Botasaurus's @browser decorator has its own 'output_folder' logic
# which defaults to "output/{function_name}".
# For screenshots, we'll explicitly save to our workspace.
WORKSPACE_DIR = "workspace"

# Note: Functions decorated with @browser create their own output folders
# (e.g., output/fetch_html_dynamic_task) for their results if not returning data
# to be handled by the caller. We will primarily use it to get page content.

# Wrapper function to be decorated by @browser, as Botasaurus expects
# the decorated function to handle the driver.
@browser(
    output=None, # We want to return data, not have Botasaurus save it directly based on function name
    # headless=True, # Botasaurus often handles this well by default, but can be explicit
    # block_images_and_css=True, # Good for speed if full rendering not needed for data
)
def _fetch_html_dynamic_task(driver: BotasaurusDriver, data: dict) -> str | None:
    url = data.get("url")
    timeout_seconds = data.get("timeout", 30) # Botasaurus driver.get uses milliseconds by default for some internal timeouts.
                                              # The page load timeout is handled by driver.get's own mechanisms.

    print(f"  [WebScraper-Dynamic] Navigating to: {url} with Botasaurus")
    try:
        # Botasaurus's driver.get handles navigation and waits for page load.
        # The timeout for driver.get itself is not a direct parameter like in requests.
        # It relies on underlying browser timeouts. We can add an overall task timeout if needed.
        driver.get(url)
        # driver.wait_for_page_load(timeout=timeout_seconds * 1000) # Example if explicit wait needed

        html_content = driver.page_html
        print(f"  [WebScraper-Dynamic] Successfully fetched dynamic HTML from {url}")
        return html_content
    except Exception as e:
        print(f"  [WebScraper-Dynamic] Error fetching dynamic HTML from {url}: {e}")
        return None

def fetch_html_dynamic(url: str, timeout: int = 30) -> str | None:
    """
    Fetches HTML content from a given URL after JavaScript execution using Botasaurus.
    Returns the HTML content as a string, or None if an error occurs.
    Timeout is a general guideline; actual page load timeout is managed by Botasaurus/browser.
    """
    print(f"  [WebScraper] Fetching dynamic HTML from: {url} (timeout hint: {timeout}s)")
    # Botasaurus decorated functions are called directly.
    # The 'data' parameter in the decorated function receives the arguments.
    return _fetch_html_dynamic_task(data={"url": url, "timeout": timeout})


@browser(output=None) # We manage output path ourselves
def _capture_screenshot_dynamic_task(driver: BotasaurusDriver, data: dict) -> bool:
    url = data.get("url")
    output_filename = data.get("output_filename")

    # Ensure output_filename is relative to WORKSPACE_DIR for consistency
    # and doesn't try to escape it.
    base_path = os.path.abspath(WORKSPACE_DIR)
    # Make output_filename safe by ensuring it's just a name, not a path traversal
    safe_filename_component = os.path.basename(output_filename)
    full_screenshot_path = os.path.join(base_path, safe_filename_component)

    # Create workspace if it doesn't exist (though run_task.py should do this)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)

    print(f"  [WebScraper-Dynamic] Navigating to: {url} for screenshot")
    try:
        driver.get(url)
        print(f"  [WebScraper-Dynamic] Saving screenshot to: {full_screenshot_path}")
        # Botasaurus driver has a save_screenshot method
        driver.save_screenshot(full_screenshot_path) # Default is full page
        print(f"  [WebScraper-Dynamic] Screenshot saved successfully to {full_screenshot_path}")
        return True
    except Exception as e:
        print(f"  [WebScraper-Dynamic] Error capturing screenshot from {url}: {e}")
        return False

def capture_screenshot_dynamic(url: str, output_filename: str) -> bool:
    """
    Captures a screenshot of a webpage after JavaScript execution using Botasaurus.
    Saves it to WORKSPACE_DIR/output_filename.
    Returns True if successful, False otherwise.
    """
    print(f"  [WebScraper] Capturing screenshot from: {url} to {output_filename}")
    return _capture_screenshot_dynamic_task(data={"url": url, "output_filename": output_filename})

# Note: The previous search_google using requests is kept for comparison or simple cases.
# This new one uses Botasaurus for dynamic content handling.
def search_google_dynamic(query: str, num_results: int = 5) -> list[dict]:
    """
    Performs a Google search using Botasaurus to fetch the page dynamically
    and then attempts to parse links and titles.
    NOTE: This is EXPERIMENTAL. Google's SERP structure is complex and frequently changes,
    and they employ strong anti-scraping measures. Success is not guaranteed and
    selectors may need frequent updates.
    """
    print(f"  [WebScraper-Dynamic] Performing dynamic Google search for: '{query}' (requesting {num_results} results)")

    search_url = f"https://www.google.com/search?{urlencode({'q': query, 'num': num_results * 2})}" # Fetch more in case some are ads/unparsable
    print(f"  [WebScraper-Dynamic] Search URL: {search_url}")

    # Use the dynamic fetcher
    # The _fetch_html_dynamic_task is already decorated with @browser
    # So we call the wrapper `fetch_html_dynamic`
    html_content = fetch_html_dynamic(search_url)

    if not html_content:
        print("  [WebScraper-Dynamic] Failed to fetch Google search results page dynamically.")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    results = []

    # Selectors for Google SERP elements are notoriously volatile.
    # Common patterns observed (these WILL change over time):
    # - Main result blocks: often `div` with classes like 'g', 'Gx5Zad', 'Ww4FFb', 'VwiC3b MUxGbd yDYNvb lyLwlc lEBKkf' etc.
    # - Link inside these blocks: `a` tag
    # - Title inside the `a` tag: often an `h3` tag with classes like 'LC20lb MBeuO DKV0Md'

    # Attempting a common, though fragile, selector pattern:
    # Find `divs` that seem to encapsulate a search result, then find `a > h3` within them.
    # This specific selector `div.g a[href] h3` is a simplified example.
    # A more robust approach would involve inspecting current SERP and using more specific classes.

    # Let's try to find hyperlink tags that have an H3 child, a common pattern.
    # We will look for `a` tags that have `h3` and a `href` starting with http or /url?q=
    count = 0
    for link_tag in soup.find_all('a', href=True):
        h3_tag = link_tag.find('h3')
        if not h3_tag:
            continue

        title = h3_tag.get_text(strip=True)
        href = link_tag['href']

        if not title: # Skip if title is empty
            continue

        actual_link = None
        if href.startswith("http") and "google.com" not in href:
            actual_link = href
        elif href.startswith("/url?q="):
            from urllib.parse import parse_qs, urlparse
            parsed_href = urlparse(href)
            qs_params = parse_qs(parsed_href.query)
            if 'q' in qs_params and qs_params['q'][0].startswith("http"):
                actual_link = qs_params['q'][0]

        if actual_link:
            # Basic deduplication based on link
            if not any(r['link'] == actual_link for r in results):
                 results.append({"title": title, "link": actual_link})
                 count += 1
                 if count >= num_results:
                    break

    if not results:
        print("  [WebScraper-Dynamic] Could not parse dynamic search results using primary method.")
        # Add more fallback parsing logic here if necessary, similar to the static search_google.

    print(f"  [WebScraper-Dynamic] Found {len(results)} dynamic search results.")
    return results[:num_results]


if __name__ == '__main__':
    # Test functions
    print("--- Testing Web Scraper ---")

    # Test fetch_html and parse_html_to_text (static)
    static_test_url = "http://example.com"
    print(f"\nTesting fetch_html and parse_html_to_text with {static_test_url}:")
    html_static = fetch_html(static_test_url)
    if html_static:
        text_content_static = parse_html_to_text(html_static)
        print("\nParsed Static Text Content:")
        print(text_content_static)
    else:
        print(f"Failed to fetch {static_test_url}")

    # Test search_google (static, simulated)
    print("\nTesting search_google (simulated/basic parsing):")
    search_results_static = search_google("Python programming language", num_results=2)
    if search_results_static:
        for i, res in enumerate(search_results_static):
            print(f"Static Search Result {i+1}: Title: {res['title']}, Link: {res['link']}")
    else:
        print("No static search results found or error in search.")

    print("\n--- Testing Dynamic Web Scraping (Botasaurus) ---")
    print("NOTE: If running this directly, ensure you use 'xvfb-run python app/tools/web_scraper.py'")

    # Setup workspace for dynamic tests if not present
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)
        print(f"Created {WORKSPACE_DIR} for dynamic tests.")

    # Test fetch_html_dynamic
    # Using a site known for JS content or a test site like toscrape.com
    # For simplicity, let's use example.com first to ensure Botasaurus itself works,
    # then a more JS-heavy site if available and simple.
    # http://quotes.toscrape.com/js/ is a good test site.
    dynamic_test_url_simple = "http://example.com"
    dynamic_test_url_js = "http://quotes.toscrape.com/js/" # This site uses JS to load quotes

    print(f"\nTesting fetch_html_dynamic with {dynamic_test_url_simple}:")
    html_dynamic_simple = fetch_html_dynamic(dynamic_test_url_simple)
    if html_dynamic_simple:
        print(f"Dynamic HTML (simple) fetched (first 300 chars): {html_dynamic_simple[:300]}...")
        # Simple check:
        if "Example Domain" in html_dynamic_simple:
            print("  SUCCESS: 'Example Domain' found in dynamic HTML.")
        else:
            print("  ERROR: 'Example Domain' NOT found in dynamic HTML.")

    else:
        print(f"Failed to fetch dynamic HTML from {dynamic_test_url_simple}")

    print(f"\nTesting fetch_html_dynamic with JS-reliant site: {dynamic_test_url_js}:")
    html_dynamic_js = fetch_html_dynamic(dynamic_test_url_js)
    if html_dynamic_js:
        print(f"Dynamic HTML (JS-site) fetched (first 300 chars): {html_dynamic_js[:300]}...")
        # Check for content known to be loaded by JS on that site
        # For quotes.toscrape.com/js, quotes are within <div class="quote"> elements.
        # A simple check could be looking for "<span>by <small class="author""
        if '<span>by <small class="author"' in html_dynamic_js:
             print("  SUCCESS: JS-loaded content indicators found.")
        else:
             print("  ERROR: JS-loaded content indicators NOT found. Scraping might not have waited for JS.")
    else:
        print(f"Failed to fetch dynamic HTML from {dynamic_test_url_js}")


    # Test capture_screenshot_dynamic
    screenshot_filename = "test_screenshot_example.png"
    print(f"\nTesting capture_screenshot_dynamic with {dynamic_test_url_simple}, output to {screenshot_filename}:")
    screenshot_success = capture_screenshot_dynamic(dynamic_test_url_simple, screenshot_filename)
    if screenshot_success:
        full_screenshot_path = os.path.join(WORKSPACE_DIR, screenshot_filename)
        if os.path.exists(full_screenshot_path):
            print(f"  SUCCESS: Screenshot saved to {full_screenshot_path}")
        else:
            print(f"  ERROR: Screenshot function returned success, but file not found at {full_screenshot_path}")
    else:
        print("  Failed to capture screenshot.")

    # Test search_google_dynamic
    print("\nTesting search_google_dynamic (EXPERIMENTAL):")
    dynamic_search_query = "web scraping with python botasaurus"
    dynamic_search_results = search_google_dynamic(dynamic_search_query, num_results=2)
    if dynamic_search_results:
        for i, res in enumerate(dynamic_search_results):
            print(f"Dynamic Search Result {i+1}: Title: {res['title']}, Link: {res['link']}")
    else:
        print(f"No dynamic search results for '{dynamic_search_query}' or search failed.")

    print("\n--- Web Scraper Test Complete ---")
