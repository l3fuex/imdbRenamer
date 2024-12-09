import logging
import configparser
import json
from pathlib import Path
from urllib import request
from urllib.parse import urlencode

config = configparser.ConfigParser()
config.read(Path(__file__).resolve().parent / "config.ini")
APIKEY = config.get("OMDb", "apikey")

BASEURL = "http://www.omdbapi.com/"


def get_title(imdbid):
    params = { "i": imdbid }
    url = build_url(params)
    response = api_call(url)

    if response["Response"] == "True":
        response.pop("Response")
        return response
    else:
        logging.error("API response: %s", response["Error"])

    return None


def get_episodes(imdbid, season):
    def insert_placeholder():
        placeholder = {"Placeholder": "No Data"}
        for index, data in enumerate(response["Episodes"]):
            if index < int(data["Episode"])-1:
                response["Episodes"].insert(index, placeholder)

    params = { "i": imdbid, "Season": season }
    url = build_url(params)
    response = api_call(url)

    if response["Response"] == "True":
        # Insert placeholder in case an episode is missing
        insert_placeholder()
        return response["Episodes"]
    else:
        logging.error("API response: %s", response["Error"])

    return []


def search_title(title, category, year):
    params = { "s": title, "type": category, "y": year }
    url = build_url(params)
    response = api_call(url)

    if response["Response"] == "True":
        return response["Search"]
    else:
        logging.error("API response: %s", response["Error"])

    return []


def build_url(params):
    params["apikey"] = APIKEY

    for key in list(params.keys()):
        if params[key] is None:
            params.pop(key)

    return f"{BASEURL}?{urlencode(params)}"


def api_call(url):
    logging.debug("Sending API call: %s", url)

    with request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    return data
