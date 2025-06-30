from app.tools import web_scraper

def skill_extract_text_from_url(url: str, use_dynamic_fetch: bool = False) -> str | None:
    """
    Fetches HTML from a URL and extracts readable text content.
    Returns the text content, or None if an error occurs.
    Setting use_dynamic_fetch=True will use Botasaurus.
    """
    print(f"  [Skill] Attempting to extract text from URL: {url} (Dynamic: {use_dynamic_fetch})")
    html_content = None
    if use_dynamic_fetch:
        html_content = web_scraper.fetch_html_dynamic(url)
    else:
        html_content = web_scraper.fetch_html(url)

    if html_content:
        text_content = web_scraper.parse_html_to_text(html_content)
        print(f"  [Skill] Successfully extracted text from {url}")
        return text_content
    else:
        print(f"  [Skill] Failed to fetch or parse HTML from {url} (Dynamic: {use_dynamic_fetch})")
        return None

def skill_perform_basic_search(query: str, num_results: int = 3) -> list[dict]:
    """
    Performs a basic web search using the web_scraper's static search_google function.
    Returns a list of search results (title, link).
    """
    print(f"  [Skill] Performing basic web search for: '{query}' (max {num_results} results)")
    results = web_scraper.search_google(query, num_results=num_results)
    if results:
        print(f"  [Skill] Search returned {len(results)} results.")
    else:
        print("  [Skill] Search returned no results or failed.")
    return results

def skill_perform_dynamic_search(query: str, num_results: int = 3) -> list[dict]:
    """
    Performs a web search using the web_scraper's EXPERIMENTAL search_google_dynamic function.
    Returns a list of search results (title, link).
    Requires Botasaurus setup and potentially xvfb-run.
    """
    print(f"  [Skill] Performing dynamic web search for: '{query}' (max {num_results} results)")
    results = web_scraper.search_google_dynamic(query, num_results=num_results)
    if results:
        print(f"  [Skill] Dynamic search returned {len(results)} results.")
    else:
        print("  [Skill] Dynamic search returned no results or failed.")
    return results


if __name__ == '__main__':
    print("--- Testing Web Research Skills ---")
    print("NOTE: For dynamic tests, run this with 'xvfb-run python app/skills/web_research.py'")

    # Test skill_extract_text_from_url (static)
    test_url_static = "http://example.com"
    print(f"\nTesting skill_extract_text_from_url (static) with: {test_url_static}")
    text_static = skill_extract_text_from_url(test_url_static, use_dynamic_fetch=False)
    if text_static:
        print(f"Static Extracted Text (first 100 chars): {text_static[:100]}...")
        assert "Example Domain" in text_static
    else:
        print("Failed to extract static text.")

    # Test skill_extract_text_from_url (dynamic)
    # Using a JS-heavy site for this test
    test_url_dynamic_js = "http://quotes.toscrape.com/js/"
    print(f"\nTesting skill_extract_text_from_url (dynamic) with: {test_url_dynamic_js}")
    text_dynamic = skill_extract_text_from_url(test_url_dynamic_js, use_dynamic_fetch=True)
    if text_dynamic:
        print(f"Dynamic Extracted Text (first 100 chars): {text_dynamic[:100]}...")
        # Check for JS-loaded content
        if '<span>by <small class="author">' in text_dynamic:
             print("  SUCCESS: JS-loaded content indicators found in dynamic extract.")
        else:
             print("  ERROR: JS-loaded content indicators NOT found in dynamic extract.")
    else:
        print(f"Failed to extract dynamic text from {test_url_dynamic_js}.")

    test_url_invalid = "http://thissitedoesnotexist123abc.com"
    print(f"\nTesting skill_extract_text_from_url (static) with invalid URL: {test_url_invalid}")
    text_invalid_static = skill_extract_text_from_url(test_url_invalid, use_dynamic_fetch=False)
    if text_invalid_static is None:
        print("Correctly failed to extract static text from invalid URL.")
    else:
        print(f"Unexpectedly got static text from invalid URL: {text_invalid_static}")

    print(f"\nTesting skill_extract_text_from_url (dynamic) with invalid URL: {test_url_invalid}")
    text_invalid_dynamic = skill_extract_text_from_url(test_url_invalid, use_dynamic_fetch=True)
    if text_invalid_dynamic is None:
        print("Correctly failed to extract dynamic text from invalid URL.")
    else:
        print(f"Unexpectedly got dynamic text from invalid URL: {text_invalid_dynamic}")


    # Test skill_perform_basic_search (static)
    print("\nTesting skill_perform_basic_search (static):")
    search_query_static = "benefits of Python programming"
    search_results_static = skill_perform_basic_search(search_query_static, num_results=1)
    if search_results_static:
        print(f"Static search results for '{search_query_static}':")
        for res in search_results_static: print(f"  - {res['title']}: {res['link']}")
    else:
        print(f"No static search results for '{search_query_static}' or search failed.")

    # Test skill_perform_dynamic_search
    print("\nTesting skill_perform_dynamic_search (EXPERIMENTAL):")
    search_query_dynamic = "latest advancements in AI"
    search_results_dynamic = skill_perform_dynamic_search(search_query_dynamic, num_results=1)
    if search_results_dynamic:
        print(f"Dynamic search results for '{search_query_dynamic}':")
        for res in search_results_dynamic: print(f"  - {res['title']}: {res['link']}")
    else:
        print(f"No dynamic search results for '{search_query_dynamic}' or search failed.")

    print("\n--- Web Research Skills Test Complete ---")
