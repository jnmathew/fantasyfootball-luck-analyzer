from api_client import fetch_league_views, fetch_league_data
from analysis import get_luck_index, get_luck_index_2, get_luck_index_3, get_luck_index_4, calculate_pythagorean_expectation_luck, \
simulate_hypothetical_records
from visualization import generate_luck_index_chart_sorted, load_data, plot_luck_indices, \
save_luck_indices_to_file_2, save_luck_indices_to_file_3, save_and_visualize_pythagorean_luck, create_scheduling_luck_dataframe
from archive import time_comparison

import os
import json
import csv
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from espn_api.football import League

# Load environment variables from .env file
load_dotenv()

LEAGUE_ID = os.getenv('LEAGUE_ID')
SWID = os.getenv('SWID')
ESPN_S2 = os.getenv('ESPN_S2')


def main():

    league = League(league_id=LEAGUE_ID,year=2024,espn_s2=ESPN_S2,swid=SWID)

    #league_data = fetch_league_views(LEAGUE_ID, SWID, ESPN_S2)

    league_data = fetch_league_data(league)
    #print(league_data)

    # Approach 1: Pythagorean Luck
    #pythagorean_luck_data = calculate_pythagorean_expectation_luck(league)
    #save_and_visualize_pythagorean_luck(pythagorean_luck_data, output_file="pythagorean_luck.csv")

    # Approach 2: Luck Index
    # luck_indices = get_luck_index_2(league)

    ## Approach 1: Load data and plot luck indices
    # Load data
    #data = load_data("out/luck_indices_2.csv")

    # Plot luck indices
    #plot_luck_indices(data, output_file="luck_index_chart_v11.png")
    '''
    ## Approach 2: Using optimized function
    luck_indices_v1 = get_luck_index_2(league)
    print(luck_indices_v1)

    
    settings = fetch_league_views(LEAGUE_ID, SWID, ESPN_S2, view="mSettings")
    luck_indices_v2 = get_luck_index_3(league_data, settings)
    print(luck_indices_v2)
    save_luck_indices_to_file_3(league, luck_indices_v2, output_file="luck_indices_3.csv")

    plot_luck_indices("luck_indices_3.csv", output_file="luck_index_chart_v12.png")
    '''
    #generate_luck_index_chart_sorted(league, luck_indices, output_file="luck_index_chart_v2.png")

    #total_luck = sum(luck_indices)
    #print(f"Total Luck Index Across League: {total_luck}")

    #generate_luck_index_chart_sorted(league, luck_indices, output_file="luck_index_chart.png")

    #pythagorean_luck_data = calculate_pythagorean_expectation_luck(league)
    #save_and_visualize_pythagorean_luck(pythagorean_luck_data)

    # Simulate hypothetical records
    hypothetical_records = simulate_hypothetical_records(league_data)
    print(hypothetical_records)

    # Example usage: Create scheduling luck DataFrame
    scheduling_luck_df = create_scheduling_luck_dataframe(league_data)
    print(scheduling_luck_df)


if __name__ == "__main__":
    main()