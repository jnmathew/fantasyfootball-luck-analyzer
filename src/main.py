from api_client import fetch_league_data
from analysis import calculate_luck_index

import os
import csv
import time
import matplotlib.pyplot as plt
from dotenv import load_dotenv

from espn_api.football import League

# Load environment variables from .env file
load_dotenv()

LEAGUE_ID = os.getenv('LEAGUE_ID')
SWID = os.getenv('SWID')
ESPN_S2 = os.getenv('ESPN_S2')

def generate_luck_index_chart_sorted(league, luck_indices, output_file=None):
    """
    Generate a bar chart for Luck Index directly from the league API, handling missing team IDs dynamically,
    and sorting teams from worst luck to best luck.

    Parameters:
    - league: The league object (e.g., from the ESPN API).
    - luck_indices: List of corresponding luck index values (from get_luck_index_2).
    - output_file: Optional file path to save the chart as an image.
    """
    # Fetch valid teams and their IDs from the league
    teams = [(team.team_id, team.team_name) for team in league.teams]

    # Dynamically filter the luck indices to match the valid team IDs
    filtered_luck_data = []

    for team_id, team_name in teams:
        # Dynamically get the luck index for the valid team_id
        if 0 <= team_id - 1 < len(luck_indices):  # Ensure no out-of-bounds indexing
            filtered_luck_data.append((team_name, luck_indices[team_id - 1]))

    # Sort teams by Luck Index (ascending: worst luck to best luck)
    filtered_luck_data.sort(key=lambda x: x[1])  # Sort by the Luck Index value (second element in tuple)

    # Separate sorted team names and luck indices
    sorted_team_names = [item[0] for item in filtered_luck_data]
    sorted_luck_indices = [item[1] for item in filtered_luck_data]

    # Debugging: Print sorted data
    print(f"Sorted Team Names: {sorted_team_names}")
    print(f"Sorted Luck Indices: {sorted_luck_indices}")

    # Create the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(sorted_team_names, sorted_luck_indices, color=["green" if x > 0 else "red" for x in sorted_luck_indices])
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add a line at 0 for reference
    plt.title("Luck Index by Team (Sorted)", fontsize=16)
    plt.xlabel("Team Name", fontsize=12)
    plt.ylabel("Luck Index (Opponent Underperformance)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Annotate bars with their values
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + (0.2 if yval > 0 else -0.2),
                 f"{yval:.2f}", ha="center", va="bottom" if yval > 0 else "top", fontsize=10)

    # Save the chart to a file if specified
    if output_file:
        plt.savefig(output_file)
        print(f"Chart saved to {output_file}")

    # Show the plot
    plt.show()

def save_luck_indices_to_file_2(league, output_file="luck_indices_2.csv"):
    """
    Calculate and save the luck indices of all teams to a file using the optimized `get_luck_index_2`.
    """
    # Initialize a list to store team luck index data
    team_luck_data = []

    # Calculate the luck indices for all teams using the optimized approach
    luck_indices = get_luck_index_2(league)

    # Iterate over all teams in the league to match luck indices to team names
    for team in league.teams:
        team_id = team.team_id
        team_name = team.team_name

        # Get the corresponding luck index for this team
        luck_index = luck_indices[team_id - 1]  # Adjust for 0-based indexing
        print(f"Team: {team_name}, Luck Index: {luck_index}")

        # Add the result to the list
        team_luck_data.append({
            "Team Name": team_name,
            "Team ID": team_id,
            "Luck Index": luck_index
        })

    # Save results to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Luck Index"])
        writer.writeheader()
        writer.writerows(team_luck_data)

    print(f"Luck indices saved to {output_file}!")

def save_luck_indices_to_file(league, output_file="luck_indices.csv"):
    """
    Calculate and save the luck indices of all teams to a file.
    """
    # Initialize a list to store team luck index data
    team_luck_data = []

    teams = league.teams

    # Iterate over all teams in the league
    for team in teams:
        team_id = team.team_id
        team_name = team.team_name

        # Calculate the team's luck index
        luck_index = get_luck_index(league, team_id)
        print(f"Team: {team_name}, Luck Index: {luck_index}")

        # Add the result to the list
        team_luck_data.append({
            "Team Name": team_name,
            "Team ID": team_id,
            "Luck Index": luck_index
        })

    # Save results to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Luck Index"])
        writer.writeheader()
        writer.writerows(team_luck_data)

    print(f"Luck indices saved to {output_file}!")

