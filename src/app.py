import streamlit as st
from espn_api.football import League
from api_client import fetch_league_data
from visualization import plot_luck_indices, plot_pythagorean_expectation_luck, save_luck_indices_to_file_3, create_scheduling_luck_dataframe, save_and_visualize_pythagorean_luck \
    , create_scatterplot_luck_figure
from analysis import calculate_pythagorean_expectation_luck, calculate_scatterplot_luck, get_luck_index_3
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
LEAGUE_ID = os.getenv('LEAGUE_ID')
SWID = os.getenv('SWID')
ESPN_S2 = os.getenv('ESPN_S2')

def log_in():
    st.title("ESPN Fantasy Football Luck Analyzer")
    st.write("Welcome to the Fantasy Football Luck Analyzer!")
    st.write("This tool will help you determine how lucky or unlucky you've been in your fantasy football league.") 

    if 'league' not in st.session_state:
        st.session_state['league'] = None
    if 'league_data' not in st.session_state:
        st.session_state['league_data'] = None

    if DEBUG_MODE:
        st.session_state['logged_in'] = True
        st.session_state['league_id'] = LEAGUE_ID
        st.session_state['swid'] = SWID
        st.session_state['espn_s2'] = ESPN_S2
        # Fetch league data and store in session state
        league = League(league_id=LEAGUE_ID, year=2024, espn_s2=ESPN_S2, swid=SWID)
        st.session_state['league'] = league
        st.session_state['league_data'] = fetch_league_data(league)
        st.rerun()
    else:
        # Input Fields
        st.header("Enter Your League Information")
        league_id = st.text_input("League ID", help="Your ESPN Fantasy Football League ID")
        swid = st.text_input("SWID", help="Find this in your browser cookies for ESPN.")
        espn_s2 = st.text_input("ESPN_S2", help="Find this in your browser cookies for ESPN.", type="password")

        with st.expander("How to find your SWID and ESPN_S2 tokens"):
            st.write("""
                1. Open your web browser and go to the ESPN Fantasy Football website.
                2. Log in to your account.
                3. Open the developer tools (usually by right-clicking on the page and selecting "Inspect" or pressing F12).
                4. Go to the "Application" tab.
                5. Under "Cookies", find the cookies for `espn.com`.
                6. Look for the `SWID` and `ESPN_S2` cookies and copy their values.
            """)

        # Submit Button
        if st.button("Submit"):
            if not league_id or not swid or not espn_s2:
                st.error("Please fill in all fields.")
            else:
                st.success("Credentials submitted! Fetching data...")
                st.session_state['logged_in'] = True
                st.session_state['league_id'] = league_id
                st.session_state['swid'] = swid
                st.session_state['espn_s2'] = espn_s2

                # Fetch league data and store in session state
                league = League(league_id=league_id, year=2024, espn_s2=espn_s2, swid=swid)
                st.session_state['league'] = league
                st.session_state['league_data'] = fetch_league_data(league)

                st.rerun()

def display_visualizations():
    st.title("Luck Analysis")
    st.write("Here are some visualizations to help you analyze your luck in the league.")

    # Buttons for each metric
    if st.button("Opponent Underperformance"):
        st.session_state['metric'] = 'opponent_underperformance'
    if st.button("Pythagorean Expectation"):
        st.session_state['metric'] = 'pythagorean_expectation'
    if st.button("Scatterplot Luck"):
        st.session_state['metric'] = 'scatterplot_luck'
    if st.button("Scheduling Luck"):
        st.session_state['metric'] = 'scheduling_luck'

    # Display the selected metric
    if 'metric' in st.session_state:
        if 'league_data' not in st.session_state or 'league' not in st.session_state:
            st.error("League data not found. Please log in again.")
            st.session_state['logged_in'] = False
            st.rerun()
        else:
            league_data = st.session_state['league_data']
            league = st.session_state['league']

            if st.session_state['metric'] == 'opponent_underperformance':
                luck_indices = get_luck_index_3(league_data)
                luck_indices_df = save_luck_indices_to_file_3(league_data, luck_indices)
                st.dataframe(luck_indices_df)
                plot = plot_luck_indices(luck_indices_df)
                st.pyplot(plot)
            elif st.session_state['metric'] == 'pythagorean_expectation':
                pythagorean_luck_data = calculate_pythagorean_expectation_luck(league_data)
                fig = plot_pythagorean_expectation_luck(pythagorean_luck_data)
                st.pyplot(fig)
            elif st.session_state['metric'] == 'scatterplot_luck':
                scatterplot_luck_df = calculate_scatterplot_luck(league_data)
                team_names = scatterplot_luck_df["Team Name"].unique()
                selected_team = st.selectbox("Select a team to highlight", options=["All Teams"] + list(team_names))
                if selected_team == "All Teams":
                    selected_team = None
                fig = create_scatterplot_luck_figure(scatterplot_luck_df, selected_team)
                st.plotly_chart(fig)
            elif st.session_state['metric'] == 'scheduling_luck':
                scheduling_luck_df = create_scheduling_luck_dataframe(league_data)
                st.dataframe(scheduling_luck_df)

    # Back Button
    if st.button("Back"):
        st.session_state['logged_in'] = False
        st.rerun()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        display_visualizations()
    else:
        log_in()

if __name__ == "__main__":
    main()