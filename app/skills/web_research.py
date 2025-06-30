from app.tools import web_scraper

def skill_extract_text_from_url(url: str) -> str | None:
    """
    Fetches HTML from a URL and extracts readable text content.
    Returns the text content, or None if an error occurs.
    """
    print(f"  [Skill] Attempting to extract text from URL: {url}")
    html_content = web_scraper.fetch_html(url)
    if html_content:
        text_content = web_scraper.parse_html_to_text(html_content)
        print(f"  [Skill] Successfully extracted text from {url}")
        return text_content
    else:
        print(f"  [Skill] Failed to fetch or parse HTML from {url}")
        return None

def skill_perform_basic_search(query: str, num_results: int = 3) -> list[dict]:
    """
    Performs a basic web search using the web_scraper's search_google function.
    Returns a list of search results (title, link).
    """
    print(f"  [Skill] Performing basic web search for: '{query}' (max {num_results} results)")
    results = web_scraper.search_google(query, num_results=num_results)
    if results:
        print(f"  [Skill] Search returned {len(results)} results.")
    else:
        print("  [Skill] Search returned no results or failed.")
    return results

if __name__ == '__main__':
    print("--- Testing Web Research Skills ---")

    test_url_valid = "http://example.com"
    print(f"\nTesting skill_extract_text_from_url with valid URL: {test_url_valid}")
    text = skill_extract_text_from_url(test_url_valid)
    if text:
        print("Extracted Text (first 200 chars):")
        print(text[:200] + "..." if len(text) > 200 else text)
    else:
        print("Failed to extract text.")

    test_url_invalid = "http://thissitedoesnotexist123abc.com"
    print(f"\nTesting skill_extract_text_from_url with invalid URL: {test_url_invalid}")
    text_invalid = skill_extract_text_from_url(test_url_invalid)
    if text_invalid is None:
        print("Correctly failed to extract text from invalid URL.")
    else:
        print(f"Unexpectedly got text from invalid URL: {text_invalid}")


    print("\nTesting skill_perform_basic_search:")
    search_query = "benefits of Python programming"
    search_results = skill_perform_basic_search(search_query, num_results=2)
    if search_results:
        print(f"Search results for '{search_query}':")
        for i, res in enumerate(search_results):
            print(f"  {i+1}. Title: {res['title']}")
            print(f"     Link: {res['link']}")
    else:
        print(f"No search results for '{search_query}' or search failed.")

    print("\n--- Web Research Skills Test Complete ---")
