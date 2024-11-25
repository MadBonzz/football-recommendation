import streamlit as st
import pandas as pd
import functions

st.title('Similar-Players-Finder')

df = pd.read_csv('percentile.csv')

columns = [col for col in df.columns if col not in ['Name', 'current_club', 'League', 'Tier', 'FW', 'MF', 'DF', 'Unnamed: 0']]
options = ["All"] + columns

selected_options = st.multiselect(
    "Select Parameters",
    options=options,
    default=["All"]
)

possible_names = df['Name'].unique().tolist()

search_query = ""
filtered_names = [name for name in possible_names if search_query.lower() in name.lower()]

selected_name = st.selectbox("Matching names:", filtered_names if filtered_names else ["No matching names found"])

if st.button("Submit"):
    if "All" in selected_options:
        final_selection = columns
    else:
        final_selection = selected_options

    if selected_name == "No matching names found":
        st.warning("Please select a valid name.")
    else:
        st.write(f"You selected: {selected_name}")

        null_cols, cols, similar = functions.find_similar(df, selected_name, final_selection)

        similar = similar.sort_values(by='similarity', ascending=False).head(20).reset_index(drop=True)
        if len(null_cols) > 0:
            st.write(f"The following data was not found for the player")
            st.write(", ".join(map(str, null_cols)))
        st.write(similar)
