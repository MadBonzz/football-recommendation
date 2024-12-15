import pandas as pd
from selectolax.parser import HTMLParser
import re
import numpy as np
import gc
import os

READ_FILENAME = "parsed.txt"

names_list = []
if os.path.exists(READ_FILENAME):
    with open('parsed.txt', 'r+', encoding='utf-8') as file:
        for line in file:
            line = line.replace('\n','')
            names_list.append(line)

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
    for pos in eval(comp):
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

df = pd.read_csv('detailed_stats.csv', header=None, names=['Name', 'Position', 'Comparable', 'Statistics'])

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
        comparable = row['Comparable']
        stats = eval(row['Statistics'])
        
        print(name)
        if(len(stats.keys()) == 0):
            print(f"No stats found for {name}")
            continue
        
        personal_info = extract_player_info(pos)
        comp          = extract_comparisons(comparable)
        statistics    = process_stats(stats)
        
        statistics['Name'] = name
        statistics['Comparables'] = comp
        for key in personal_info.keys():
            statistics[key] = personal_info[key]
        if((personal_info['Position'] is np.nan) or ('GK' not in personal_info['Position'])):
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
    
    
