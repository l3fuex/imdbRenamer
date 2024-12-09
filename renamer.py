import argparse
import re
import logging
import mimetypes
from pathlib import Path
from datetime import datetime
import omdb

logging.basicConfig(
#    level=logging.DEBUG, format="%(levelname)-8s %(funcName)s:%(lineno)d - %(message)s"
    level=logging.INFO, format="%(levelname)-8s %(message)s"
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "file",
    nargs="*",
    help="Path to file which should be renamed",
)
parser.add_argument(
    "-s",
    "--simulate",
    help="No renaming",
    action="store_true",
)
args = parser.parse_args()


def info_parser(file):
    directory = Path(file).parent

    # search for .nfo files and extract imdbid
    imdbid = None
    for element in directory.iterdir():
        if element.suffix == ".nfo":
            logging.debug("Parsing .nfo-File <%s>", element)
            with open(element, "rb") as f:
                content = f.read()

            pattern = r"(?:www.)?imdb.com/title/(tt\d*)"
            result = re.findall(pattern, str(content), flags=re.IGNORECASE)
            if result:
                imdbid = result[0]
                logging.debug("imdbID: %s", imdbid)
                break

    if imdbid is None:
        logging.debug("No imdbID found!")

    return imdbid


def year_parser(title):
    pattern = r"19[0-9]{2}|"
    currentyear = datetime.now().year

    # Build regex pattern to match a year from 2000 until the current year
    millennium = int(currentyear / 1000)
    century = int((currentyear / 100) % 10)
    if century > 0:
        pattern += rf"{millennium}[0-{century-1}][0-9]{{2}}|"
    decade = int((currentyear / 10) % 10)
    if decade > 0:
        pattern += rf"{millennium}{century}[0-{decade-1}][0-9]|"
    year = int(currentyear % 10)

    pattern += rf"{millennium}{century}{decade}[0-{year}]"
    results = re.findall(pattern, title)
    if results:
        releaseyear = results[len(results)-1]
        logging.debug("year: %s", results[len(results)-1])
    else:
        releaseyear = None
        logging.debug("No year found!")

    return releaseyear


def title_parser(file, year):
    path = Path(file).with_suffix("").resolve()
    chunks = list(path.parts)
    logging.debug("Full path: <%s>", path)

    # Calc informational value of path chunk
    for index, chunk in enumerate(chunks):
        words = re.split(r"[ _\.-]", chunk)
        count = 0
        count += 0.3 * len(words)

        infoval = index + count

        chunks[index] = (" ".join(words), infoval)
        logging.debug("Path chunk <%s> has an informational value of: %f", " ".join(words), infoval)

    # Sort list by informational value
    chunks = sorted(chunks, key=lambda x: x[1], reverse=True)
    title = chunks[0][0]
    logging.debug("Path chunk <%s> will be used for title parsing!", chunks[0][0])

    # Cut out specific strings
    cutstr = [ r"[\(\)\[\]]", "(720|1080|2160)p?", "director[´'`]?s cut", "[xh]26[4,5]", "bluray", "dubbed", "repack", "extended", "unrated", "uncut", "remastered", "dl", "a[av]c", "ac3[d]?", "dts", "dsnp", "amzn" ]
    regex = re.compile("|".join(cutstr), flags=re.IGNORECASE)
    title = regex.sub("", title)
    title = re.sub(" +", " ", title)
    logging.debug("Sanitized title string: <%s>", title)

    # In case the pattern S01E01 is found, return the leading string as the title
    pattern = r"[sS]\d{1,2}[eE]\d{1,2}"
    results = re.findall(pattern, title)
    if results:
        title = re.split(results[0], title)
        title = title[0].strip()

    # In case a release year is known, return the leading string as the title
    if year:
        results = re.findall(year, title)
        if results:
            title = re.split(results[len(results)-1], title)
            title = title[0].strip()

    logging.debug("title: %s", title)
    return title


def episode_parser(file):
    pattern = r".*[sS](\d{1,2})[eE](\d{1,2}).*"
    results = re.match(pattern, file)
    if results:
        season = results.group(1).zfill(2)
        episode = results.group(2).zfill(2)
        logging.debug("season: %s, episode: %s", season, episode)
    else:
        season = episode = None
        logging.debug("No season or episode found!")

    return season, episode


def omdb_search(title, category, year):
    matches = omdb.search_title(title, category, year)

    if len(matches) == 0:
        imdbid = None

    elif len(matches) == 1:
        imdbid = matches[0]["imdbID"]

    elif len(matches) > 1 and matches[0]["Title"] == title:
        imdbid = matches[0]["imdbID"]

    elif len(matches) > 1:
        for index, match in enumerate(matches):
            print(f"{index+1}: {match['Title']} {match['Year']}")
        while True:
            number = input(f"Please choose a number between 1 and {len(matches)}: ")
            if number.isdigit() and int(number) >= 1 and int(number) <= len(matches):
                imdbid = matches[int(number)-1]["imdbID"]
                break

    if imdbid is not None:
        logging.debug("imdbID: %s", imdbid)
    else:
        logging.debug("No match found")

    return imdbid


def main():
    prevtitle = prevseason = prevepisodes = metadata = None

    for index, file in enumerate(args.file):
        path = Path(file)
        episodes = None

        logging.info("Start processing file: <%s>", path.name)

        # Check for valid file argument
        if not Path(file).is_file():
            logging.critical("<%s> is not a valid file!", file)
            continue

        # Check if given file is a video
        mimetype = mimetypes.guess_type(file)
        if "video" not in mimetype[0]:
            logging.critical("<%s> is not a video file!", file)
            continue

        # Parse information
        imdbid = info_parser(file)
        year = year_parser(file)
        title = title_parser(file, year)
        season, episode = episode_parser(file)

        if season is not None:
            category = "series"
        else:
            category = "movie"

        # Batch mode
        if index > 0 and title == prevtitle and season is not None and season == prevseason:
            logging.debug("Batch mode")
            metadata = prevmetadata
            episodes = prevepisodes
        # Normal mode
        else:
            logging.debug("Normal mode")
            if imdbid is None:
                logging.debug("Search for title and retrieve imdbID")
                imdbid = omdb_search(title, category, year)
            if imdbid is None:
                logging.error("Renaming aborted! No search results found for given pattern <%s>", title)
                continue
            logging.debug("Get metadata for specified imdbID")
            metadata = omdb.get_title(imdbid)
            if category == "series":
                logging.debug("Get episodes for specified season")
                episodes = omdb.get_episodes(imdbid, season)

        # Save parsed information for possible batch run
        prevtitle = title
        prevseason = season
        prevmetadata = metadata
        prevepisodes = episodes

        # Build series name
        if category == "series":
            if "Placeholder" not in episodes[int(episode)-1]:
                name = f"{metadata['Title']} - S{season}E{episode} - {episodes[int(episode)-1]['Title']}{path.suffix}"
            else:
                logging.error("Missing episode data! Renaming skipped for file <%s> ", path.name)
                continue

        # Build movie name
        if category == "movie":
            name = f"{metadata['Title']} ({metadata['Year']}){path.suffix}"

        # Sanitize name
        logging.debug("raw name: <%s>", name)
        name = re.sub(r"[\*\?<>\"|\\/]", "", name)
        name = re.sub(":", "\ua789", name)
        logging.debug("sanitized name: <%s>", name)

        # Rename file
        logging.info("Renameing <%s> to <%s>", path.name, name)
        if not args.simulate:
            path.rename(path.with_name(name))


if __name__ == "__main__":
    main()
