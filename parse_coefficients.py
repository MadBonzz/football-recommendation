import json
import pandas as pd

# Filepath of the JSON file
file_path = "coefficients.json"
all_seasons = []
with open(file_path, "r") as json_file:
    json_list = json.load(json_file)  # Load the JSON data as a Python list

    complete_data = dict()
    for i, json_obj in enumerate(json_list):
        print(f"JSON Object {i + 1}:")
        print(f"The number of members are : {len(json_obj['data']['members'])}")
        for country in json_obj['data']['members']:
            country_name = country['member']['countryName']
            if country_name not in complete_data.keys():
                complete_data[country_name] = []
            points = country['overallRanking']['totalValue']
            season = country['overallRanking']['targetSeasonYear']
            complete_data[country_name].append({season : points})

transformed_data = {}
for country, records in complete_data.items():
    transformed_data[country] = {season: points for record in records for season, points in record.items()}

df = pd.DataFrame.from_dict(transformed_data, orient='index')

df.index.name = 'country'
df.columns.name = 'season'

df.to_csv('coefficients.csv')