from bs4 import BeautifulSoup
import requests
import sys
from urllib.parse import urljoin , urlparse
import re

s = requests.session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

def check_url(url_for_check):
    
    # Regex to check valid URL 
    regex = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
     # Compile the ReGex
    p = re.compile(regex)
    # If the string is empty 
    # return false
    if (url_for_check == None):
        return False
 
    # Return if the string 
    # matched the ReGex
    if(re.search(p, url_for_check)) and url_for_check[-1] == '/':

        url_for_check = url_for_check.rstrip(url_for_check[-1])
        return url_for_check
    
    elif re.search(p, url_for_check):
        return url_for_check
    
    else:
        return False

def get_links(url, max_redirects=5):
    url = check_url(url)
    given_url = urlparse(url)

    soup = BeautifulSoup(s.get(url).content, "html.parser")
    urls = []

    if max_redirects == 0:
        return urls

    for links in soup.find_all('a'):
        parts = urlparse(links.get('href'))

        if parts.netloc == given_url.netloc:
            urls.append(links.get('href'))
        elif parts.scheme == '' and parts.netloc == '' and parts.fragment == '' and parts.path.startswith('/'):
            urls.append(urljoin(url, parts.path))
        elif parts.scheme == '' and parts.netloc == '' and parts.fragment == '' and not parts.path.startswith('/'):
            urls.append(urljoin(url, '/' + parts.path))

    return urls

def get_forms(url, max_redirects=5):
    forms = []

    if max_redirects == 0:
        return forms

    for i in get_links(url, max_redirects=max_redirects - 1):
        soup_for_forms = BeautifulSoup(s.get(i).content, "html.parser")
        forms.append(soup_for_forms.find_all("form"))

    res = [i for n, i in enumerate(forms) if i not in forms[:n]]

    return res

def get_form_details(forms, url):
    form_details = []
    for form in forms:
        details = {}
        action = form.attrs.get("action")
        if action:
            action = urljoin(url, action)
        else:
            action = url

        method = form.attrs.get("method", "get").lower()

        inputs = []
        for input_tag in form.find_all("input"):
            input_type = input_tag.attrs.get("type", "text")
            input_name = input_tag.attrs.get("name")
            input_value = input_tag.attrs.get("value", "")
            inputs.append({"type": input_type, "name": input_name, "value": input_value})

        details["action"] = action
        details["method"] = method
        details["inputs"] = inputs

        form_details.append(details)

    return form_details

# Verilen Url Adresinin geröek bir siteye ait olup olmadıgını kontrol etmem gerekıyor mu? Belki ping atıp server up mı down mı görebilirim. Bunu yapmam lazım mı ???
#url='https://juice-shop.herokuapp.com/#/'
url='https://tascisec.com/'
#url='http://testphp.vulnweb.com/'
#url='https://cnn.com'


print('*****' , check_url(url), '*****')
if check_url(url) == False:
    print('URL is not Valid !!')

else:
    links = get_links(url)

    for link in links:
        forms = get_forms(link)

        for form in forms:
            form_details = get_form_details(form, link)
            print(form_details)




    

# *****Yarın Yapılacaklar*****

# Sitenin içerisindeki url leri bulma işini bir fonksiyon haline getir o zaman daha düzenli bir kodun olur +++++++++++++++
# URL leri bulma işini yaptık ama bıraz daha araştır bakalım tam olmuş gibi hissetmiyorum. ++++++++++++++++ (Ama sub domainlere bakmıyor eklemek isterrsen sonra bak)
# Formları alıyoruz aynı olanları cıkartıyoruz ama 'value' değişkeni işi bozabiliyor +++++++++++++++
# Formları alıyoruz simdi bu formların input alanlarını bulmak ve kontrol etmek lazım youtube videsundan bakmak lazım nasıl yapıldıgına +++++++++++++++++++++++++++++++
# Sadece verilen url de tarama yapmak için bir lite scan metodu yaz
# Hız konusunda ciddi endişelerim var programı hızlandırmamız lazım 
# verilen linklerin ne döndüğünü kontrol etmek isteyebilirsin ex: 200,302,404 
# Payload dosyalarını hazıla
# Veri tabanlarının error listesini bulmak lazım 