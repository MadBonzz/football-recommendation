import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def find_similar(df, player, columns, club=None, league=None, tier=None):
    player_row = df[df['Name'] == player].drop(columns=['Name']).dropna(axis=1)
    null_columns = list(set(columns) - set(player_row.columns))
    columns = [col for col in columns if col not in null_columns]
    remaining_df = df[df['Name'] != player]
    if club:
        remaining_df = remaining_df[remaining_df['current_club'].isin(club)]
    if league:
        remaining_df = remaining_df[remaining_df['League'].isin(league)]
    if tier:
        remaining_df = remaining_df[remaining_df['Tier'].isin(tier)]
    df_lists = []
    if player_row['FW'].iat[0] == 1:
        temp_df = remaining_df[remaining_df['FW'] == 1]
        df_lists.append(temp_df)
    if player_row['MF'].iat[0] == 1:
        temp_df = remaining_df[remaining_df['MF'] == 1]
        df_lists.append(temp_df)
    if player_row['DF'].iat[0] == 1:
        temp_df = remaining_df[remaining_df['DF'] == 1]
        df_lists.append(temp_df)
    remaining_df = df_lists[0]
    if len(df_lists) > 1:
        for i in range(1, len(df_lists)):
            remaining_df = pd.concat([remaining_df, df_lists[i]])
    remaining_df.drop_duplicates(inplace=True)
    player_row = player_row[columns]
    columns.append('Name')
    remaining_df = remaining_df[columns]
    names = remaining_df['Name']
    remaining_df.drop(columns=['Name'], inplace=True)
    remaining_df.dropna(inplace=True)
    cosine_sim = cosine_similarity(player_row, remaining_df)
    remaining_df['similarity'] = cosine_sim[0]
    remaining_df = pd.concat([remaining_df, names], axis=1)
    columns.remove('Name')
    return null_columns, columns, remaining_df[['Name', 'similarity']]