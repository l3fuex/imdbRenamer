# IMDb-Renamer
The purpose of this program is to rename movie and TV show files based on metadata retrieved from the OMDb API, making it ideal for organizing a media library.

It does so by looking for `.nfo` files in the same directory as the video file. These files often include a link to the IMDb website, which, in turn, contains the IMDb ID. The info parser attempts to extract this IMDb ID to use it as the source of truth for further processing.
If no IMDb ID can be extracted, the program uses the file path as the source of truth and analyzes it to derive details such as the title, release year, and, if applicable, the episode and season number. This information is then used to search for the corresponding IMDb ID.

Once an IMDb ID is determined, metadata is retrieved from the OMDb API, and the video file is renamed accordingly.
To minimize API calls when renaming an entire season, the software operates in batch mode. This means that only one API call is triggered, retrieving all the information about that season in a single response. The response is cached and used to rename the remaining episodes during the current program run.

## Prerequisites
- Python >= 3.6
- [OMDb API Key](https://www.omdbapi.com/apikey.aspx)

## Installation
```bash
# Copy the code to your machine
git clone https://github.com/l3fuex/imdbRenamer

# Add OMDb API key to the configuration file
mv imdbRenamer/config.ini.example imdbRenamer/config.ini && chmod 600 imdbRenamer/config.ini
vi imdbRenamer/config.ini

# Make the script executable
chmod +x imdbRenamer/*.py
```

## Usage
```bash
python3 imdbRenamer.py /path/to/movie.mkv
python3 imdbRenamer.py -s /path/to/movie_a.mkv /path/to/movie_b.mkv /path/to/movie_x.mkv
```

## License
This software is provided under the [Creative Commons BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license.

## Acknowledgments
- [OMDb API](https://www.omdbapi.com/) for metadata retrieval.