from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlencode
import time
import ssl


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
}

def get_all_forms(url):
    response = urlopen(Request(url, headers=headers), context=ssl._create_unverified_context())
    soup = bs(response.read(), "html.parser")
    return soup.find_all("form")

def get_form_details(form):
    details = {}
    try:
        action = form.attrs.get("action").lower()
    except:
        action = None
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
    return details

def is_vulnerable(response):
    errors = {
        "you have an error in your sql syntax;",
        "warning: mysql",
        "unclosed quotation mark after the character string",
        "quoted string not properly terminated",
        "Hello Admin User "
    }
    for error in errors:
        if error in response.decode().lower():
            return True
    return False

def scan_sql_injection(url):
    response_list = []
    
    for c in "\"'":
        new_url = f"{url}{c}"
        response_list.append(f"[!] Trying {new_url}")
        try:
            response = urlopen(Request(new_url, headers=headers), context=ssl._create_unverified_context()).read()
        except:
            continue
        if is_vulnerable(response):
            response_list.append(f"[+] SQL Injection vulnerability detected, link: {new_url}")
            return "\n".join(response_list)

    forms = get_all_forms(url)
    response_list.append(f"[+] Detected {len(forms)} forms on {url}.")
    
    for form in forms:
        form_details = get_form_details(form)
        for c in "\"'":
            data = {}
            for input_tag in form_details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    try:
                        data[input_tag["name"]] = input_tag["value"] + c
                    except:
                        pass
                elif input_tag["type"] != "submit":
                    data[input_tag["name"]] = f"test{c}"
            
            action_url = urljoin(url, form_details["action"])
            try:
                if form_details["method"] == "post":
                    start_time = time.time()
                    response = urlopen(Request(action_url, headers=headers, data=urlencode(data).encode()), context=ssl._create_unverified_context())
                    end_time = time.time()
                elif form_details["method"] == "get":
                    start_time = time.time()
                    response = urlopen(Request(f"{action_url}?{urlencode(data)}", headers=headers), context=ssl._create_unverified_context())
                    end_time = time.time()
            except:
                continue
            
            if is_vulnerable(response) and end_time - start_time > 2:
                response_list.append(f"[+] SQL Injection vulnerability detected, link: {action_url}")
                response_list.append("[+] Form details:")
                response_list.append(str(form_details))
                break
                
    return "\n".join(response_list)