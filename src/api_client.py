import requests

def fetch_league_data(league_id, swid, espn_s2):
    """
    Fetch league data from the ESPN API.
    """
    season_id = '2024'
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season_id}/segments/0/leagues/{league_id}"
    
    cookies = {
        'SWID': swid,
        'espn_s2': espn_s2
    }
    
    response = requests.get(url, cookies=cookies)
    
    if response.status_code == 200:
        return response.json()  # Return league data as a Python dictionary
    else:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")