from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin , urlparse, parse_qs , urlencode, urlunparse
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
        if '?' in link and '=' in link:
            golden_links.append(link)
    
    return golden_links



def scanner(url):

    golden_links = links_with_query(main_site_url)
    url_with_payload = []
    for url in golden_links:
    
        parsed_url = urlparse(url)
    
        query_params = parse_qs(parsed_url.query)
        
        if query_params:

            last_param_key = list(query_params.keys())[-1]

            query_params[last_param_key] = ["*"] * len(query_params[last_param_key])
        
            updated_query = urlencode(query_params, doseq=True)

            final_link = urlunparse(parsed_url._replace(query=updated_query))

            url_with_payload.append(final_link)

        else:
           print(url)

    return url_with_payload


main_site_url = "https://www.prepostseo.com/"

for link in scanner(main_site_url):
    
    print(link)



