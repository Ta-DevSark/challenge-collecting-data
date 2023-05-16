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
