from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
import json
from datetime import datetime
import pytz
import random


# returns a dictionary representing the current standings of the NBA
from constants import OPENING_NIGHT_CLI, SIMULATION_COUNT


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
        conference = entry["conference"]

        if (conference == "EASTERN"):
            east_standings[team_name] = (0, 0)
        else:
            west_standings[team_name] = (0, 0)

    return east_standings, west_standings


def assert_wins_match_losses(first_dict, second_dict):
    total_wins = sum(value[0] for value in first_dict.values()) + sum(value[0] for value in second_dict.values())
    total_losses = sum(value[1] for value in first_dict.values()) + sum(value[1] for value in second_dict.values())
    assert total_wins == total_losses, 'Total wins do not equal total losses!'


def get_whole_season_schedule():
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])

    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()

    games_today_dict = [entry for entry in nba_schedule if datetime.strptime(entry['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() == today]
    games_today_list = parse_teams(games_today_dict)

    games_to_simulate_dict = [game for game in nba_schedule if datetime.strptime(game['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() != today]
    games_to_simulate_list = parse_teams(games_to_simulate_dict)

    return games_today_list, games_to_simulate_list


def parse_teams(games) -> list:
    return [[game['home_team'], game['away_team']] for game in games]


def simulate_remaining_games(remaining_games):
    return [random.choice(game) for game in remaining_games]


def print_title_percentages(cli_game, first_team_wins_title_count, first_team_loses_title_count,
                            second_team_wins_title_count, second_team_loses_title_count):
    first_team_win_title_prob = round(100 * (first_team_wins_title_count / SIMULATION_COUNT), 2)
    first_team_loss_title_prob = round(100 * (first_team_loses_title_count / SIMULATION_COUNT), 2)
    first_team_title_prob_diff = first_team_win_title_prob - first_team_loss_title_prob

    second_team_win_title_prob = round(100 * (second_team_wins_title_count / SIMULATION_COUNT), 2)
    second_team_loss_title_prob = round(100 * (second_team_loses_title_count / SIMULATION_COUNT), 2)
    second_team_title_prob_diff = second_team_win_title_prob - second_team_loss_title_prob

    print(f"Assuming a win, the {cli_game[0]} would win the title: {first_team_win_title_prob:.2f}% of the time")
    print(f"Assuming a loss, the {cli_game[0]} would win the title: {first_team_loss_title_prob:.2f}% of the time")
    print(f"Assuming a win, the {cli_game[1]} would win the title: {second_team_win_title_prob:.2f}% of the time")
    print(f"Assuming a loss, the {cli_game[1]} would win the title: {second_team_loss_title_prob:.2f}% of the time")

    return first_team_title_prob_diff, second_team_title_prob_diff


def print_opening_night_swing_pct(title_team_prob_diff_dict):
    sorted_playoff_team_prob_diff_dict = dict(
        sorted(title_team_prob_diff_dict.items(), key=lambda item: item[1], reverse=True))

    opening_day_playoff_swing_pct_list = []
    for k, v in sorted_playoff_team_prob_diff_dict.items():
        print(f'{k} has a playoff swing percentage of {v}% tonight')
        opening_day_playoff_swing_pct_list.append(v)

    avg_playoff_swing_pct_opening_night = sum(opening_day_playoff_swing_pct_list) / len(
        opening_day_playoff_swing_pct_list)

    print('The average playoff swing percentage for an opening night game is: ' + str(avg_playoff_swing_pct_opening_night))

    return avg_playoff_swing_pct_opening_night


def print_cli_stats(title_team_prob_diff_dict, title_game_prob_diff_dict):
    sorted_playoff_team_prob_diff_dict = dict(
        sorted(title_team_prob_diff_dict.items(), key=lambda item: item[1], reverse=True))
    sorted_playoff_game_prob_diff_dict = dict(
        sorted(title_game_prob_diff_dict.items(), key=lambda item: item[1], reverse=True))

    print('Teams with highest cLI tonight: ')
    for k, v in sorted_playoff_team_prob_diff_dict.items():
        print(f'The {k} have a cLI of {round(v / OPENING_NIGHT_CLI, 2)} tonight')

    print('\nGames with highest cLI: ')
    for k, v in sorted_playoff_game_prob_diff_dict.items():
        print(f'{k} has cLI: {round(v / (2 * OPENING_NIGHT_CLI), 2)} tonight')