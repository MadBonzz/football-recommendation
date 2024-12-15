import pandas as pd
from DrissionPage import ChromiumOptions, ChromiumPage
from time import sleep
from selectolax.parser import HTMLParser
import re
import numpy as np
import gc
import os


options = ChromiumOptions()._is_headless
driver = ChromiumPage(options)


def extract_player_info(pos_html):
    text_only = re.sub(r'<[^>]*>', '', pos_html)
    text_only = text_only.replace("\n","").replace("\t","").replace("&nbsp;","")
    data = text_only.split("Wages")[0]

    position = re.search(r'Position:\s*([\w\s\-,()]+)', data)
    footed = re.search(r'Footed:\s*([\w]+)', data)
    height = re.search(r'(\d{3}cm)', data)
    weight = re.search(r'(\d+kg)', data)
    national_team = re.search(r'National Team:\s*([\w\s]+)', data)
    club = re.search(r'Club:\s*([\w\s\-]+)', data)

    return {
        "Position": position.group(1) if position else np.nan,
        "Preferred Foot": footed.group(1) if footed else np.nan,
        "Height": height.group(1) if height else np.nan,
        "Weight": weight.group(1) if weight else np.nan,
        "National Team": national_team.group(1).strip() if national_team else np.nan,
        "Club": club.group(1).strip() if club else np.nan,
    }

def extract_comparisons(comp):
    comps = []
    for pos in comp:
        comps.append(pos.strip())
    return '|'.join(comps)


def process_stats(stats_html):
    table_names = dict()
    for table in stats_html.keys():
        for node in HTMLParser(stats_html[table]).css('caption'):
            text = node.text().split(':')
            table_names[table] = text[0]
    final_dfs = []
    for table in table_names.keys():
        stats_df = pd.read_html(stats_html[table], match=table_names[table], flavor='lxml')[0]
        new_df = pd.DataFrame()
        for col in stats_df.columns:
            if('Unnamed' in col[0]):
                new_df[str(col[1])] = stats_df[col[0]][col[1]]
            else:
                new_df[str(col[0]) + '_' + str(col[1])] = stats_df[col[0]][col[1]]

        stats_df = pd.DataFrame(columns=new_df.columns)
        df_idx = 0
        for idx, row in new_df.iterrows():
            if((row['Season'] is np.nan) or (row['Squad'] is np.nan)):
                continue
            if(('Seasons' in row['Season']) or ('Clubs' in row['Squad'])):
                break
            stats_df.loc[df_idx] = row
            seasons = row['Season'].split('-')
            stats_df.at[df_idx, 'for_join'] = str(row['Season']) + '-' + str(row['Squad'])
            df_idx += 1
        final_dfs.append(stats_df)
    statistics = pd.DataFrame()
    for i in range(len(final_dfs)):
        if i == 0:
            statistics = final_dfs[i].copy()
            continue
        result = pd.concat([statistics, final_dfs[i]], axis=1)
        result = result.loc[:,~result.columns.duplicated()]
        statistics = result.copy()
    statistics.drop(columns=['for_join'], inplace=True)
    return statistics


std_types = ["#stats_standard_dom_lg", "#stats_shooting_dom_lg", "#stats_passing_dom_lg", "#stats_passing_types_dom_lg", 
               "#stats_gca_dom_lg", "#stats_defense_dom_lg", "#stats_possession_dom_lg", "#stats_playing_time_dom_lg",
               "#stats_misc_dom_lg"]

gk_types =  ["#stats_keeper_dom_lg", "#stats_keeper_adv_dom_lg", "#stats_standard_dom_lg", "#stats_passing_dom_lg", "#stats_passing_types_dom_lg", 
               "#stats_gca_dom_lg", "#stats_defense_dom_lg", "#stats_possession_dom_lg", "#stats_playing_time_dom_lg",
               "#stats_misc_dom_lg"]

df = pd.read_csv('players.csv')

names_list = []

with open('scraped.txt', 'r+', encoding='utf-8') as file:
    for line in file:
        line = line.replace('\n','')
        names_list.append(line)
        
curr_list = []

try:
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
            temp = driver._find_elements("#meta", timeout=14)
            pos  = temp.html
            is_gk = 'GK' in pos
        except Exception:
            print("Skipping {}".format(name))
            curr_list.remove(name)
            break

        try:
            comparables = []
            temp = driver._find_elements(".filter switcher", timeout=5)
            comparisons = temp.children()
            for  child in comparisons:
                comparables.append(child.inner_html.split("vs.")[-1].split('</')[0])
        except:
            print("No comparison table")
            comparables = []
            
        if not is_gk:
            for stat_type in std_types:
                try:
                    temp = driver._find_elements(stat_type, timeout=5)
                    player[stat_type] = str(temp.html)
                except Exception:
                    print(f"Element {stat_type} not found for player {name}. Skipping...")
                    continue
        else:
            for stat_type in gk_types:
                try:
                    temp = driver._find_elements(stat_type, timeout=5)
                    player[stat_type] = str(temp.html)
                except Exception:
                    print(f"Element {stat_type} not found for player {name}. Skipping...")
                    continue

        if(len(player.keys()) == 0):
            print(f"No stats found for {name}")
            continue
        personal_info = extract_player_info(pos)
        comp          = extract_comparisons(comparables)
        statistics    = process_stats(player)

        statistics['Name'] = name
        statistics['Comparables'] = comp
        for key in personal_info.keys():
            statistics[key] = personal_info[key]

        if not is_gk:
            statistics.to_csv('statistics.csv', mode='a', header=False, index=False)
        else:
            statistics.to_csv('gk_statistics.csv', mode='a', header=False, index=False)

except KeyboardInterrupt:
    print("Keyboard Interrupt")
    curr_list.remove(name)
finally:    
    with open('scraped.txt', 'a+', encoding='utf-8') as file:
        for name in curr_list:
            file.writelines(name + '\n')        
    driver.quit()
