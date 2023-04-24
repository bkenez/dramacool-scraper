
import requests
import re
import argparse
from bs4 import BeautifulSoup
from alive_progress import alive_bar

base_url = "https://dramacool.cy"

parser = argparse.ArgumentParser()

parser.add_argument('--year', '--years', required=True)
parser.add_argument('--newer')
parser.add_argument('--country')
parser.add_argument('--genre')
parser.add_argument('--act')
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
  
  def print_data(self, ep, newer=False):
    if not ep:
      if self.actors:
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
    URL = f"{base_url}/released-in-{year}.html?page={cursor}"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    
    parse_dramas_on_page(soup, drama_results, bar)
    cursor += 1  

  return drama_results

def parse_dramas_on_page(soup, drama_results, bar):
  drama_links = soup.find_all('a', {'class': 'img', 'href': True})

  for drama in drama_links:
    drama_url = base_url + drama['href']
    drama_page = requests.get(drama_url)
    drama_soup = BeautifulSoup(drama_page.content, "html.parser")

    drama_country = drama_soup.find(href=re.compile("country"))
    drama_year = drama_soup.find(href=re.compile("released"))
    drama_genre = drama_soup.find(href=re.compile("genre"))
    drama_actors = drama_soup.find_all(onclick=re.compile("star"))
    try:
      drama_latest_raw = drama_soup.find('span', {'class': 'type RAW'}).next_sibling.next_sibling
      drama_latest_raw_time = drama_soup.find('span', {'class': 'type RAW'}).next_sibling.next_sibling.next_sibling.next_sibling
    except AttributeError:
      drama_latest_raw = None
      drama_latest_raw_time = None
      pass

    try:
      drama_latest_sub = drama_soup.find('span', {'class': 'type SUB'}).next_sibling.next_sibling
      drama_latest_sub_time = drama_soup.find('span', {'class': 'type SUB'}).next_sibling.next_sibling.next_sibling.next_sibling
    except AttributeError:
      drama_latest_sub = None
      drama_latest_sub_time = None 
      pass

    
    actor_list = []
    for actor in drama_actors:
      actor_list.append(actor.text.strip())
    actor_list = ', '.join(actor_list)

    if drama_latest_raw:
      latest_raw = 'RAW ' + drama_latest_raw.text.strip() + ' ' + drama_latest_raw_time.text.strip()
    else:
      latest_raw = None

    if drama_latest_sub:
      latest_sub = 'SUB ' + drama_latest_sub.text.strip() + ' ' + drama_latest_sub_time.text.strip()
    else:
      latest_sub = None

    drama_episode_list = dict()
    drama_episodes = drama_soup.find_all('h3',string=re.compile(drama['title'] + ' Episode'))

    for episode in drama_episodes:
      episode_title = episode.text.strip()
      episode_time = episode.next_sibling.next_sibling.text.strip()
      episode_type = episode.previous_sibling.previous_sibling.text.strip()
      drama_episode_list[f'{episode_type} {episode_title}'] = episode_time

    drama_results.append(Drama( drama['title']
                              ,drama_country.text.strip()
                              ,drama_year.text.strip()
                              ,drama_genre.text.strip()
                              ,actor_list
                              ,latest_raw
                              ,latest_sub
                              ,drama_episode_list))
    bar()

drama_results = []
args = parser.parse_args()

with alive_bar() as bar:
  if "-" in args.year:
    start_year = int(args.year.split("-")[0])
    end_year = int(args.year.split("-")[1])

    while start_year <= end_year:
      drama_results = drama_results + parse_dramas_per_year(start_year, bar)
      start_year += 1

  else:
    drama_results = parse_dramas_per_year(args.year, bar)

for drama in drama_results:
  if args.genre and drama.genre.lower() != args.genre.lower():
    continue
  if args.country and drama.country.lower() != args.country.lower():
    continue
  if args.act and args.act.lower() not in drama.actors.lower():
    continue

  drama.print_data(args.ep, args.newer)

