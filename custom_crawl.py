# import time
from urllib.parse import urljoin, urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from readability import Document


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ["http", "https"]


def get_links(base_url, soup):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a_tag["href"])
        if is_valid_url(full_url):
            links.add(full_url)
    return links


def extract_markdown(html, url):
    doc = Document(html)
    cleaned_html = doc.summary()
    title = doc.title()
    markdown = f"# {title}\n\n" + html2text.html2text(cleaned_html)
    markdown = f"<!-- URL: {url} -->\n\n" + markdown
    return markdown


def crawl(url, depth, visited):
    if depth == 0 or url in visited:
        return []

    print(f"Crawling: {url} (depth: {depth})")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    visited.add(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    markdown = extract_markdown(html, url)

    links = get_links(url, soup)
    result = [markdown]

    for link in links:
        result += crawl(link, depth - 1, visited)

    return result


def crawl_urls(url_list, max_depth=1):
    visited = set()
    all_markdown = []

    for url in url_list:
        if is_valid_url(url):
            all_markdown += crawl(url, max_depth, visited)

    return all_markdown
