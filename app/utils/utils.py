import hashlib
import os
import string
from urllib.parse import urlparse, urlunparse


def standardize_url(url: str) -> str:
    if not urlparse(url).scheme:
        url = 'http://' + url
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace('www.', '') if parsed_url.netloc.startswith('www.') else parsed_url.netloc
    path = parsed_url.path or '/'
    standardized_url = urlunparse((parsed_url.scheme, netloc, path, '', parsed_url.query, ''))
    return standardized_url.rstrip('/')


def base62_encode(num: int) -> str:
    base62_chars = string.ascii_letters + string.digits
    if num == 0:
        return base62_chars[0]
    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(base62_chars[rem])
    return ''.join(reversed(base62))


def generate_short_key(url: str) -> str:
    return base62_encode(int(hashlib.sha256((url + os.urandom(16).hex()).encode()).hexdigest()[:12], 16))
