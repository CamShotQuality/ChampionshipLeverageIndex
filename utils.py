from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
import json
from datetime import datetime
import pytz


# returns a dictionary representing the current standings of the NBA
def get_standings_dicts():
    standings_json = client.standings(season_end_year=2024, output_type=OutputType.JSON)
    data = json.loads(standings_json)

    east_standings = {}
    west_standings = {}

    for entry in data:
        team_name = entry["team"]
        wins = entry["wins"]
        losses = entry["losses"]
        conference = entry["conference"]

        if (conference == "EASTERN"):
            east_standings[team_name] = (wins, losses)
        else:
            west_standings[team_name] = (wins, losses)

    sorted_east_standings = dict(sorted(east_standings.items(), key=lambda item: item[1][0], reverse=True))
    sorted_west_standings = dict(sorted(west_standings.items(), key=lambda item: item[1][0], reverse=True))

    return sorted_east_standings, sorted_west_standings


# return a list of today's games
def get_schedule_today():
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    # Update start_time values in the list to be EST
    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])
    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()

    games_today_dict = [entry for entry in nba_schedule if datetime.strptime(entry['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() == today]
    games_today_list = parse_teams(games_today_dict)

    return games_today_list


# Function to convert UTC to EST
def convert_utc_to_est(utc_time):
    est = pytz.timezone('US/Eastern')
    utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S%z')
    est_datetime = utc_datetime.astimezone(est)
    return est_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')


# Function to parse the list of dictionaries
def parse_teams(games):
    teams_list = []
    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        teams_list.append([home_team, away_team])
    return teams_list


# returns a dictionary representing the current standings of the NBA
def get_opening_standings_dicts():
    standings_json = client.standings(season_end_year=2024, output_type=OutputType.JSON)
    data = json.loads(standings_json)

    east_standings = {}
    west_standings = {}

    for entry in data:
        team_name = entry["team"]
        wins = entry["wins"]
        losses = entry["losses"]
        conference = entry["conference"]

        if (conference == "EASTERN"):
            east_standings[team_name] = (0, 0)
        else:
            west_standings[team_name] = (0, 0)

    return east_standings, west_standings
