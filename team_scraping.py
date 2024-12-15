import pandas as pd
from DrissionPage import ChromiumOptions, ChromiumPage
from time import sleep
from bs4 import BeautifulSoup

options = ChromiumOptions()._is_headless
driver = ChromiumPage(options)

top5 = 'https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats'
eredivisie = 'https://fbref.com/en/comps/23/Eredivisie-Stats'
primeira = 'https://fbref.com/en/comps/32/Primeira-Liga-Stats'
turkey = 'https://fbref.com/en/comps/26/Super-Lig-Stats'

link_dict = {
    "Name" : [],
    "Link" : []
}

def extract_top5_leagues():
    driver.get(top5)
    table = driver._find_elements("#big5_table", timeout=10)
    table = table.children()[3]
    for team in table.children():
        content = team.inner_html
        if 'href' in content:
            soup = BeautifulSoup(content, 'html.parser')

            team_data = soup.find('td', {'data-stat': 'team'})
            team_link = team_data.find('a')

            team_href = 'fbref.com/' + team_link['href']
            team_name = team_link.text

            link_dict['Name'].append(team_name)
            link_dict['Link'].append(team_href)

def extract_eredivisie():
    driver.get(eredivisie)
    table = driver._find_elements("#results2024-2025231_overall", timeout=10)
    table = table.children()[3]
    for team in table.children():
        content = team.inner_html
        if 'href' in content:
            soup = BeautifulSoup(content, 'html.parser')

            team_data = soup.find('td', {'data-stat': 'team'})
            team_link = team_data.find('a')

            team_href = 'fbref.com/' + team_link['href']
            team_name = team_link.text

            link_dict['Name'].append(team_name)
            link_dict['Link'].append(team_href)

def extract_primeira():
    driver.get(primeira)
    table = driver._find_elements("#results2024-2025321_overall", timeout=10)
    table = table.children()[3]
    for team in table.children():
        content = team.inner_html
        if 'href' in content:
            soup = BeautifulSoup(content, 'html.parser')

            team_data = soup.find('td', {'data-stat': 'team'})
            team_link = team_data.find('a')

            team_href = 'fbref.com/' + team_link['href']
            team_name = team_link.text

            link_dict['Name'].append(team_name)
            link_dict['Link'].append(team_href)

def extract_turkish():
    driver.get(turkey)
    table = driver._find_elements("#results2024-2025261_overall", timeout=10)
    table = table.children()[-1]
    for team in table.children():
        content = team.inner_html
        if 'href' in content:
            soup = BeautifulSoup(content, 'html.parser')

            team_data = soup.find('td', {'data-stat': 'team'})
            team_link = team_data.find('a')

            team_href = 'fbref.com/' + team_link['href']
            team_name = team_link.text

            link_dict['Name'].append(team_name)
            link_dict['Link'].append(team_href)

extract_top5_leagues()
extract_eredivisie()
extract_primeira()
extract_turkish()

df = pd.DataFrame(link_dict)
print(df.head())
df.to_csv('team_links.csv')