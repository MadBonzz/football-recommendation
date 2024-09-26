from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

driver = webdriver.Chrome()

url = 'https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats'
driver.get(url)

time.sleep(2)

table = driver.find_element(By.ID, 'all_big5_table')

team_elements = table.find_elements(By.XPATH, '//*[@id="big5_table"]/tbody/tr/td[1]/a')

teams = []

for team_element in team_elements:
    team_name = team_element.text
    team_link = team_element.get_attribute('href')
    teams.append((team_name, team_link))

teams_df = pd.DataFrame(teams, columns=['Team_Name', 'Link'])
print(teams_df)

players = []

for index, row in teams_df.iterrows():
    team_name = row['Team_Name']
    link = row['Link']
    driver.get(link)
    time.sleep(1)
    
    table = driver.find_element(By.ID, 'all_stats_standard')

    player_elements = table.find_elements(By.XPATH, './/tbody/tr/th[@data-stat="player"]/a')
    
    for player in player_elements:
        name = player.text
        link = player.get_attribute('href')
        players.append((name, link))

players_df = pd.DataFrame(players, columns=['Name', 'Link'])
print(players_df)

players_df.to_csv('player_links.csv', index=False)

driver.quit()


