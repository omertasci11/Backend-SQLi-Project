from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin , urlparse, parse_qs , urlencode, urlunparse
import re
import xml.etree.ElementTree as ET

visited_links = set()
tree = ET.parse('errors.xml')
root = tree.getroot()

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
    
    session = requests.Session()

    url = check_url(url)
    if not url or url in visited_links or depth == 0:
        return set()

    visited_links.add(url)

    try:
        with session.get(url, timeout=5) as response:
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


def get_all_error_patterns():
    all_error_patterns = []

    for dbms_element in root.findall(".//dbms"):
        dbms_name = dbms_element.get("value")
        error_patterns = [error.get('regexp') for error in dbms_element.findall('error')]
        all_error_patterns.append((dbms_name, error_patterns))

    return all_error_patterns



def manipulate_urls(url):

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

            url_with_payload = list(set(url_with_payload))
          
        else:
           print(url)

    return url_with_payload



def scanner(url):
    
    urls = manipulate_urls(main_site_url)

    errors = []

    scanned_results = []

    all_error_patterns = get_all_error_patterns()

    for url in urls:
        response = requests.get(url)

        if response.status_code == 200:

            for dbms_name, patterns in all_error_patterns:
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        errors.extend(matches)
                        scanned_results.append((url, dbms_name, matches))


            
    return scanned_results

     


main_site_url = "http://testphp.vulnweb.com/"


for i in scanner(main_site_url):
    print(i)
    
