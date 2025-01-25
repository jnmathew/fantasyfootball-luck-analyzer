from api_client import fetch_league_views, fetch_league_data
import pandas as pd

def calculate_luck_index(league_data, team_id):
    """
    Calculate how 'unlucky' a team is based on opponent performance.
    """
    # Extract schedule from league_data
    matchups = league_data.get('schedule', [])
    if not matchups:
        print(f"No matchups found in league data for team {team_id}.")
        return 0

    luck_score = 0
    matchups_processed = 0

    # Iterate through each matchup
    for matchup in matchups:
        if matchup['home']['teamId'] == team_id:
            # Team is the home team
            opponent_score = matchup['away'].get('totalPoints', 0)
            opponent_proj = matchup['away'].get('pointsProjected', 0)
            matchups_processed += 1
            print(f"Home Opponent: Actual = {opponent_score}, Projected = {opponent_proj}")
        elif matchup['away']['teamId'] == team_id:
            # Team is the away team
            opponent_score = matchup['home'].get('totalPoints', 0)
            opponent_proj = matchup['home'].get('pointsProjected', 0)
            matchups_processed += 1
            print(f"Away Opponent: Actual = {opponent_score}, Projected = {opponent_proj}")
        else:
            # Skip matchups that don't involve this team
            continue

        # Calculate overperformance for the matchup
        luck_score += (opponent_score - opponent_proj)

    # Debugging outputs
    print(f"Matchups Processed for Team {team_id}: {matchups_processed}")
    print(f"Luck Score for Team {team_id}: {luck_score}")
    
    # Return the calculated Luck Index
    return luck_score

def get_luck_index_4(league_data):
    # Number of teams in the league
    num_teams = league_data['status']['teamsJoined']
    luck_indices = [0] * (num_teams + 1)  # One extra index to handle non-sequential IDs

    # Loop through each matchup in the schedule
    for matchup in league_data['schedule']:
        home_team = matchup.get('home', {})
        away_team = matchup.get('away', {})

        # Skip invalid matchups (e.g., bye weeks or incomplete data)
        if not home_team or not away_team:
            continue

        # Update luck index for the home team
        home_team_id = home_team.get('teamId')
        away_projected = away_team.get('pointsByScoringPeriod', {}).get(str(matchup['matchupPeriodId']), 0)
        away_actual = away_team.get('totalPoints', 0)
        home_luck = away_projected - away_actual
        if home_team_id is not None and 0 <= home_team_id <= num_teams:
            luck_indices[home_team_id] += home_luck

        # Update luck index for the away team
        away_team_id = away_team.get('teamId')
        home_projected = home_team.get('pointsByScoringPeriod', {}).get(str(matchup['matchupPeriodId']), 0)
        home_actual = home_team.get('totalPoints', 0)
        away_luck = home_projected - home_actual
        if away_team_id is not None and 0 <= away_team_id <= num_teams:
            luck_indices[away_team_id] += away_luck

    return luck_indices

def get_luck_index_3(league_data):
    num_teams = len(league_data['teams'])
    luck_indices = [0] * (num_teams + 5)  # add arbitrary buffer for non-sequential IDs, in case of missing teams

    # Get the current fantasy week
    current_week = league_data['current_week']

    # Loop through each regular season week
    for week in range(1, min(current_week, league_data['regular_season_count'] + 1)):
        box_scores = league_data['box_scores'][week]

        # Process each matchup
        for box_score in box_scores:
            # Skip invalid matchups (Bye weeks or incomplete data)
            if box_score['away_team_id'] == 0 or box_score['home_team_id'] == 0:
                continue

            # Update luck index for the home team
            home_team_id = box_score['home_team_id']
            home_luck = box_score['away_projected'] - box_score['away_score']
            if 0 <= home_team_id < len(luck_indices):
                luck_indices[home_team_id] += home_luck

            # Update luck index for the away team
            away_team_id = box_score['away_team_id']
            away_luck = box_score['home_projected'] - box_score['home_score']
            if 0 <= away_team_id < len(luck_indices):
                luck_indices[away_team_id] += away_luck

    return luck_indices

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

def calculate_pythagorean_expectation_luck(league_data, p=2):
    """
    Calculate Pythagorean Expectation Luck for all teams, with normalization.

    Parameters:
    - league_data: The dictionary with data on teams and matchups.
    - p: The exponent for the Pythagorean formula (default=2).

    Returns:
    - List of dictionaries with Team Name, Team ID, Actual Wins, Expected Wins, and Luck Score.
    """
    team_luck_data = []
    current_week = league_data['current_week']
    games_played = min(current_week - 1, league_data['regular_season_count'])  # Games completed so far

    total_actual_wins = 0
    total_expected_wins = 0

    teams = league_data['teams']

    for team in teams:
        points_for = team['points_for']
        points_against = team['points_against']
        actual_wins = team['wins']

        # Calculate expected win percentage
        expected_win_percentage = (points_for ** p) / ((points_for ** p) + (points_against ** p))

        # Adjust expected wins based on games played so far
        expected_wins = expected_win_percentage * games_played

        # Track totals for normalization
        total_actual_wins += actual_wins
        total_expected_wins += expected_wins

        # Add preliminary team data to the results
        team_luck_data.append({
            "Team Name": team['name'],
            "Team ID": team['id'],
            "Actual Wins": actual_wins,
            "Expected Wins": expected_wins,  # To be normalized
            "Luck Index": None  # Placeholder for now
        })

    # Calculate scaling factor for normalization
    scaling_factor = total_actual_wins / total_expected_wins

    # Normalize expected wins and calculate final luck index
    for team in team_luck_data:
        normalized_expected_wins = team["Expected Wins"] * scaling_factor
        team["Expected Wins"] = round(normalized_expected_wins, 2)
        team["Luck Index"] = round(team["Actual Wins"] - normalized_expected_wins, 2)

    return team_luck_data

