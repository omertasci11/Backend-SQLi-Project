from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import re
import os

tree = ET.parse('errors.xml')
root = tree.getroot()

def get_all_error_patterns():
    all_error_patterns = []

    for dbms_element in root.findall(".//dbms"):
        dbms_name = dbms_element.get("value")
        error_patterns = [error.get('regexp') for error in dbms_element.findall('error')]
        all_error_patterns.append((dbms_name, error_patterns))

    return all_error_patterns


def scanner(url):

    parsed_url = urlparse(url)

    query_params = parse_qs(parsed_url.query)

    errors = []

    all_error_patterns = get_all_error_patterns()

    if query_params:
        last_param_key = list(query_params.keys())[-1]

        query_params[last_param_key] = ["'"]
        
        updated_query = urlencode(query_params, doseq=True)

        new_url = urlunparse(parsed_url._replace(query=updated_query))

        response = requests.get(new_url)

        if response.status_code == 200:

            for _, error_patterns in all_error_patterns:
                for pattern in error_patterns:
                    matches = re.findall(pattern, response.text)
                    errors.extend(matches)

                return errors
        
        else:
            return print(f"Error: {response.status_code}")


print(scanner('http://testphp.vulnweb.com/artists.php?artist=%2A'))