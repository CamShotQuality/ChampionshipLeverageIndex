import time

from constants import EAST_TEAMS, CONF_SEED_CHAMPIONSHIP_ODDS, OPENING_NIGHT_EVERY_TEAM, SIMULATION_COUNT, WEST_TEAMS
from utils import get_opening_standings_dicts, get_whole_season_schedule, simulate_remaining_games, \
    print_title_percentages, print_opening_night_swing_pct


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


def get_title_count(east_sim_standings, west_sim_standings, team_name, win_flag=True):
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

    teams_order = list(final_standings_dict.keys())

    # + 1 to acct for 0-indexed list
    team_seed = str(teams_order.index(team_name) + 1)

    if team_name in list(teams_order)[:6]:
        return CONF_SEED_CHAMPIONSHIP_ODDS.get(team_seed)
    elif team_name in list(teams_order)[:8]:
        return 0.5 * CONF_SEED_CHAMPIONSHIP_ODDS.get('7') + 0.25 * CONF_SEED_CHAMPIONSHIP_ODDS.get('8')
    elif team_name in list(teams_order)[:10]:
        return 0.25 * CONF_SEED_CHAMPIONSHIP_ODDS.get('8')
    else:
        return 0


def main():
    games_today, games_after_today = get_whole_season_schedule()

    title_team_prob_diff_dict = {}

    east_standings_dict, west_standings_dict = get_opening_standings_dicts()

    for cli_game in OPENING_NIGHT_EVERY_TEAM:
        start_time = time.time()  # Start time logging

        # VALIDITY CHECK - commented out to reduce script runtime
        # assert_wins_match_losses(east_standings_dict, west_standings_dict)

        # Remove cli_game from games_today
        games_today_without_cli = [game for game in OPENING_NIGHT_EVERY_TEAM if game != cli_game]
        # Concatenate games_today without cli_game with games_after_today
        games_to_simulate = games_after_today + games_today_without_cli

        first_team_wins_title_count = 0
        first_team_loses_title_count = 0

        second_team_wins_title_count = 0
        second_team_loses_title_count = 0

        for _ in range(0, SIMULATION_COUNT):
            simulated_game_winners_list = simulate_remaining_games(games_to_simulate)

            east_simulated_standings_dict = get_simulated_final_standings(east_standings_dict.copy(), EAST_TEAMS,
                                                                          simulated_game_winners_list, cli_game)
            west_simulated_standings_dict = get_simulated_final_standings(west_standings_dict.copy(), WEST_TEAMS,
                                                                          simulated_game_winners_list, cli_game)

            # VALIDITY CHECK - commented out to reduce script runtime
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

        end_time = time.time()  # End time logging
        print(f"Time taken for processing this game: {end_time - start_time:.2f} seconds\n")

    avg_playoff_swing_pct_opening_night = print_opening_night_swing_pct(title_team_prob_diff_dict)


if __name__ == '__main__':
    main()
