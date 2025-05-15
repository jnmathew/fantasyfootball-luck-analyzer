# === Archived legacy versions for benchmarking ===
# v1: single-team perspective, used for early manual testing
# v2: full-team dictionary, unoptimized API calls

import csv
import matplotlib.pyplot as plt

def get_luck_index_v1(league, team_id, regular_season_weeks=14):

    """
    Calculate how 'unlucky' a team is based on opponent performance.
    """
    # Initialize the luck index
    luck_index = 0

    # Get the current fantasy week
    current_week = league.current_week

    # Loop through each week
    for week in range(1, min(league.current_week + 1, regular_season_weeks + 1)):
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
            break

    return luck_index

def save_luck_indices_to_file_v1(league, output_file=None):
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
        luck_index = get_luck_index_v1(league, team_id)

        # Add the result to the list
        team_luck_data.append({
            "Team Name": team_name,
            "Team ID": team_id,
            "Luck Index": luck_index
        })

    if output_file:
        # Save results to a CSV file
        with open(output_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Luck Index"])
            writer.writeheader()
            writer.writerows(team_luck_data)

        print(f"Luck indices saved to {output_file}!")

def get_luck_index_v2(league, regular_season_weeks=14):
    """
    Calculate how 'lucky' all teams are based on opponent performance.

    Parameters:
    - league: The league object with data on teams and matchups.

    Returns:
    - luck_indices: An array with cumulative luck scores for all teams.
    """
    luck_indices = {}

    # Initialize each team's luck to 0
    for team in league.teams:
        luck_indices[team.team_id] = 0

    for week in range(1, min(league.current_week + 1, regular_season_weeks + 1)):
        box_scores = league.box_scores(week=week)

        for box_score in box_scores:
            if not box_score.home_team or not box_score.away_team:
                continue

            home_id = box_score.home_team.team_id
            away_id = box_score.away_team.team_id

            home_luck = box_score.away_projected - box_score.away_score
            away_luck = box_score.home_projected - box_score.home_score

            if home_id in luck_indices:
                luck_indices[home_id] += home_luck
            if away_id in luck_indices:
                luck_indices[away_id] += away_luck

    return luck_indices

def save_luck_indices_to_file_v2(league, output_file=None):
    """
    Calculate and save the luck indices of all teams to a file using the optimized `get_luck_index_v2`.
    """
    luck_indices = get_luck_index_v2(league)
    team_luck_data = []

    for team in league.teams:
        team_id = team.team_id
        team_name = team.team_name
        luck_index = luck_indices.get(team_id, 0)

        team_luck_data.append({
            "Team Name": team_name,
            "Team ID": team_id,
            "Luck Index": luck_index
        })

    if output_file:
        with open(output_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Luck Index"])
            writer.writeheader()
            writer.writerows(team_luck_data)
        print(f"Luck indices saved to {output_file}!")

def save_and_visualize_pythagorean_luck(pythagorean_luck_data, output_file=None, image_file=None):
    """
    Save and visualize Pythagorean Expectation Luck for all teams, sorted by Luck Index from least lucky to most lucky.

    Parameters:
    - pythagorean_luck_data: List of dictionaries with Pythagorean Luck data.
    - output_file: The file where results will be saved (default=None).
    - image_file: The file where the visualization will be saved (default=None).
    """

    # Sort by Luck Index (ascending: least lucky to most lucky)
    pythagorean_luck_data_sorted = sorted(pythagorean_luck_data, key=lambda x: x["Luck Index"])

    # Save results to a CSV file
    if output_file:
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
    if image_file:
        plt.savefig(image_file, dpi=300)
        print(f"Pythagorean Expectation Luck visualization saved to {image_file}!")

    # Show the plot
    plt.show()
