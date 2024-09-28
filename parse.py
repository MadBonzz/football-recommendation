import pandas as pd
from selectolax.parser import HTMLParser
import re
import numpy as np
import gc
import os

READ_FILENAME = "parsed.txt"

names_list = []
#Adds already parsed player information to names_list
if os.path.exists(READ_FILENAME):
    with open('parsed.txt', 'r+', encoding='utf-8') as file:
        for line in file:
            line = line.replace('\n','')
            names_list.append(line)

def extract_player_info(pos_html):
    info = []
    for node in HTMLParser(pos_html).css('p'):
        name = node.text()
        info.append(name.strip())
        
    attrs = []
    for val in info:
        val = re.sub('▪| |\xa0|\n','', val)
        attrs.append(val)
        
    data = "\n".join(attrs)
    
    position_pattern = r'Position:\s*([A-Z\-\/]+)(?:\s*\(.*\))?'  # Capture main position before parentheses
    footed_pattern = r'Footed:\s*(\w+)'  # Capture footed (left/right)
    height_pattern = r'(\d{3})cm'  # Capture height in cm
    weight_pattern = r'(\d{2,3})kg'  # Capture weight in kg
    age_pattern = r'Age:(\d+)'  # Capture age in years
    national_team_pattern = r'National Team:\s*([A-Za-z\s]+)'  # Capture national team
    club_pattern = r'Club:\s*([A-Za-z\s]+)'  # Capture club

    # Function to extract data
    def extract_data(pattern, text):
        match = re.search(pattern, text)
        return match.group(1) if match else np.nan

    # Extracting fields
    position = extract_data(position_pattern, data)
    footed = extract_data(footed_pattern, data)
    height = extract_data(height_pattern, data)
    weight = extract_data(weight_pattern, data)
    age = extract_data(age_pattern, data)
    national_team = extract_data(national_team_pattern, data)
    club = extract_data(club_pattern, data)

    return {
        "position"         :position,
        "footed"          :footed,
        "height"          :height,
        "weight"          :weight,
        "age"             :age,
        "national_team"   :national_team,
        "current_club"    :club
    }


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

df = pd.read_csv('player_stats.csv')

df.drop(columns=['StatDict'], inplace=True)
df.rename(columns={'Position':'StatDict', 'Name':'Position', 'Unnamed: 0':'Name'}, inplace=True)

if(len(names_list) == 0):
    statistics_df    = pd.DataFrame()
    gk_statistics_df = pd.DataFrame()
else:
    statistics_df    = pd.read_csv('statistics.csv')
    gk_statistics_df = pd.read_csv('gk_statistics.csv')

try:
    for idx, row in df.iterrows():
        name  = row['Name']
        if(name in names_list):
            continue
        pos   = row['Position']
        stats = eval(row['StatDict'])
        
        print(name)
        if(len(stats.keys()) == 0):
            print(f"No stats found for {name}")
            continue
        
        personal_info = extract_player_info(pos)
        statistics    = process_stats(stats)
        
        statistics['Name'] = name
        for key in personal_info.keys():
            statistics[key] = personal_info[key]
        if((personal_info['position'] is np.nan) or ('GK' not in personal_info['position'])):
            statistics_df = pd.concat([statistics_df, statistics])
        else:
            gk_statistics_df = pd.concat([gk_statistics_df, statistics])
        with open('parsed.txt', 'a+', encoding='utf-8') as file:
            file.writelines(name + '\n')
        gc.collect()
finally:
    if(len(names_list) == 0):
        statistics_df.to_csv('statistics.csv', mode='a', header=True, index=False)
        gk_statistics_df.to_csv('gk_statistics.csv', mode='a', header=True, index=False)
    else:
        statistics_df.to_csv('statistics.csv', mode='a', header=False, index=False)
        gk_statistics_df.to_csv('gk_statistics.csv', mode='a', header=False, index=False)
    
    