def get_luck_index_2(league):
    """
    Calculate how 'lucky' all teams are based on opponent performance.

    Parameters:
    - league: The league object with data on teams and matchups.

    Returns:
    - luck_indices: An array with cumulative luck scores for all teams.
    """
    num_teams = len(league.teams)
    luck_indices = [0] * (num_teams + 1)  # One extra index to handle non-sequential IDs

    # Get the current fantasy week
    current_week = league.current_week

    # Loop through each week up to but excluding the current week
    for week in range(1, current_week):
        box_scores = league.box_scores(week=week)

        # Process each matchup
        for box_score in box_scores:
            # Skip invalid matchups (Bye weeks or incomplete data)
            if not box_score.home_team or not box_score.away_team:
                continue

            # Update luck index for the home team
            home_team_id = box_score.home_team.team_id
            opponent_projected = box_score.away_projected
            opponent_actual = box_score.away_score
            home_luck = opponent_projected - opponent_actual
            if 0 <= home_team_id - 1 < len(luck_indices):
                luck_indices[home_team_id - 1] += home_luck

            # Update luck index for the away team
            away_team_id = box_score.away_team.team_id
            opponent_projected = box_score.home_projected
            opponent_actual = box_score.home_score
            away_luck = opponent_projected - opponent_actual
            if 0 <= away_team_id - 1 < len(luck_indices):
                luck_indices[away_team_id - 1] += away_luck

    return luck_indices

def get_luck_index(league, team_id):
    """
    Calculate how 'unlucky' a team is based on opponent performance.
    """
    # Initialize the luck index
    luck_index = 0

    # Get the current fantasy week
    current_week = league.current_week

    # Loop through each week up to but excluding the current week
    for week in range(1, current_week):
        # Get box scores for the week
        box_scores = league.box_scores(week=week)
        
        # Find the matchup involving your team
        for box_score in box_scores:
            # Check if it's a valid matchup (Bye weeks may have None or 0 for teams)
            if (box_score.home_team == 0 or box_score.away_team == 0):
                continue

            if box_score.home_team.team_id == team_id:
                #opponent = box_score.away_team.team_name
                opponent_score = box_score.away_score
                opponent_projected = box_score.away_projected
            elif box_score.away_team.team_id == team_id:
                #opponent = box_score.home_team.team_name
                opponent_score = box_score.home_score
                opponent_projected = box_score.home_projected
            else:
                continue
            
            # Calculate weekly luck and update the index
            weekly_luck = opponent_projected - opponent_score
            luck_index += weekly_luck
            #print(f"Week {week}: Opponent {opponent} Actual = {opponent_score}, Projected = {opponent_projected}, Weekly Luck = {weekly_luck}")
            break

    return luck_index

def calculate_pythagorean_expectation_luck(league, p=2):
    """
    Calculate Pythagorean Expectation Luck for all teams, with normalization.

    Parameters:
    - league: The league object with data on teams and matchups.
    - p: The exponent for the Pythagorean formula (default=2).

    Returns:
    - List of dictionaries with Team Name, Team ID, Actual Wins, Expected Wins, and Luck Score.
    """
    team_luck_data = []
    current_week = league.current_week
    games_played = current_week - 1  # Games completed so far

    print("Debugging Pythagorean Expectation Luck Calculation:\n")
    total_actual_wins = 0
    total_expected_wins = 0

    for team in league.teams:
        points_for = team.points_for
        points_against = team.points_against
        actual_wins = team.wins

        # Calculate expected win percentage
        expected_win_percentage = (points_for ** p) / ((points_for ** p) + (points_against ** p))

        # Adjust expected wins based on games played so far
        expected_wins = expected_win_percentage * games_played

        # Track totals for normalization
        total_actual_wins += actual_wins
        total_expected_wins += expected_wins

        # Add preliminary team data to the results
        team_luck_data.append({
            "Team Name": team.team_name,
            "Team ID": team.team_id,
            "Actual Wins": actual_wins,
            "Expected Wins": expected_wins,  # To be normalized
            "Luck Index": None  # Placeholder for now
        })

    # Calculate scaling factor for normalization
    scaling_factor = total_actual_wins / total_expected_wins
    print(f"\nScaling Factor for Normalization: {scaling_factor:.4f}\n")

    # Normalize expected wins and calculate final luck index
    for team in team_luck_data:
        normalized_expected_wins = team["Expected Wins"] * scaling_factor
        team["Expected Wins"] = round(normalized_expected_wins, 2)
        team["Luck Index"] = round(team["Actual Wins"] - normalized_expected_wins, 2)

    # Debug: Print league-wide totals
    print("League-Wide Totals After Normalization:")
    print(f"  Total Actual Wins: {total_actual_wins}")
    print(f"  Total Expected Wins: {sum(t['Expected Wins'] for t in team_luck_data):.2f}")
    print(f"  Difference (should be ~0): {total_actual_wins - sum(t['Expected Wins'] for t in team_luck_data):.2f}\n")

    return team_luck_data



