import random
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
import json
from datetime import datetime
import pytz
import time

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


def win_playoff_count(east_sim_standings, west_sim_standings, team_name) -> float:
    if team_name in EAST_TEAMS:
        curr_standings = east_sim_standings[team_name]
        east_sim_standings[team_name] = (curr_standings[0] + 1, curr_standings[1])
        final_east_standings_dict = dict(sorted(east_sim_standings.items(), key=lambda item: item[1][0], reverse=True))

        if team_name in list(final_east_standings_dict.keys())[:6]:
            return 1
        elif team_name in list(final_east_standings_dict.keys())[:8]:
            return 0.75
        elif team_name in list(final_east_standings_dict.keys())[:10]:
            return 0.25
        else:
            return 0
    else:
        curr_standings = west_sim_standings[team_name]
        west_sim_standings[team_name] = (curr_standings[0] + 1, curr_standings[1])
        final_west_standings_dict = dict(sorted(west_sim_standings.items(), key=lambda item: item[1][0], reverse=True))

        if team_name in list(final_west_standings_dict.keys())[:6]:
            return 1
        elif team_name in list(final_west_standings_dict.keys())[:8]:
            return 0.75
        elif team_name in list(final_west_standings_dict.keys())[:10]:
            return 0.25
        else:
            return 0


def loss_playoff_count(east_sim_standings, west_sim_standings, team_name):
    if team_name in EAST_TEAMS:
        curr_standings = east_sim_standings[team_name]
        east_sim_standings[team_name] = (curr_standings[0], curr_standings[1] + 1)
        final_east_standings_dict = dict(sorted(east_sim_standings.items(), key=lambda item: item[1][0], reverse=True))

        if team_name in list(final_east_standings_dict.keys())[:6]:
            return 1
        elif team_name in list(final_east_standings_dict.keys())[:8]:
            return 0.75
        elif team_name in list(final_east_standings_dict.keys())[:10]:
            return 0.25
        else:
            return 0
    else:
        curr_standings = west_sim_standings[team_name]
        west_sim_standings[team_name] = (curr_standings[0], curr_standings[1] + 1)
        final_west_standings_dict = dict(sorted(west_sim_standings.items(), key=lambda item: item[1][0], reverse=True))

        if team_name in list(final_west_standings_dict.keys())[:6]:
            return 1
        elif team_name in list(final_west_standings_dict.keys())[:8]:
            return 0.75
        elif team_name in list(final_west_standings_dict.keys())[:10]:
            return 0.25
        else:
            return 0


def main():
    games_today, games_after_today = get_rest_of_season_schedule()

    playoff_prob_diff_dict = {}

    for cli_game in games_today:
        print('We are going to calculate importance of ' + str(cli_game))
        start_time = time.time()  # Start time logging

        east_standings_dict, west_standings_dict = get_standings_dicts()
        assert_wins_match_losses(east_standings_dict, west_standings_dict)

        # Remove cli_game from games_today
        games_today_without_cli = [game for game in games_today if game != cli_game]
        # Concatenate games_today without cli_game with games_after_today
        games_to_simulate = games_after_today + games_today_without_cli

        assume_first_team_wins_playoff_count = 0
        assume_first_team_loses_playoff_count = 0

        assume_second_team_wins_playoff_count = 0
        assume_second_team_loses_playoff_count = 0

        for _ in range(0, SIMULATION_COUNT):
            simulated_game_winners_list = simulate_remaining_games(games_to_simulate)

            east_simulated_standings_dict = get_simulated_final_standings(east_standings_dict.copy(), EAST_TEAMS, simulated_game_winners_list, cli_game)
            west_simulated_standings_dict = get_simulated_final_standings(west_standings_dict.copy(), WEST_TEAMS, simulated_game_winners_list, cli_game)

            # takes a lot of time
            # assert_wins_match_losses(east_simulated_standings_dict, west_simulated_standings_dict)

            assume_first_team_wins_playoff_count += win_playoff_count(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[0])
            assume_first_team_loses_playoff_count += loss_playoff_count(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[0])

            assume_second_team_wins_playoff_count += win_playoff_count(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[1])
            assume_second_team_loses_playoff_count += loss_playoff_count(east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[1])

        first_team_win_playoff_prob = round(100 * (assume_first_team_wins_playoff_count / SIMULATION_COUNT), 2)
        first_team_loss_playoff_prob = round(100 * (assume_first_team_loses_playoff_count / SIMULATION_COUNT), 2)
        first_team_playoff_prob_diff = first_team_win_playoff_prob - first_team_loss_playoff_prob

        second_team_win_playoff_prob = round(100 * (assume_second_team_wins_playoff_count / SIMULATION_COUNT), 2)
        second_team_loss_playoff_prob = round(100 * (assume_second_team_loses_playoff_count / SIMULATION_COUNT), 2)
        second_team_playoff_prob_diff = second_team_win_playoff_prob - second_team_loss_playoff_prob

        # add playoff margins to dictionary
        playoff_prob_diff_dict[cli_game[0]] = round(first_team_playoff_prob_diff, 2)
        playoff_prob_diff_dict[cli_game[1]] = round(second_team_playoff_prob_diff, 2)

        print(f"Assuming a win, the {cli_game[0]} would make the playoffs: {first_team_win_playoff_prob:.2f}% of the time")
        print(f"Assuming a loss, the {cli_game[0]} would make the playoffs: {first_team_loss_playoff_prob:.2f}% of the time")
        print(f"Assuming a win, the {cli_game[1]} would make the playoffs: {second_team_win_playoff_prob:.2f}% of the time")
        print(f"Assuming a loss, the {cli_game[1]} would make the playoffs: {second_team_loss_playoff_prob:.2f}% of the time")
        end_time = time.time()  # End time logging

        print(f"Time taken for processing: {end_time - start_time:.2f} seconds")
        print()

    sorted_playoff_prob_diff_dict = dict(sorted(playoff_prob_diff_dict.items(), key=lambda item: item[1], reverse=True))
    for k, v in sorted_playoff_prob_diff_dict.items():
        print(f'{k} has a playoff swing percentage of {v}% tonight')


if __name__ == '__main__':
    main()
