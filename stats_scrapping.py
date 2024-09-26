from undetected_chromedriver import Chrome
import pandas as pd
from DrissionPage import ChromiumOptions, ChromiumPage
from time import sleep


options = ChromiumOptions()._headless
driver = ChromiumPage(options)



std_types = ["#stats_standard_dom_lg", "#stats_shooting_dom_lg", "#stats_passing_dom_lg", "#stats_passing_types_dom_lg", 
               "#stats_gca_dom_lg", "#stats_defense_dom_lg", "#stats_possession_dom_lg", "#stats_playing_time_dom_lg",
               "#stats_misc_dom_lg"]

gk_types =  ["#stats_keeper_dom_lg", "#stats_keeper_adv_dom_lg", "#stats_standard_dom_lg", "#stats_passing_dom_lg", "#stats_passing_types_dom_lg", 
               "#stats_gca_dom_lg", "#stats_defense_dom_lg", "#stats_possession_dom_lg", "#stats_playing_time_dom_lg",
               "#stats_misc_dom_lg"]
players = []

df = pd.read_csv('player_links.csv')

names_list = []

with open('parsed.txt', 'r+', encoding='utf-8') as file:
    for line in file:
        line = line.replace('\n','')
        names_list.append(line)
        
curr_list = []

for idx, row in df.iterrows():
    player = dict()
    name = row['Name']
    if name in names_list:
        continue
    curr_list.append(name)
    url  = row['Link']
    print(url)
    driver.get(url)
    sleep(8)
    
    try:
        temp = driver._find_elements("#meta")
        pos  = temp.html
        is_gk = 'GK' in pos
    except Exception:
        print("Skipping {}".format(name))
        curr_list.remove(name)
        break
        
    """
    finally:
        player_stats = pd.DataFrame.from_dict(players, columns=['Name', 'Position', 'StatDict'])
        player_stats.to_csv('player_stats.csv', mode='a', header=False, index=False)
        with open('parsed.txt', 'a+') as file:
            for name in curr_list:
                file.writelines(name + '\n')
    """
    if not is_gk:
        for stat_type in std_types:
            try:
                temp = driver._find_elements(stat_type)
                player[stat_type] = str(temp.html)
            except Exception:
                print(f"Element {stat_type} not found for player {name}. Skipping...")
                continue
    else:
        for stat_type in gk_types:
            try:
                temp = driver._find_elements(stat_type)
                player[stat_type] = str(temp.html)
            except Exception:
                print(f"Element {stat_type} not found for player {name}. Skipping...")
                continue
            
                
    players.append([name, pos, player])
    
with open('parsed.txt', 'a+', encoding='utf-8') as file:
    for name in curr_list:
        file.writelines(name + '\n')
player_stats = pd.DataFrame(players)
print(player_stats.head())
player_stats.to_csv('player_stats.csv', mode='a', header=False, index=False) 
    
driver.quit()
