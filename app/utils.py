import hashlib


def hash_url(url: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(url.encode("utf-8"))
    hash_value = sha256.hexdigest()
    return hash_value


def get_favicon_url(tld: str) -> str:
    return f"https://www.google.com/s2/favicons?domain={tld}"