import time

from championship_leverage_index.core.constants import EAST_TEAMS, SIMULATION_COUNT, WEST_TEAMS, EAST_OPENING_STANDINGS, \
    WEST_OPENING_STANDINGS
from championship_leverage_index.core.utils import coin_toss_simulate, \
    print_title_percentages, print_opening_night_swing_pct, get_simulated_final_standings, get_title_count, \
    get_beginning_of_season_schedule


def main():
    # get first fifteen games (each containing unique team)
    first_fifteen_games, remaining_games = get_beginning_of_season_schedule()

    title_team_prob_diff_dict = {}

    for cli_game in first_fifteen_games:
        start_time = time.time()  # Start time logging
        print('We are simulating for ' + str(cli_game))

        # VALIDITY CHECK - commented out for runtime purposes
        # assert_wins_match_losses(east_standings_dict, west_standings_dict)

        # Remove cli_game from games_today
        games_today_without_cli = [game for game in first_fifteen_games if game != cli_game]
        # Concatenate games_today without cli_game with games_after_today
        games_to_simulate = remaining_games + games_today_without_cli

        first_team_wins_title_count = 0
        first_team_loses_title_count = 0

        second_team_wins_title_count = 0
        second_team_loses_title_count = 0

        for _ in range(0, SIMULATION_COUNT):
            simulated_game_winners_list = coin_toss_simulate(games_to_simulate)

            east_simulated_standings_dict = get_simulated_final_standings(EAST_OPENING_STANDINGS.copy(), EAST_TEAMS,
                                                                          simulated_game_winners_list, cli_game)
            west_simulated_standings_dict = get_simulated_final_standings(WEST_OPENING_STANDINGS.copy(), WEST_TEAMS,
                                                                          simulated_game_winners_list, cli_game)

            # VALIDITY CHECK
            # assert_wins_match_losses(east_simulated_standings_dict, west_simulated_standings_dict)

            first_team_wins_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                           west_simulated_standings_dict.copy(),
                                                           cli_game[0])
            first_team_loses_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                            west_simulated_standings_dict.copy(), cli_game[0],
                                                            False)

            second_team_wins_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                            west_simulated_standings_dict.copy(),
                                                            cli_game[1])
            second_team_loses_title_count += get_title_count(east_simulated_standings_dict.copy(),
                                                             west_simulated_standings_dict.copy(),
                                                             cli_game[1],
                                                             False)

        first_team_title_prob_diff, second_team_title_prob_diff = print_title_percentages(cli_game,
                                                                                          first_team_wins_title_count,
                                                                                          first_team_loses_title_count,
                                                                                          second_team_wins_title_count,
                                                                                          second_team_loses_title_count)

        title_team_prob_diff_dict[cli_game[0]] = round(first_team_title_prob_diff, 2)
        title_team_prob_diff_dict[cli_game[1]] = round(second_team_title_prob_diff, 2)

    print_opening_night_swing_pct(title_team_prob_diff_dict)


if __name__ == '__main__':
    main()
