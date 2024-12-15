import pandas as pd
from DrissionPage import ChromiumOptions, ChromiumPage
from time import sleep
from bs4 import BeautifulSoup

options = ChromiumOptions()._is_headless
driver = ChromiumPage(options)

df = pd.read_csv('team_links.csv')

link_dict = {
    "Name" : [],
    "Link" : []
}

for i, row in df.iterrows():
    name = row['Name']
    url  = row['Link']
    print(name)

    driver.get("https://" + url)
    table = driver._find_elements("#all_stats_standard", timeout=10)
    table = table.children()[-1].children()[0].children()[-2]
    for team in table.children():
        content = team.inner_html
        if 'href' in content:
            soup = BeautifulSoup(content, 'html.parser')

            player_data = soup.find('th', {'data-stat': 'player'}).find('a')
            player_href = "https://fbref.com/" + player_data['href']
            player_name = player_data.text
            link_dict['Name'].append(player_name)
            link_dict['Link'].append(player_href)

players = pd.DataFrame(link_dict)
players.to_csv('players.csv')