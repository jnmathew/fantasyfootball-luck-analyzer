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