def calculate_scatterplot_luck(league_data):
    """
    Calculate matchup-based scatterplot luck for all teams.

    Parameters:
    - league_data: The dictionary with data on teams and matchups.

    Returns:
    - Pandas DataFrame with Team Name, Points For, Points Against, Result, Matchup Luck Type, and Opponent.
    """
    matchup_luck_data = []

    # Preprocess teams for quick lookups
    team_id_to_team = {team["id"]: team for team in league_data["teams"]}

    # Calculate weekly league averages
    weekly_avg_scores = {}
    current_week = league_data['current_week']
    regular_season_count = league_data['regular_season_count']

    for week in range(1, min(current_week, regular_season_count + 1)):
        box_scores = league_data['box_scores'].get(week, [])
        if not box_scores:
            continue

        total_weekly_score = sum(box_score['home_score'] + box_score['away_score'] for box_score in box_scores)
        num_teams = len(box_scores) * 2  # Each matchup involves two teams
        weekly_avg_scores[week] = total_weekly_score / num_teams

    # Iterate through weeks and matchups
    for week in range(1, min(current_week, regular_season_count + 1)):
        box_scores = league_data['box_scores'].get(week, [])  # Safely get box scores for the week
        league_avg_score = weekly_avg_scores.get(week, 0)

        for box_score in box_scores:
            # Skip invalid matchups
            if box_score.get('home_team_id') == 0 or box_score.get('away_team_id') == 0:
                continue

            # Extract match info
            home_score = box_score['home_score']
            away_score = box_score['away_score']
            home_team = team_id_to_team[box_score['home_team_id']]
            away_team = team_id_to_team[box_score['away_team_id']]

            # Normalize scores by league average for Home Team
            home_points_for = home_score - league_avg_score
            home_points_against = away_score - league_avg_score
            home_result = "Win" if home_score > away_score else "Loss"
            home_luck_type = (
                "Lucky Win" if home_result == "Win" and home_points_for < 0 else
                "Unlucky Loss" if home_result == "Loss" and home_points_for > 0 else
                "Neutral"
            )

            matchup_luck_data.append({
                "Week": week,
                "Team Name": home_team["name"],
                "Points For": home_points_for,
                "Points Against": home_points_against,
                "Result": home_result,
                "Matchup Luck Type": home_luck_type,
                "Opponent": away_team["name"]
            })

            # Normalize scores by league average for Away Team
            away_points_for = away_score - league_avg_score
            away_points_against = home_score - league_avg_score
            away_result = "Win" if away_score > home_score else "Loss"
            away_luck_type = (
                "Lucky Win" if away_result == "Win" and away_points_for < 0 else
                "Unlucky Loss" if away_result == "Loss" and away_points_for > 0 else
                "Neutral"
            )

            matchup_luck_data.append({
                "Week": week,
                "Team Name": away_team["name"],
                "Points For": away_points_for,
                "Points Against": away_points_against,
                "Result": away_result,
                "Matchup Luck Type": away_luck_type,
                "Opponent": home_team["name"]
            })

    # Convert the list to a DataFrame
    df = pd.DataFrame(matchup_luck_data)

    return df

def calculate_actual_records(league):
    records = {team.team_id: {'wins': team.wins, 'losses': team.losses} for team in league.teams}
    return records

def simulate_hypothetical_records(league_data):
    hypothetical_records = {team['id']: {opponent['id']: {'wins': 0, 'losses': 0} for opponent in league_data['teams']} for team in league_data['teams']}

    for team in league_data['teams']:
        team_id = team['id']
        team_scores = []

        for week in range(1, min(league_data['current_week'], league_data['regular_season_count'] + 1)):
            box_scores = league_data['box_scores'][week]

            for box_score in box_scores:
                if box_score['home_team_id'] == 0 or box_score['away_team_id'] == 0:
                    continue

                if box_score['home_team_id'] == team_id:
                    team_scores.append(box_score['home_score'])
                elif box_score['away_team_id'] == team_id:
                    team_scores.append(box_score['away_score'])

        for opponent_team in league_data['teams']:
            opponent_id = opponent_team['id']
            if opponent_id == team_id:
                hypothetical_records[team_id][opponent_id]['wins'] = team['wins']
                hypothetical_records[team_id][opponent_id]['losses'] = team['losses']
                continue

            opponent_id = opponent_team['id']
            opponent_scores = []

            for week in range(1, min(league_data['current_week'], league_data['regular_season_count'] + 1)):
                box_scores = league_data['box_scores'][week]

                for box_score in box_scores:
                    if box_score['home_team_id'] == 0 or box_score['away_team_id'] == 0:
                        continue

                    if box_score['home_team_id'] == opponent_id:
                        opponent_scores.append(box_score['home_score'])
                    elif box_score['away_team_id'] == opponent_id:
                        opponent_scores.append(box_score['away_score'])

            wins = sum(1 for ts, os in zip(team_scores, opponent_scores) if ts > os)
            losses = len(team_scores) - wins

            hypothetical_records[team_id][opponent_id]['wins'] = wins
            hypothetical_records[team_id][opponent_id]['losses'] = losses

    return hypothetical_records