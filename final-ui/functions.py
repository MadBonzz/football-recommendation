import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances

def check_comparables(df, idx, unique_comparables):
    comparables = []
    for comp in unique_comparables:
        if df.at[idx, comp] == 1:
            comparables.append(comp)
    return comparables

def find_similar(df, player, unique_comparables, columns, club=None, league=None, tier=None):
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
    if 'Side' in player_row.columns:
        if player_row['Side'] is not np.nan:
            side = player_row['Side']
            remaining_df = remaining_df[remaining_df['Side'].isin([side.iloc[0], np.nan])]
            print("Side is : ")
            print(side.iloc[0])
            print("Shape is : ")
            print(remaining_df.shape)
    comparables = check_comparables(df, player_row.index[0], unique_comparables)
    print(comparables)
    if(len(comparables) != 0):
        remaining_df = remaining_df.loc[(remaining_df[comparables] == 1).any(axis=1)]
    elif(player_row['Detailed'] is not np.nan):
        detailed = player_row['Detailed'].split('-')
        remaining_df = remaining_df.loc[(remaining_df[detailed] == 1).any(axis=1)]
    else:
        pos = player_row['Position'].split('-')
        remaining_df = remaining_df.loc[(remaining_df[pos] == 1).any(axis=1)]
    
    player_row = player_row[columns]
    columns.append('Name')
    remaining_df = remaining_df[columns]
    names = remaining_df['Name']
    remaining_df.drop(columns=['Name'], inplace=True)
    remaining_df.dropna(inplace=True)
    dist = euclidean_distances(player_row, remaining_df)
    remaining_df['similarity'] = dist[0]
    remaining_df = pd.concat([remaining_df, names], axis=1)
    columns.remove('Name')
    return null_columns, columns, remaining_df[['Name', 'similarity']]