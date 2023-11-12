from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re

visited_links = set()

def check_url(url):
    regex = re.compile(r'^(https?|ftp):\/\/'  # http:// or https:// or ftp://
                       r'([a-zA-Z0-9]+([a-zA-Z0-9-]*[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}'  # domain
                       r'(:[0-9]+)?'  # optional port
                       r'(\/[^\s]*)?$')  # optional path

    if re.search(regex, url):
        return url
    else:
        return False

def get_links_recursive(url, depth=3):
    global visited_links

    url = check_url(url)
    if not url or url in visited_links or depth == 0:
        return set()

    visited_links.add(url)

    try:
        with requests.get(url, timeout=5) as response:
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            base_url = response.url
            links = {urljoin(url, a['href']) for a in soup.find_all('a', href=True) if urljoin(url, a['href']).startswith(main_site_url)}
            internal_links = set(links)

            for link in links:
                internal_links.update(get_links_recursive(link, depth - 1))

            return internal_links

    except requests.exceptions.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return set()

def links_with_query(links):

    links= get_links_recursive(links)
    golden_links=[]
    for link in links:
        if '?' and '=' in link:
            golden_links.append(link)
    
    return golden_links

main_site_url = "http://testphp.vulnweb.com"

for link in links_with_query(main_site_url):
    print(link)
