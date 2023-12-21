import requests
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class Scraper:
    def __init__(self, headers: dict | None = None):
        if headers:
            self.headers = headers
        else:
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "DNT": "1",
            }

    def scrape_page(self, url: str):
        res = self._request("GET", url)
        soup = BeautifulSoup(res.content, "html.parser")

        data = {
            "tld": self._get_tld(url),
            "title": self._get_title(soup),
            "description": self._get_description(soup),
            "image_url": self._get_image_url(soup),
            "favicon_url": self._get_favicon_url(url, soup),
            "site_name": self._get_site_name(soup),
        }
        return data

    def _request(self, method: str, url: str, data: dict | None = None):
        res = requests.request(method=method, url=url, headers=self.headers, data=data)
        res.raise_for_status()
        return res

    def _get_tld(self, url: str):
        return tldextract.extract(url).registered_domain

    def _get_title(self, soup: BeautifulSoup):
        title = soup.find("meta", property="og:title")
        if title:
            title = title.get("content")
        return title

    def _get_description(self, soup: BeautifulSoup):
        description = soup.find("meta", property="og:description")
        if description:
            description = description.get("content")
        return description

    def _get_image_url(self, soup: BeautifulSoup):
        image_url = soup.find("meta", property="og:image")
        if image_url:
            image_url = image_url.get("content")
        return image_url

    def _get_favicon_url(self, url, soup: BeautifulSoup):
        icon_link = soup.find("link", rel="shortcut icon")
        if icon_link is None:
            icon_link = soup.find("link", rel="icon")

        if icon_link:
            favicon_url = urljoin(url, icon_link["href"])
        else:
            favicon_url = urljoin(url, "/favicon.ico")

        return favicon_url

    def _get_site_name(self, soup: BeautifulSoup):
        site_name_tag = soup.find("meta", property="og:site_name")
        if site_name_tag:
            return site_name_tag["content"]
        return None
