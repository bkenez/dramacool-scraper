
import requests
import re
import argparse
from bs4 import BeautifulSoup
from alive_progress import alive_bar

base_url = "https://dramacool.cy"

parser = argparse.ArgumentParser()

parser.add_argument('--year', '--years')
parser.add_argument('--newer')
parser.add_argument('--country')
parser.add_argument('--genre')
parser.add_argument('--act')
parser.add_argument('--noact', action='store_true')
parser.add_argument('--ep', action='store_true')

class Drama:
  def __init__(self, title, country, year, genre, actors, latest_raw, latest_sub, episode_list):
    self.title = title
    self.country = country
    self.year = year
    self.genre = genre
    self.actors = actors
    self.latest_raw = latest_raw
    self.latest_sub = latest_sub
    self.episode_list = episode_list
  
  def print_data(self, ep, newer, list_actors):
    if not ep:
      if self.actors and not list_actors:
        print(f'{self.title} - {self.year} - {self.country} - {self.genre} - {self.actors}')
      else:
        print(f'{self.title} - {self.year} - {self.country} - {self.genre}')
    if not newer:
      if self.latest_raw:
        print(f'  {self.latest_raw}')
      if self.latest_sub:
        print(f'  {self.latest_sub}')
    else:
      for episode, time in self.episode_list.items():
        if time > newer:
          print(f'{episode} {time}')

def regex_escaper(string):
  return string.replace("(","\\(").replace(")","\\)").replace(".","\\.")

def soupify_url(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")
  
def parse_dramas_per_year(year,bar):
  drama_results = []
  URL = f"{base_url}/released-in-{year}.html"
  page = requests.get(URL)
  soup = BeautifulSoup(page.content, "html.parser")
  pages = 1
  cursor = 1

  try:
    last_page = soup.find('li', {'class': 'last'}).a['href']
    pages = int(last_page.split('=')[1])
  except AttributeError:
    pass


  bar.title(f"Getting dramas from {year}...")
  while cursor <= pages:
    soup = soupify_url(f"{base_url}/released-in-{year}.html?page={cursor}")
    
    parse_dramas_on_page(soup, drama_results, bar)
    cursor += 1  

  return drama_results

def get_drama_info(soup, info):
  return soup.find(href=re.compile(info)).text.strip()

def get_drama_actors(soup):
  drama_actors = soup.find_all(onclick=re.compile("star"))
  actor_list = []
  for actor in drama_actors:
    actor_list.append(actor.text.strip())
  actor_list = ', '.join(actor_list)

  return actor_list

def get_drama_latest_episodes(soup):
  try:
    drama_latest_raw = soup.find('span', {'class': 'type RAW'}).next_sibling.next_sibling
    drama_latest_raw_time = soup.find('span', {'class': 'type RAW'}).next_sibling.next_sibling.next_sibling.next_sibling
  except AttributeError:
    drama_latest_raw = None
    drama_latest_raw_time = None
    pass

  try:
    drama_latest_sub = soup.find('span', {'class': 'type SUB'}).next_sibling.next_sibling
    drama_latest_sub_time = soup.find('span', {'class': 'type SUB'}).next_sibling.next_sibling.next_sibling.next_sibling
  except AttributeError:
    drama_latest_sub = None
    drama_latest_sub_time = None 
    pass

  if drama_latest_raw:
    latest_raw = 'RAW ' + drama_latest_raw.text.strip() + ' ' + drama_latest_raw_time.text.strip()
  else:
    latest_raw = None

  if drama_latest_sub:
    latest_sub = 'SUB ' + drama_latest_sub.text.strip() + ' ' + drama_latest_sub_time.text.strip()
  else:
    latest_sub = None

  return latest_raw,latest_sub

def get_drama_episode_list(soup, title):
  drama_episode_list = dict()
  drama_episodes = soup.find_all('h3',string=re.compile(regex_escaper(title) + ' Episode'))
  #speacial case handling with inconsistent work/episode titling
  if not drama_episodes:
    drama_episodes = soup.find_all('h3',string=re.compile(regex_escaper(title.split('(')[0].strip()) + ' Episode'))

  for episode in drama_episodes:
    episode_title = episode.text.strip()
    episode_time = episode.next_sibling.next_sibling.text.strip()
    episode_type = episode.previous_sibling.previous_sibling.text.strip()
    drama_episode_list[f'{episode_type} {episode_title}'] = episode_time

  return drama_episode_list

def parse_dramas_on_page(soup, drama_results, bar):
  drama_links = soup.find_all('a', {'class': 'img', 'href': True})

  for drama in drama_links:
    drama_url = base_url + drama['href']
    drama_page = requests.get(drama_url)
    drama_soup = BeautifulSoup(drama_page.content, "html.parser")

    drama_country = get_drama_info(drama_soup, "country")
    drama_year =  get_drama_info(drama_soup, "released")
    drama_genre =  get_drama_info(drama_soup, "genre")
    drama_actors = get_drama_actors(drama_soup)
    latest_eps = get_drama_latest_episodes(drama_soup)
    drama_episode_list = get_drama_episode_list(drama_soup,drama['title'])

    drama_results.append(Drama( drama['title']
                              ,drama_country
                              ,drama_year
                              ,drama_genre
                              ,drama_actors
                              ,latest_eps[0]
                              ,latest_eps[1]
                              ,drama_episode_list))
    bar()

def get_total_dramas(url):
  soup = soupify_url(url)

  pages = 1
  try:
    last_page = soup.find('li', {'class': 'last'}).a['href']
    pages = int(last_page.split('=')[1])
  except AttributeError:
    pass

  if pages > 1:
    soup = soupify_url(f"{url}?page={pages}")

  drama_links = soup.find_all('a', {'class': 'img', 'href': True})

  return (pages-1) * 36 + int(len(drama_links))

drama_results = []
args = parser.parse_args()
    
if args.year and "-" in args.year:
  start_year = int(args.year.split("-")[0])
  end_year = int(args.year.split("-")[1])

if args.act:
  actor = args.act.lower().strip().replace(" ","-")
  URL = f"{base_url}/star/{actor}"
  soup = soupify_url(URL)
  total = get_total_dramas(URL)

  with alive_bar(total) as bar:
    parse_dramas_on_page(soup, drama_results, bar)


elif "-" in args.year:
    year = start_year
    total = 0

    while year <= end_year:
      total += get_total_dramas(f"{base_url}/released-in-{year}.html")
      year += 1

    year = start_year

    with alive_bar(total) as bar:
      while year <= end_year:
        drama_results = drama_results + parse_dramas_per_year(year, bar)
        year += 1

else:
  total = get_total_dramas(f"{base_url}/released-in-{args.year}.html")  
  with alive_bar(total) as bar:
    drama_results = parse_dramas_per_year(args.year, bar)

for drama in drama_results:
  if args.year:
    if "-" in args.year:
      if int(drama.year) < start_year or int(drama.year) > end_year:
        continue
    elif drama.year != args.year:
      continue 
  if args.genre and drama.genre.lower() != args.genre.lower():
    continue
  if args.country and drama.country.lower() != args.country.lower():
    continue
  if args.act and args.act.lower() not in drama.actors.lower():
    continue
  
  drama.print_data(args.ep, args.newer, args.noact)