def save_and_visualize_pythagorean_luck(pythagorean_luck_data, output_file="pythagorean_luck.csv", image_file="pythagorean_luck_chart.png"):
    """
    Save and visualize Pythagorean Expectation Luck for all teams, sorted by Luck Index from least lucky to most lucky.

    Parameters:
    - pythagorean_luck_data: List of dictionaries with Pythagorean Luck data.
    - output_file: The file where results will be saved (default="pythagorean_luck.csv").
    - image_file: The file where the visualization will be saved (default="pythagorean_luck_chart.png").
    """
    import csv
    import matplotlib.pyplot as plt

    # Sort by Luck Index (ascending: least lucky to most lucky)
    pythagorean_luck_data_sorted = sorted(pythagorean_luck_data, key=lambda x: x["Luck Index"])

    # Save results to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Actual Wins", "Expected Wins", "Luck Index"])
        writer.writeheader()
        writer.writerows(pythagorean_luck_data_sorted)

    print(f"Pythagorean Expectation Luck saved to {output_file}!")

    # Visualization
    team_names = [t["Team Name"] for t in pythagorean_luck_data_sorted]
    luck_scores = [t["Luck Index"] for t in pythagorean_luck_data_sorted]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(team_names, luck_scores, color=["red" if x < 0 else "green" for x in luck_scores])
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.title("Pythagorean Expectation Luck by Team (Sorted)", fontsize=16)
    plt.xlabel("Team Name", fontsize=12)
    plt.ylabel("Luck Index (Actual Wins - Expected Wins)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Annotate bars with luck scores
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + (0.2 if yval > 0 else -0.2),
                 f"{yval:.2f}", ha="center", va="bottom" if yval > 0 else "top", fontsize=10)

    # Save the plot to a file
    plt.savefig(image_file, dpi=300)
    print(f"Pythagorean Expectation Luck visualization saved to {image_file}!")

    # Show the plot
    plt.show()


def calculate_scatterplot_luck(league):
    """
    Calculate matchup-based scatterplot luck for all teams.

    Parameters:
    - league: The league object with data on teams and matchups.

    Returns:
    - List of dictionaries with Team Name, Points For, Points Against, Result, and Matchup Luck Type.
    """
    matchup_luck_data = []

    # Calculate league averages
    total_points_for = sum([team.points_for for team in league.teams])
    total_points_against = sum([team.points_against for team in league.teams])
    num_teams = len(league.teams)
    league_avg_points_for = total_points_for / num_teams
    league_avg_points_against = total_points_against / num_teams

    # Iterate through weeks and matchups
    current_week = league.current_week
    for week in range(1, current_week):
        box_scores = league.box_scores(week=week)

        for box_score in box_scores:
            if not box_score.home_team or not box_score.away_team:
                continue

            # Process Home Team
            home_team = box_score.home_team
            matchup_luck_data.append({
                "Team Name": home_team.team_name,
                "Points For": box_score.home_score - league_avg_points_for,
                "Points Against": box_score.away_score - league_avg_points_against,
                "Result": "Win" if box_score.home_score > box_score.away_score else "Loss",
                "Matchup Luck Type": "Lucky Win" if box_score.home_score < box_score.away_score else "Unlucky Loss"
            })

            # Process Away Team
            away_team = box_score.away_team
            matchup_luck_data.append({
                "Team Name": away_team.team_name,
                "Points For": box_score.away_score - league_avg_points_for,
                "Points Against": box_score.home_score - league_avg_points_against,
                "Result": "Win" if box_score.away_score > box_score.home_score else "Loss",
                "Matchup Luck Type": "Lucky Win" if box_score.away_score < box_score.home_score else "Unlucky Loss"
            })

    return matchup_luck_data

def time_comparison(league):
    # Time the original function
    print("Timing save_luck_indices_to_file...")
    start_time = time.time()
    save_luck_indices_to_file(league)
    end_time = time.time()
    original_time = end_time - start_time
    print(f"save_luck_indices_to_file runtime: {original_time:.2f} seconds")

    print("\nTiming save_luck_indices_to_file_2...")
    # Time the optimized function
    start_time = time.time()
    save_luck_indices_to_file_2(league)
    end_time = time.time()
    optimized_time = end_time - start_time
    print(f"save_luck_indices_to_file_2 runtime: {optimized_time:.2f} seconds")

    # Compare the two runtimes
    print("\nComparison of runtimes:")
    print(f"Original function runtime: {original_time:.2f} seconds")
    print(f"Optimized function runtime: {optimized_time:.2f} seconds")
    print(f"Performance improvement: {((original_time - optimized_time) / original_time) * 100:.2f}% faster")

def main():
    #league_id = input("Enter your League ID: ")
    #swid = input("Enter your SWID cookie: ")
    #espn_s2 = input("Enter your ESPN_S2 cookie: ")
    #team_id = input("Enter your Team ID: ")
    
    league = League(league_id=LEAGUE_ID,year=2024,espn_s2=ESPN_S2,swid=SWID)

    # Step 1: Calculate Pythagorean Luck
    #pythagorean_luck_data = calculate_pythagorean_expectation_luck(league)

    # Step 2: Save and visualize
    #save_and_visualize_pythagorean_luck(pythagorean_luck_data, output_file="pythagorean_luck.csv")

    #time_comparison(league)

    #luck_indices = get_luck_index_2(league)

    #total_luck = sum(luck_indices)
    #print(f"Total Luck Index Across League: {total_luck}")

    #generate_luck_index_chart_sorted(league, luck_indices, output_file="luck_index_chart.png")

    pythagorean_luck_data = calculate_pythagorean_expectation_luck(league)
    save_and_visualize_pythagorean_luck(pythagorean_luck_data)

if __name__ == "__main__":
    main()