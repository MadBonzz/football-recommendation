import streamlit as st
import pandas as pd
import functions

st.title('Similar-Players-Finder')

df = pd.read_csv('final-ui/percentile.csv')

unique_comparables = ['Att Mid / Wingers', 'Forwards', 'Midfielders', 'Center Backs', 'Fullbacks']

columns = [col for col in df.columns if col not in ['Name', 'Club', 'League', 'Tier', 'FW', 'MF', 'DF', 'Unnamed: 0',
                'Age', 'Forwards', 'Midfielders', 'Center Backs', 'Att Mid / Wingers', 'Fullbacks', 'FB', 'DM', 'AM', 
                'CB', 'CM', 'WM', 'left', 'right', 'Position', 'Detailed', 'Side']]
print(columns)
options = ["All"] + columns

clubs = df['Club'].unique().tolist()
club_options = clubs + ["All"]
leagues = df['League'].unique().tolist()
league_options = leagues + ["All"]
tiers = df['Tier'].unique().tolist()
tier_options = tiers + ["All"]


selected_options = st.multiselect(
    "Select Parameters",
    options=options,
    default=["All"]
)

selected_clubs = st.multiselect(
    "Select Cubs",
    options=club_options, 
    default=['All']
)

selected_leagues = st.multiselect(
    "Select Leagues",
    options=league_options,
    default=['All']
)

seelcted_tiers = st.multiselect(
    "Select Tiers",
    options=tier_options,
    default=['All']
)

parameters = [selected_clubs, selected_leagues, seelcted_tiers]

possible_names = df['Name'].unique().tolist()

search_query = ""
filtered_names = [name for name in possible_names if search_query.lower() in name.lower()]

selected_name = st.selectbox("Matching names:", filtered_names if filtered_names else ["No matching names found"])

if st.button("Submit"):
    if "All" in selected_options:
        final_selection = columns
    else:
        final_selection = selected_options
    
    for parameter in parameters:
        if 'All' in parameter:
            parameter = parameter.remove('All')

    if selected_name == "No matching names found":
        st.warning("Please select a valid name.")
    else:
        st.write(f"You selected: {selected_name}")

        null_cols, cols, similar = functions.find_similar(df, selected_name, unique_comparables, final_selection, selected_clubs, selected_leagues, seelcted_tiers)

        similar = similar.sort_values(by='similarity').head(10).reset_index(drop=True)
        if len(null_cols) > 0:
            st.write(f"The following data was not found for the player")
            st.write(", ".join(map(str, null_cols)))
        st.write(similar)
