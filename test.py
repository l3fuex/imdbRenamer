from urllib import request
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
import sys


def imdb_search(title):
    params = {"q": title}
    url = f"https://www.imdb.com/find/?{urlencode(params)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    req = request.Request(url, headers=headers)

    with request.urlopen(req) as response:
        body = response.read()

    soup = BeautifulSoup(body.decode("utf-8"), "html.parser")

    # Extract all links from website
    links = [link.get("href") for link in soup.find_all("a")]

    # Look for result pattern and write matching links in a new list
    data = []
    pattern = r"\/title\/(tt[\d]+)\/\?ref_=(fn_all_ttl_[\d]+)"
    for link in links:
        tmp = {}
        result = re.match(pattern, link)
        if result:
            tmp["id"] = result.group(1)
            tmp["ref"] = result.group(2)
            data.append(tmp)

    if len(data) > 1:
        for index, element in enumerate(data[1:]):
            print(index)
            print(data)
            print("\n")
            if data[index]["ref"] == element["ref"]:
                data.pop(index)
                data.pop(index)
    print(data)
    sys.exit()

"""
    pattern = r"\/title\/(tt[\d]+)\/\?ref_=(fn_all_ttl_[\d]+)"
    n = 0
    while n < len(data)-1:
        result1 = re.match(pattern, data[n])
        result2 = re.match(pattern, data[n+1])
        # Delete link if pattern does not match
        if not result1:
            data.pop(n)
        # Delete both links if ref string is identical
        elif result1 and result2 and result1.group(2) == result2.group(2):
            data.pop(n)
            data.pop(n)
        else:
            data[n] = result1.group(1)
            n += 1

        print(n)

    return data
"""

def main():
    print(imdb_search("Special.Ops.Lioness"))


if __name__ == "__main__":
    main()
