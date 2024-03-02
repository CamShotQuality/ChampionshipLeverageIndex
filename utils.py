from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
import json
from datetime import datetime
import pytz
import random

from constants import OPENING_NIGHT_CLI, SIMULATION_COUNT, CONF_SEED_CHAMPIONSHIP_ODDS, EAST_TEAMS


# helper functions that rely on upstream dependency basketball_reference_web_scraper library
def get_current_standings_dicts():
    standings_json = client.standings(season_end_year=2024, output_type=OutputType.JSON)
    data = json.loads(standings_json)

    east_standings = {}
    west_standings = {}

    for entry in data:
        team_name = entry["team"]
        wins = entry["wins"]
        losses = entry["losses"]
        conference = entry["conference"]

        if conference == "EASTERN":
            east_standings[team_name] = (wins, losses)
        else:
            west_standings[team_name] = (wins, losses)

    sorted_east_standings = dict(sorted(east_standings.items(), key=lambda item: item[1][0], reverse=True))
    sorted_west_standings = dict(sorted(west_standings.items(), key=lambda item: item[1][0], reverse=True))

    return sorted_east_standings, sorted_west_standings


def get_rest_of_season_schedule():
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])

    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()

    games_today_dict = [entry for entry in nba_schedule if
                        datetime.strptime(entry['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() == today]
    games_today_list = parse_teams(games_today_dict)

    games_to_simulate_dict = [game for game in nba_schedule if
                              game['away_team_score'] is None and datetime.strptime(game['start_time'],
                                                                                    '%Y-%m-%dT%H:%M:%S%z').date() != today]
    games_to_simulate_list = parse_teams(games_to_simulate_dict)

    return games_today_list, games_to_simulate_list


def get_schedule_today():
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    # Update start_time values in the list to be EST
    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])
    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()

    games_today_dict = [entry for entry in nba_schedule if
                        datetime.strptime(entry['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() == today]
    games_today_list = parse_teams(games_today_dict)

    return games_today_list


def get_beginning_of_season_schedule():
    # first 15 games include all 30 teams, treat as if it were one day v
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])

    # each of first 15 games this year contain unique teams (30 in total)
    # ref: https: // www.basketball - reference.com / leagues / NBA_2024_games.html
    first_fifteen_games_dict = nba_schedule[:15]
    remaining_games_dict = nba_schedule[15:]

    first_fifteen_games_list = parse_teams(first_fifteen_games_dict)
    remaining_games_list = parse_teams(remaining_games_dict)

    return first_fifteen_games_list, remaining_games_list



def get_whole_season_schedule():
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])

    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()

    games_today_dict = [entry for entry in nba_schedule if
                        datetime.strptime(entry['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() == today]
    games_today_list = parse_teams(games_today_dict)

    games_to_simulate_dict = [game for game in nba_schedule if
                              datetime.strptime(game['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() != today]
    games_to_simulate_list = parse_teams(games_to_simulate_dict)

    return games_today_list, games_to_simulate_list


def convert_utc_to_est(utc_time):
    est = pytz.timezone('US/Eastern')
    utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S%z')
    est_datetime = utc_datetime.astimezone(est)
    return est_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')


# helper functions related to calculating expected championship probability
def update_standings(east_sim_standings, west_sim_standings, team_name, win_flag):
    if team_name in EAST_TEAMS:
        curr_standings = east_sim_standings[team_name]
        if win_flag:
            east_sim_standings[team_name] = (curr_standings[0] + 1, curr_standings[1])
        else:
            east_sim_standings[team_name] = (curr_standings[0], curr_standings[1] + 1)
        final_standings_dict = dict(sorted(east_sim_standings.items(), key=lambda item: item[1][0], reverse=True))
    else:
        curr_standings = west_sim_standings[team_name]
        if win_flag:
            west_sim_standings[team_name] = (curr_standings[0] + 1, curr_standings[1])
        else:
            west_sim_standings[team_name] = (curr_standings[0], curr_standings[1] + 1)
        final_standings_dict = dict(sorted(west_sim_standings.items(), key=lambda item: item[1][0], reverse=True))

    return final_standings_dict


def get_team_seed(final_standings_dict, team_name):
    final_teams_order = list(final_standings_dict.keys())
    # + 1 to acct for 0-indexed
    team_seed = str(final_teams_order.index(team_name) + 1)

    return team_seed


# gets expected NBA title percent based on seed
def get_title_pct_from_seed(final_standings_dict, team_name):
    final_teams_order = list(final_standings_dict.keys())
    team_seed = get_team_seed(final_standings_dict, team_name)

    if team_name in list(final_teams_order)[:6]:
        return CONF_SEED_CHAMPIONSHIP_ODDS.get(team_seed)
    # play-in specific logic!!!
    elif team_name in list(final_teams_order)[:8]:
        return 0.5 * CONF_SEED_CHAMPIONSHIP_ODDS.get('7') + 0.25 * CONF_SEED_CHAMPIONSHIP_ODDS.get('8')
    elif team_name in list(final_teams_order)[:10]:
        return 0.25 * CONF_SEED_CHAMPIONSHIP_ODDS.get('8')
    else:
        return 0


def get_title_count(east_sim_standings, west_sim_standings, team_name, win_flag=True):
    final_standings_dict = update_standings(east_sim_standings, west_sim_standings, team_name, win_flag)

    return get_title_pct_from_seed(final_standings_dict, team_name)


def get_simulated_final_standings(standings_dict, teams, simulated_game_winners_list, cli_game) -> dict:
    simulated_final_standings_dict = {}

    for team in teams:
        simulated_wins_count = simulated_game_winners_list.count(team)
        curr_wins_losses = standings_dict.get(team)

        if team in cli_game:
            total_games = 81
        else:
            total_games = 82

        simulated_losses_count = total_games - (curr_wins_losses[0] + curr_wins_losses[1] + simulated_wins_count)
        simulated_wins_losses = (
            curr_wins_losses[0] + simulated_wins_count, curr_wins_losses[1] + simulated_losses_count)

        simulated_final_standings_dict[team] = simulated_wins_losses

    return simulated_final_standings_dict


def parse_teams(games) -> list:
    return [[game['home_team'], game['away_team']] for game in games]


# takes in a list of lists representing remaining games -> chooses one team from each sublist at random (50-50)
def coin_toss_simulate(remaining_games):
    return [random.choice(game) for game in remaining_games]


# for data integrity purposes in case basketball_reference_web_scraper upstream dependency returns invalid data
def assert_wins_match_losses(first_dict, second_dict):
    total_wins = sum(value[0] for value in first_dict.values()) + sum(value[0] for value in second_dict.values())
    total_losses = sum(value[1] for value in first_dict.values()) + sum(value[1] for value in second_dict.values())
    assert total_wins == total_losses, 'Total wins do not equal total losses!'


# helper functions for printing out to console
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

    print('The average playoff swing percentage for an opening night game is: ' + str(
        avg_playoff_swing_pct_opening_night))


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

