
# csrf.py

from html.parser import HTMLParser
from urllib import request as urllib_request
from urllib import error as urllib_error
from http import cookiejar

class CSRFTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.csrf_token = None


    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            for attr, value in attrs:
                if attr == 'name' and value == 'csrftoken':
                    self.csrf_token = attrs['value']

def fetch_csrf_token(html_content):
    parser = CSRFTokenParser()
    parser.feed(html_content)
    return parser.csrf_token

def check_csrf_vulnerability(csrf_url):
    try:
        # Create a cookie jar to handle cookies
        cookie_jar = cookiejar.CookieJar()
        cookie_processor = urllib_request.HTTPCookieProcessor(cookie_jar)
        opener = urllib_request.build_opener(cookie_processor)
        
        # Perform GET request to fetch CSRF token
        response = opener.open(csrf_url)
        html_content = response.read().decode('utf-8')
        
        # Fetch CSRF token from HTML content
        csrf_token = fetch_csrf_token(html_content)
        
        # Check if CSRF token exists
        if csrf_token:
            return {'status': 'vulnerable', 'message': 'CSRF token found. This website might be vulnerable to CSRF.'}
        else:
            return {'status': 'not_vulnerable', 'message': 'No CSRF token found. This website is likely not vulnerable to CSRF.'}
    
    except urllib_error.URLError as e:
        return {'status': 'error', 'message': f'Error occurred: {e.reason}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Error occurred: {e}'}