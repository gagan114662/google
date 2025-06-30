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

if __name__ == '__main__':
    # Test functions
    print("--- Testing Web Scraper ---")

    # Test fetch_html and parse_html_to_text
    # Using a known simple site for testing, like example.com
    test_url = "http://example.com" # More reliable for simple tests
    print(f"\nTesting fetch_html and parse_html_to_text with {test_url}:")
    html = fetch_html(test_url)
    if html:
        # print("\nRaw HTML:")
        # print(html[:500] + "...") # Print first 500 chars
        text_content = parse_html_to_text(html)
        print("\nParsed Text Content:")
        print(text_content)
    else:
        print(f"Failed to fetch {test_url}")

    # Test search_google
    print("\nTesting search_google (simulated/basic parsing):")
    search_results = search_google("Python programming language", num_results=3)
    if search_results:
        for i, res in enumerate(search_results):
            print(f"Result {i+1}:")
            print(f"  Title: {res['title']}")
            print(f"  Link: {res['link']}")
    else:
        print("No search results found or error in search.")

    print("\n--- Web Scraper Test Complete ---")
