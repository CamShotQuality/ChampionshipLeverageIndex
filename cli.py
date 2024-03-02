import time

from constants import EAST_TEAMS, SIMULATION_COUNT, WEST_TEAMS
from utils import get_current_standings_dicts, coin_toss_simulate, \
    print_title_percentages, print_cli_stats, get_simulated_final_standings, get_title_count, \
    get_rest_of_season_schedule


def main():
    games_today, games_after_today = get_rest_of_season_schedule()

    title_team_prob_diff_dict = {}
    title_game_prob_diff_dict = {}

    for cli_game in games_today:
        print('We are going to calculate importance of ' + str(cli_game))
        start_time = time.time()  # Start time logging

        east_standings_dict, west_standings_dict = get_current_standings_dicts()

        # Data validity check of upstream dependency (basketball_reference_web_scraper)
        # commented out to reduce script runtime
        # assert_wins_match_losses(east_standings_dict, west_standings_dict)

        # Remove current game from games_today
        games_today_without_cli = [game for game in games_today if game != cli_game]

        # represents list of games to simulate (every remaining game in season except cli_game)
        games_to_simulate = games_after_today + games_today_without_cli

        assume_first_team_wins_title_count = 0
        assume_first_team_loses_title_count = 0

        assume_second_team_wins_title_count = 0
        assume_second_team_loses_title_count = 0

        for _ in range(0, SIMULATION_COUNT):
            simulated_game_winners_list = coin_toss_simulate(games_to_simulate)

            east_simulated_standings_dict = get_simulated_final_standings(east_standings_dict.copy(), EAST_TEAMS,
                                                                          simulated_game_winners_list, cli_game)
            west_simulated_standings_dict = get_simulated_final_standings(west_standings_dict.copy(), WEST_TEAMS,
                                                                          simulated_game_winners_list, cli_game)

            # VALIDITY CHECK - commented out to reduce script runtime
            # assert_wins_match_losses(east_simulated_standings_dict, west_simulated_standings_dict)

            # add expected title count to cumulative counter
            assume_first_team_wins_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                                  west_simulated_standings_dict.copy(), cli_game[0])
            assume_first_team_loses_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                                   west_simulated_standings_dict.copy(), cli_game[0],
                                                                   False)

            assume_second_team_wins_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                                   west_simulated_standings_dict.copy(), cli_game[1])
            assume_second_team_loses_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                                    west_simulated_standings_dict.copy(), cli_game[1],
                                                                    False)

        first_team_title_prob_diff, second_team_title_prob_diff = print_title_percentages(cli_game,
                                                                                          assume_first_team_wins_title_count,
                                                                                          assume_first_team_loses_title_count,
                                                                                          assume_second_team_wins_title_count,
                                                                                          assume_second_team_loses_title_count)

        # add title margins to team dict
        title_team_prob_diff_dict[cli_game[0]] = round(first_team_title_prob_diff, 2)
        title_team_prob_diff_dict[cli_game[1]] = round(second_team_title_prob_diff, 2)

        # add title margins to game dict
        title_game_prob_diff_dict[cli_game[0] + ' vs. ' + cli_game[1]] = round(first_team_title_prob_diff, 2) + round(
            second_team_title_prob_diff, 2)
        end_time = time.time()  # End time logging

        print(f"Time taken for processing this game: {end_time - start_time:.2f} seconds")
        print()

    print_cli_stats(title_team_prob_diff_dict, title_game_prob_diff_dict)


if __name__ == '__main__':
    main()
