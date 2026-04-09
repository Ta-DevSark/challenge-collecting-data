--- get_property_links.py
import requests
import re
from bs4 import BeautifulSoup
import concurrent.futures
from functools import partial

def process_page(page, session):
    print('start: %d' %page)
    start_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page='
    url = f"{start_url}{page}&orderBy=relevance"
    req = session.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    urls = list()
    # Find all 'a' tags and extract the 'href' attribute
    for link in soup.find_all('a', class_='card__title-link'):
        href = link.get('href')
        if href:
            urls.append(href)

    print('end: %d' %page)
    return urls

def scrape_all_pages(num_pages):
    with requests.Session() as session:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            nested_urls = executor.map(partial(process_page, session=session), range(1, num_pages + 1))

    urls = list()
    for inner_urls in nested_urls:
        urls.extend(inner_urls)

    return urls

+++ get_property_links.py
"""
Property Links Scraper

This module scrapes property listing URLs from Immoweb.be search results pages.

Usage:
    python get_property_links.py [--num-pages N]
"""

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Optional
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def process_page(page: int, session: requests.Session) -> List[str]:
    """
    Scrape property URLs from a single search results page.

    Args:
        page: Page number to scrape
        session: Requests session for connection pooling

    Returns:
        List of property URLs found on the page
    """
    logger.debug(f'Starting page: {page}')

    base_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page='
    url = f"{base_url}{page}&orderBy=relevance"

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        urls = []
        # Find all property card title links
        for link in soup.find_all('a', class_='card__title-link'):
            href = link.get('href')
            if href:
                urls.append(href)

        logger.debug(f'Completed page: {page} - Found {len(urls)} URLs')
        return urls

    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping page {page}: {str(e)}")
        return []


def scrape_all_pages(num_pages: int = 300, max_workers: int = 5) -> List[str]:
    """
    Scrape property URLs from multiple search results pages.

    Args:
        num_pages: Number of pages to scrape
        max_workers: Maximum concurrent threads

    Returns:
        List of all property URLs found
    """
    logger.info(f"Starting URL scraper for {num_pages} pages")

    with requests.Session() as session:
        # Set user agent to avoid blocking
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map pages to worker threads
            nested_urls = executor.map(
                partial(process_page, session=session),
                range(1, num_pages + 1)
            )

    # Flatten the list of lists
    urls = []
    for inner_urls in nested_urls:
        urls.extend(inner_urls)

    logger.info(f"Found {len(urls)} total property URLs from {num_pages} pages")
    return urls


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Scrape property URLs from Immoweb.be'
    )
    parser.add_argument(
        '--num-pages', '-n',
        type=int,
        default=300,
        help='Number of pages to scrape (default: 300)'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=5,
        help='Maximum concurrent workers (default: 5)'
    )

    args = parser.parse_args()

    try:
        urls = scrape_all_pages(
            num_pages=args.num_pages,
            max_workers=args.workers
        )
        print(f"\n✓ Successfully scraped {len(urls)} URLs")

        # Optionally save to file
        if urls:
            output_file = 'property_urls.txt'
            with open(output_file, 'w') as f:
                for url in urls:
                    f.write(url + '\n')
            print(f"  URLs saved to: {output_file}")

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        sys.exit(1)
