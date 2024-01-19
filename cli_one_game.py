import random
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
import json
from datetime import datetime
import pytz

from utils import convert_utc_to_est, get_standings_dicts

# Constants
EAST_TEAMS = ['BOSTON CELTICS', 'PHILADELPHIA 76ERS', 'NEW YORK KNICKS', 'BROOKLYN NETS', 'TORONTO RAPTORS',
              'MILWAUKEE BUCKS', 'INDIANA PACERS', 'CLEVELAND CAVALIERS', 'CHICAGO BULLS', 'DETROIT PISTONS',
              'MIAMI HEAT', 'ORLANDO MAGIC', 'ATLANTA HAWKS', 'CHARLOTTE HORNETS', 'WASHINGTON WIZARDS']
WEST_TEAMS = ['MINNESOTA TIMBERWOLVES', 'OKLAHOMA CITY THUNDER', 'DENVER NUGGETS', 'UTAH JAZZ',
              'PORTLAND TRAIL BLAZERS', 'LOS ANGELES CLIPPERS', 'SACRAMENTO KINGS', 'PHOENIX SUNS',
              'LOS ANGELES LAKERS', 'GOLDEN STATE WARRIORS', 'NEW ORLEANS PELICANS', 'DALLAS MAVERICKS',
              'HOUSTON ROCKETS', 'MEMPHIS GRIZZLIES', 'SAN ANTONIO SPURS']
SIMULATION_COUNT = 25000


def get_rest_of_season_schedule():
    schedule_json = client.season_schedule(season_end_year=2024, output_type=OutputType.JSON)
    nba_schedule = json.loads(schedule_json)

    for game in nba_schedule:
        game['start_time'] = convert_utc_to_est(game['start_time'])

    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()

    games_today_dict = [entry for entry in nba_schedule if datetime.strptime(entry['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() == today]
    games_today_list = parse_teams(games_today_dict)

    games_to_simulate_dict = [game for game in nba_schedule if game['away_team_score'] is None and datetime.strptime(game['start_time'], '%Y-%m-%dT%H:%M:%S%z').date() != today]
    games_to_simulate_list = parse_teams(games_to_simulate_dict)

    return games_today_list, games_to_simulate_list


def parse_teams(games) -> list:
    return [[game['home_team'], game['away_team']] for game in games]


def simulate_remaining_games(remaining_games):
    return [random.choice(game) for game in remaining_games]


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
        simulated_wins_losses = (curr_wins_losses[0] + simulated_wins_count, curr_wins_losses[1] + simulated_losses_count)

        simulated_final_standings_dict[team] = simulated_wins_losses

    return simulated_final_standings_dict


def assert_wins_match_losses(first_dict, second_dict):
    total_wins = sum(value[0] for value in first_dict.values()) + sum(value[0] for value in second_dict.values())
    total_losses = sum(value[1] for value in first_dict.values()) + sum(value[1] for value in second_dict.values())
    assert total_wins == total_losses, 'Total wins do not equal total losses!'


def win_does_team_make_playoffs(east_sim_standings, west_sim_standings, team_name) -> bool:
    if team_name in EAST_TEAMS:
        curr_standings = east_sim_standings[team_name]
        east_sim_standings[team_name] = (curr_standings[0] + 1, curr_standings[1])
        final_east_standings_dict = dict(sorted(east_sim_standings.items(), key=lambda item: item[1][0], reverse=True))
        return team_name in list(final_east_standings_dict.keys())[:8]
    else:
        curr_standings = west_sim_standings[team_name]
        west_sim_standings[team_name] = (curr_standings[0] + 1, curr_standings[1])
        final_west_standings_dict = dict(sorted(west_sim_standings.items(), key=lambda item: item[1][0], reverse=True))
        return team_name in list(final_west_standings_dict.keys())[:8]


def loss_does_team_make_playoffs(east_sim_standings, west_sim_standings, team_name):
    if team_name in EAST_TEAMS:
        curr_standings = east_sim_standings[team_name]
        east_sim_standings[team_name] = (curr_standings[0], curr_standings[1] + 1)
        final_east_standings_dict = dict(sorted(east_sim_standings.items(), key=lambda item: item[1][0], reverse=True))
        return team_name in list(final_east_standings_dict.keys())[:8]
    else:
        curr_standings = west_sim_standings[team_name]
        west_sim_standings[team_name] = (curr_standings[0], curr_standings[1] + 1)
        final_west_standings_dict = dict(sorted(west_sim_standings.items(), key=lambda item: item[1][0], reverse=True))
        return team_name in list(final_west_standings_dict.keys())[:8]


def main():
    games_today, games_after_today = get_rest_of_season_schedule()
    cli_game = games_today[0]
    print('We are going to calculate importance of :' + str(cli_game))

    east_standings_dict, west_standings_dict = get_standings_dicts()
    assert_wins_match_losses(east_standings_dict, west_standings_dict)

    games_to_simulate = games_after_today + games_today[1:]
    simulated_game_winners_list = simulate_remaining_games(games_to_simulate)

    east_simulated_standings_dict = get_simulated_final_standings(east_standings_dict.copy(), EAST_TEAMS, simulated_game_winners_list, cli_game)
    west_simulated_standings_dict = get_simulated_final_standings(west_standings_dict.copy(), WEST_TEAMS, simulated_game_winners_list, cli_game)

    # assert_wins_match_losses(east_simulated_standings_dict, west_simulated_standings_dict)

    # todo: update these to be counter variables
    first_team_win_make_playoffs_bool = win_does_team_make_playoffs(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[0])
    first_team_lose_make_playoffs_bool = loss_does_team_make_playoffs(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[0])

    second_team_win_make_playoffs_bool = win_does_team_make_playoffs(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[1])
    second_team_lose_make_playoffs_bool = loss_does_team_make_playoffs(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[1])

    print('Assuming a win, the ' + cli_game[0] + " would make the playoffs: " + str(first_team_win_make_playoffs_bool))
    print('Assuming a loss, the ' + cli_game[0] + " would make the playoffs: " + str(first_team_lose_make_playoffs_bool))

    print('Assuming a win, the ' + cli_game[1] + " would make the playoffs: " + str(second_team_win_make_playoffs_bool))
    print('Assuming a loss, the ' + cli_game[1] + " would make the playoffs: " + str(second_team_lose_make_playoffs_bool))

    # todo: simulate this 25000 times and return difference in above counter variables


if __name__ == '__main__':
    main()
