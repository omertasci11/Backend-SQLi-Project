from bs4 import BeautifulSoup
import requests
import sys
from urllib.parse import urljoin , urlparse
import re

def check_url(url):

    regex = re.compile(
        r'^(https?|ftp):\/\/'  # http:// or https:// or ftp://
        r'([a-zA-Z0-9]+([a-zA-Z0-9-]*[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}'  # domain
        r'(:[0-9]+)?'  # optional port
        r'(\/[^\s]*)?$'  # optional path
    )

    if not url[-1] == '/':

       url= url+'/'


    if re.search(regex, url):

        return url

    else:
        
        return False

def get_links_recursive(url, depth=3):

    url= check_url(url)
    visited_links = set()
    if depth == 0:
        return set()

    if url in visited_links:
        return set()

    visited_links.add(url)

   
    response = requests.get(url, timeout=5)
    

    soup = BeautifulSoup(response.text, 'html.parser')
    links = {urljoin(url, a['href']) for a in soup.find_all('a', href=True) if urljoin(url, a['href']).startswith(main_site_url)}

    internal_links = set(links)
    for link in links:
        
        internal_links.update(get_links_recursive(link, depth - 1))
        #print(internal_links)

    return internal_links

def links_with_query(links):

    links= get_links_recursive(links)
    golden_links=[]
    for link in links:
        if '?' and '=' in link:
            golden_links.append(link)
    
    return golden_links

main_site_url= "http://testphp.vulnweb.com/categories.php"

for links in links_with_query(main_site_url):
    print(links)


#git için bir yorum satırı ekledım bu main branch