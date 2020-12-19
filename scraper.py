import requests
from bs4 import BeautifulSoup

Z_LIB = "https://b-ok.africa"
PDF_DRIVE = "https://www.pdfdrive.com"


def scrape_zlib(query):
    response = []
    url = f"{Z_LIB}/s/{query}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="resItemBox resItemBoxBooks exactMatch")
    for index, result in enumerate(results):
        _ = {
            "title": result.find("h3", {"itemprop": True}).contents[1].text.strip(),
            "authors": ", ".join(
                [_.text.strip() for _ in result.find_all("a", {"itemprop": True})]
            ),
            "size": result.find("div", class_="bookProperty property__file")
            .contents[-2]
            .text.strip(),
            "url": Z_LIB
            + result.find(
                "div", class_="checkBookDownloaded itemCoverWrapper"
            ).contents[1]["href"],
        }

        # image validation
        image = (
            result.find("img", class_="cover")
            .get("data-srcset")
            .split(", ")[-1]
            .split(" ")[0]
            .strip()
            if result.find("img", class_="cover").get("data-srcset")
            else result.find("img", class_="cover")
            .get("src")
            .split(", ")[-1]
            .split(" ")[0]
            .strip()
        )

        if image.startswith("https://"):
            _.update({"image": image})
        else:
            _.update({"image": Z_LIB + image})

        response.append(_)

    return response


