import requests
import streamlit as st
import pandas as pd

#@st.cache_data
def fetch_league_views(league_id, swid, espn_s2, view=None):
    """
    Fetch league views from the ESPN API.
    """
    season_id = '2024'
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season_id}/segments/0/leagues/{league_id}?view={view}"
    
    cookies = {
        'SWID': swid,
        'espn_s2': espn_s2
    }
    
    response = requests.get(url, cookies=cookies)
    
    if response.status_code == 200:
        return response.json()  # Return league data as a Python dictionary
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

def fetch_league_data(league):
    """
    Fetch all necessary league data once and store it for reuse.
    """
    data = {
        "teams": [{"id": team.team_id, "name": team.team_name, "wins": team.wins, "losses": team.losses, "points_for": team.points_for, "points_against": team.points_against} for team in league.teams],
        "current_week": league.current_week,
        "regular_season_count": league.settings.reg_season_count,
        "box_scores": {}
    }

    # Fetch box scores for each week up to the end of the regular season
    for week in range(1, data["regular_season_count"] + 1):
        try:
            print(f"Fetching box scores for week {week}")
            box_scores = league.box_scores(week=week)
            data["box_scores"][week] = []
            for box_score in box_scores:
                # Handle bye weeks where the team is set as the integer 0
                if isinstance(box_score.home_team, int) and box_score.home_team == 0:
                    continue
                if isinstance(box_score.away_team, int) and box_score.away_team == 0:
                    continue

                data["box_scores"][week].append({
                    "home_team_id": box_score.home_team.team_id,
                    "home_score": box_score.home_score,
                    "home_projected": box_score.home_projected,
                    "away_team_id": box_score.away_team.team_id,
                    "away_score": box_score.away_score,
                    "away_projected": box_score.away_projected
                })
            print(f"Fetched box scores for week {week}")
        except Exception as e:
            print(f"Error fetching box scores for week {week}: {e}")
            data["box_scores"][week] = None

    return data