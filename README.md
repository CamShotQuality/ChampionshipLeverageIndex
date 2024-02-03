# ChampionshipLeverageIndex
This project calculates a Championship Leverage Index(cLI) for each game from a nightly NBA Slate. This is done by running a coin-toss simulation for each game remaining in the season 25k times and calculating the average difference in championship win probability after a win vs after a loss. 

cLI was created to quanitfy the importance of each game in the MLB and descriptions can be found below: 
- https://www.baseball-reference.com/about/wpa.shtml#:~:text=While%20Leverage%20Index%20(LI)%20measures,of%20winning%20the%20World%20Series.
- https://www.sports-reference.com/blog/2020/09/__trashed-2/

How Does it Work?
For each NBA game being played tonight, we calculate each team's chance of making the playoffs assuming a win tonight and assuming a loss. The difference between these two probabilities is then normalized to an average of 1.0 by dividing by 7.7% - the marginal difference in playoff probability for an opening night game.

Where does the 7.7% come from? To normalize cLI such that the average game has a cLI of 1.00, we run an opening night simulation to determine the effect an opening night game has on a team's championship win percentage. After simulating this value 25k times, the average value was found to be ~7.7%. This means that on average, a team winning a game on opening night will have about a 7.7% greater chance of making the playoffs than a team that loses its opening game. 

How is the play-in tourney handled?
Seeds 9 and 10 - 25% playoff chance
9/10 seeds must win 2 games to make the playoffs as the 8 seed. As there is likely not a huge difference in talent level between the 9 and 10 seed - both teams are assigned a 50% chance of winning this game. After winning this game, the 9/10 seed plays the loser of 7/8 matchup for the 8 seed. Assuming there is not a huge difference in talent level between winner of 9/10 and loser of 7/8, we assign a 50% win chance to this game as well. Assuming independence - 50% * 50% yields a 25% chance to make the playoffs. 

Seeds 7 and 8 - 75% playoff chance
By similar logic as above

How do you determine what championship % to assign to each seed?
[Good question]
