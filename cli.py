import time

from constants import EAST_TEAMS, SIMULATION_COUNT, WEST_TEAMS
from utils import (
    get_current_standings_dicts, coin_toss_simulate, print_title_percentages,
    print_cli_stats, get_simulated_final_standings, get_title_count,
    get_rest_of_season_schedule, assert_wins_match_losses
)


# simulates remaining games, updates current standings and derives title odds
def simulate_game(cli_game, games_after_today, games_today_without_cli):
    east_standings_dict, west_standings_dict = get_current_standings_dicts()

    games_to_simulate = games_after_today + games_today_without_cli

    # counters
    assume_first_team_wins_title_count = 0
    assume_first_team_loses_title_count = 0
    assume_second_team_wins_title_count = 0
    assume_second_team_loses_title_count = 0

    for _ in range(0, SIMULATION_COUNT):
        # coin toss simulate rest of season
        simulated_game_winners_list = coin_toss_simulate(games_to_simulate)

        # add coin toss sim results to current standings
        east_simulated_standings_dict = get_simulated_final_standings(
            east_standings_dict.copy(), EAST_TEAMS, simulated_game_winners_list, cli_game)
        west_simulated_standings_dict = get_simulated_final_standings(
            west_standings_dict.copy(), WEST_TEAMS, simulated_game_winners_list, cli_game)

        # VALIDITY CHECK - commented out for script runtime purposes
        # assert_wins_match_losses(east_simulated_standings_dict, west_simulated_standings_dict)

        # update expected title counters
        assume_first_team_wins_title_count += get_title_count(
            east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[0])
        assume_first_team_loses_title_count += get_title_count(
            east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[0], False)

        assume_second_team_wins_title_count += get_title_count(
            east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[1])
        assume_second_team_loses_title_count += get_title_count(
            east_simulated_standings_dict.copy(), west_simulated_standings_dict.copy(), cli_game[1], False)

    return (
        assume_first_team_wins_title_count, assume_first_team_loses_title_count,
        assume_second_team_wins_title_count, assume_second_team_loses_title_count
    )


def process_games(games_today, games_after_today):
    title_team_prob_diff_dict = {}
    title_game_prob_diff_dict = {}

    # loop through each game today
    for cli_game in games_today:
        print('We are going to calculate cLI of ' + str(cli_game))

        # for logging of script runtime purposes
        start_time = time.time()

        games_today_without_cli = [game for game in games_today if game != cli_game]

        # simulate remaining games
        (
            assume_first_team_wins_title_count, assume_first_team_loses_title_count,
            assume_second_team_wins_title_count, assume_second_team_loses_title_count
        ) = simulate_game(cli_game, games_after_today, games_today_without_cli)

        # print title percentages to console
        first_team_title_prob_diff, second_team_title_prob_diff = print_title_percentages(
            cli_game, assume_first_team_wins_title_count, assume_first_team_loses_title_count,
            assume_second_team_wins_title_count, assume_second_team_loses_title_count
        )

        title_team_prob_diff_dict[cli_game[0]] = round(first_team_title_prob_diff, 2)
        title_team_prob_diff_dict[cli_game[1]] = round(second_team_title_prob_diff, 2)

        title_game_prob_diff_dict[cli_game[0] + ' vs. ' + cli_game[1]] = (
            round(first_team_title_prob_diff, 2) + round(second_team_title_prob_diff, 2)
        )

        end_time = time.time()
        print(f"Time taken for processing this game: {end_time - start_time:.2f} seconds")
        print()

    # print cLI to console
    print_cli_stats(title_team_prob_diff_dict, title_game_prob_diff_dict)


def main():
    games_today, games_after_today = get_rest_of_season_schedule()
    process_games(games_today, games_after_today)


if __name__ == '__main__':
    main()
