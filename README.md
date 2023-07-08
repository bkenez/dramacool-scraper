# Web Scraper

This is a past excercise I have completed, moved to a public repo in order to demonstrate python skills.

### Setup

```
# Create virtual environment
python -m venv venv
# Activate Virtual Environment
source venv/bin/activate
# Install dependencies
python -m pip install requests beautifulsoup4
...
# Example run for 1996
python scrap.py 1996
...
# Exit from virtual Environment
deactivate
```

## NAME

scrap.py - Python web scraping program for extracting information from the Dramacool website

## SYNOPSIS

```
scrap.py [--year YEAR | --years YEAR_RANGE] [--newer DATE_TIME] [--country COUNTRY] [--genre GENRE]
         [--act ACTOR] [--noact] [--ep]
```

## DESCRIPTION

The `scrap.py` program is designed to scrape information from the Dramacool website, a platform for Asian dramas. It allows users to retrieve drama details based on various criteria such as release year, country, genre, and actors. By default, the program lists the most recent episodes in SUB (subtitled) and RAW (without subtitles) formats.

If the `--act` flag is used, the program changes its behavior and first scrapes the specified actor's page as the endpoint. This optimization allows for faster retrieval of results specific to the actor.

## OPTIONS

* `--year YEAR`, `--years YEAR_RANGE`

  Specifies a single year or a range of years for filtering the results. The `YEAR` argument should be in the format "YYYY," while the `YEAR_RANGE` argument should be in the format "YYYY-YYYY." The program will only display dramas that fall within the specified year(s).

* `--newer DATE_TIME`

  Filters the episodes by listing only those released after the specified `DATE_TIME`. The `DATE_TIME` argument should be in the format "YYYY-MM-DD HH:MM:SS."

* `--country COUNTRY`

  Filters the dramas based on the specified `COUNTRY`. Only dramas from the specified country will be listed.

* `--genre GENRE`

  Filters the dramas based on the specified `GENRE`. Only dramas of the specified genre will be listed.

* `--act ACTOR`

  Filters the dramas by listing only those that feature the specified `ACTOR`. Only dramas with the specified actor will be displayed. The program optimizes the scraping process by first scraping the actor's page as the endpoint to retrieve results faster.

* `--noact`

  By default, the program lists the actors associated with each drama. This flag can be used to suppress the actor listing, resulting in a more concise output.

* `--ep`

  By default, the program lists only the most recent SUB and RAW episodes. If this flag is present, all episodes, including older ones, will be listed.

## EXAMPLES

```
scrap.py --years 1996 --country Japanese --genre comedy
```

List all Japanese comedy dramas released in the year 1996:

```
Supermarket Woman - 1996 - Japanese - Comedy
  SUB Supermarket Woman Episode 1 2015-06-01 12:16:53
Free and Easy 8 - 1996 - Japanese - Comedy
  RAW Free and Easy 8 Episode 1 2016-06-02 14:49:46
Shota no Sushi - 1996 - Japanese - Comedy - Kashiwabara Takashi (1977), Sugimoto Tetta (1965), Imada Koji (1966), Kitahara Masaki (1940)
  SUB Shota no Sushi Episode 17 2014-12-03 14:18:09
Shall We Dance? - 1996 - Japanese - Comedy
  SUB Shall We Dance? Episode 1 2019-06-05 19:06:48
```

## SEE ALSO

For more information about web scraping using Python, refer to the documentation of libraries such as BeautifulSoup and Requests.
