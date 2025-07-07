import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime

def get_cert_expiry(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    if not hostname:
        raise ValueError("Invalid URL: Could not extract hostname.")

    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            expiry_str = cert['notAfter']
            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
            return expiry_date
