from secrets import token_hex

import requests
from bs4 import BeautifulSoup

Z_LIB = "https://b-ok.africa"
PDF_DRIVE = "https://www.pdfdrive.com/"


def scrape_zlib(query):
    response = []
    url = f"{Z_LIB}/s/{query}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="resItemBox resItemBoxBooks exactMatch")[:10]
    for result in results:
        _ = {
            "title": result.find("h3", {"itemprop": True}).contents[1].text.strip(),
            "authors": ", ".join(
                [_.text.strip() for _ in result.find_all("a", {"itemprop": True})]
            ),
            "size": result.find("div", class_="bookProperty property__file")
            .contents[-2]
            .text,
            "image": result.find("img", class_="cover lazy")["data-src"],
            "url": Z_LIB
            + result.find(
                "div", class_="checkBookDownloaded itemCoverWrapper"
            ).contents[1]["href"],
        }
        page = BeautifulSoup(requests.get(_.get("url")).content, "html.parser")
        download_link = {
            "dl_link": Z_LIB
            + page.find("a", class_="btn btn-primary dlButton addDownloadedBook")[
                "href"
            ]
        }
        _.update(download_link)
        response.append(_)

    return response