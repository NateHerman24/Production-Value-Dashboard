import streamlit as st
import pandas as pd

# Load CSV
@st.cache_data
def load_data():
    df = pd.read_csv("productionvalue.csv")
    return df

df = load_data()

st.title("NBA Production Value Dashboard")

# -------------------------------
# TEAM MATCHUP SECTION
# -------------------------------

st.header("Team Win Prediction (Wins Added)")

teams = df['Team'].unique()

team_1 = st.selectbox("Select Team 1", teams)
team_2 = st.selectbox("Select Team 2", teams)

def team_wins_added(df, team, excluded_players):
    team_df = df[df['Team'] == team]
    team_df = team_df[~team_df['Player'].isin(excluded_players)]
    return team_df['Wins Added'].sum()

if team_1 and team_2:
    st.write(f"{team_1} vs {team_2}")

    excluded_1 = st.multiselect(
        f"Exclude players from {team_1}",
        df[df['Team'] == team_1]['Player'].tolist(),
        key="ex1"
    )

    excluded_2 = st.multiselect(
        f"Exclude players from {team_2}",
        df[df['Team'] == team_2]['Player'].tolist(),
        key="ex2"
    )

    team1_sum = team_wins_added(df, team_1, excluded_1)
    team2_sum = team_wins_added(df, team_2, excluded_2)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(team_1, f"{team1_sum:.2f}")

    with col2:
        st.metric(team_2, f"{team2_sum:.2f}")

    diff = abs(team1_sum - team2_sum)

    if st.button("Predict Matchup"):
        if team1_sum > team2_sum:
            st.write(f"{team_1} is predicted to win by {diff:.2f} Wins Added")
        elif team2_sum > team1_sum:
            st.write(f"{team_2} is predicted to win by {diff:.2f} Wins Added")
        else:
            st.write("It's a tie!")

# -------------------------------
# Team Rankings
# -------------------------------

st.header("Top Teams by Total Wins Added")

# Slider for number of teams
num_teams = st.slider(
    "Select number of teams to display",
    min_value=1,
    max_value=30,
    value=10,
    key="team_slider"
)

# Group by team and sum Wins Added
team_rankings = (
    df.groupby('Team')['Wins Added']
    .sum()
    .reset_index()
    .sort_values(by='Wins Added', ascending=False)
    .head(num_teams)
)

# Format for display
team_rankings = team_rankings.reset_index(drop=True)
team_rankings.index += 1
team_rankings['Wins Added'] = team_rankings['Wins Added'].map(lambda x: f"{x:.2f}")

# Display
st.table(team_rankings)

# -------------------------------
# PLAYER LOOKUP SECTION
# -------------------------------

st.header("Player Profile Lookup")

players = df['Player'].unique()
selected_player = st.selectbox("Select a Player", players)

if selected_player:
    player_data = df[df['Player'] == selected_player].iloc[0]

    st.subheader(selected_player)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Team", player_data['Team'])
        st.metric("Production Value", f"${player_data['Production Value (Millions)']:.2f}M")
        st.metric("Possesions", int(player_data['Possesions']))

    with col2:
        st.metric("RAPM Over Replacement", f"{player_data['RAPM over replacement']:.2f}")
        st.metric("AAV", f"${player_data['AAV']:.2f}M")

    with col3:
        st.metric("Wins Added", f"{player_data['Wins Added']:.2f}")
        st.metric("Net Value", f"{player_data['Net Value']:.2f}")

# -------------------------------
# LEADERBOARDS
# -------------------------------

st.header("Player Leaderboards")

stat_choice = st.selectbox(
    "Select Stat to Rank Players",
    [
        "RAPM over replacement",
        "Wins Added",
        "Production Value (Millions)",
        "Net Value"
    ]
)

num_players = st.slider("Number of players to display", 5, 300, 10)

leaderboard = df.sort_values(by=stat_choice, ascending=False).head(num_players)

leaderboard = leaderboard.reset_index(drop=True)
leaderboard.index += 1

leaderboard_display = leaderboard[['Player', 'Team', stat_choice]].copy()
leaderboard_display[stat_choice] = leaderboard_display[stat_choice].map(lambda x: f"{x:.2f}")

st.table(leaderboard_display)
