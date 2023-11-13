from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

def scanner(url):

    parsed_url = urlparse(url)

    query_params = parse_qs(parsed_url.query)

    if query_params:
        last_param_key = list(query_params.keys())[-1]

        query_params[last_param_key] = ["*"]
        
        updated_query = urlencode(query_params, doseq=True)

        new_url = urlunparse(parsed_url._replace(query=updated_query))



    return new_url

print(scanner('https://www.prepostseo.com/guest-posting-sites?page=2'))