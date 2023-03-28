import sys
import requests
from bs4 import BeautifulSoup

year = sys.argv[1] # 1967
base_url = "https://watchasian.id"

URL = f"{base_url}/released-in-{year}.html"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
# links = soup.select("a.img")
links = soup.find_all('a', {'class': 'img', 'href': True})

for l in links:
  url1 = base_url + l['href']
  print(l.text.strip(), url1)
  page1 = requests.get(url1)
  soup1 = BeautifulSoup(page1.content, "html.parser")
  links1 = soup1.find_all('a', {'class': 'img', 'href': True})
  for l1 in links1:
    print(l1.text.strip())

