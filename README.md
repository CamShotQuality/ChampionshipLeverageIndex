# ChampionshipLeverageIndex

**What is this?**

This project aims to calculate a Championship Leverage Index(cLI) for each game from a nightly NBA Slate. This is done by running a coin-toss simulation for each game remaining in the season 25k times and calculating the average difference in championship win probability after a win vs after a loss. 

cLI was initially created to quanitfy the importance of each game in the MLB and descriptions can be found below: 
- [Championship Leverage Index](https://www.baseball-reference.com/about/wpa.shtml#:~:text=While%20Leverage%20Index%20(LI)%20measures,of%20winning%20the%20World%20Series.)
- [Championship Win Probability](https://www.sports-reference.com/blog/2020/09/__trashed-2/)

**How Does it Work?**

For each NBA game being played on a given day, we calculate both team's chance of making the playoffs assuming a win and assuming a loss. This percentage is derived from a Monte-Carlo style simulation of 25k coin flips. 

Each percentage difference is then normalized against the marginal difference of a win on opening night. The marginal difference of a win on opening night was determined empirically by running the `baseline_cli.py` file. This value is about 0.85%. 

**How can I run the script?**

To run the script, pull the repository and run the `main()` function from the `cli.py` file. For each game tonight it will print to console:
- Title odds assuming win/loss for Team A
- Title odds assuming win/loss for Team B
- cLI for Team A
- cLI for Team B
- Game cLI

**What exactly does the script do?**

1. Use [basketball_reference_web_scraper](https://pypi.org/project/basketball_reference_web_scraper/) library to get:
   - Current standings
   - Remaining Schedule
2. Loop through each game tonight
   - Calculate title % assuming Team A wins
   - Calculate title % assuming Team A loses
   - Calculate title % assuming Team B wins
   - Calculate title % assuming Team B loses
   - Calculate marginal title % difference for both Teams A and B
3. For each marginal title % difference, normalize against opening night 
4. Print out cLI for each team/game to console

**How do you calculate title % after assuming a win or loss?**

This is done by running a coin-flip simulation 25k times for remaining games and deriving 25k sets of final standings. For each final standing, a title % odd is assigned to each of the 8 seeds based on the methodology outlined below. 

**How do you determine what championship % to assign to each seed?**

The vast majority of NBA titles have been won by [one of the top 3 seeds in either conference](https://www.landofbasketball.com/championships/champions_by_seed.htm)(97.4%). The champion has been a 1 seed in 51/77(66.2%) NBA Finals. Only 2 titles were won by a team with a 4 seed or higher. However, simply assigning championship % to seeds based on historical data would mean that 5, 7 and 8 seeds would have a 0% chance of winning the title (6 seed has won 1 NBA title). Clearly, these seeds do not have a 0% chance of winning the NBA title. Furthermore, the league is deeper and more talented than it has ever been - as evidenced by the Miami Heat (8 seed) making the finals last year. 

Since championship data in the mid-1900's likely isn't as relevant as data from more recent NBA history, we will look at data post NBA-ABA merger (1977 onwards). Championships won by seed post-1977 can be found below: 

- 1st Seed: 30 
- 2nd Seed: 8 
- 3rd Seed: 8 
- 4th Seed: 0 
- 5th Seed: 0 
- 6th Seed: 1 
- 7th Seed: 0 
- 8th Seed: 0 

Since this is such a small dataset, we will also look at finals runner-ups post-merger in an attempt to gain a better understanding of how seed relates to title odds: 
- 1st Seed: 19 
- 2nd Seed: 15 
- 3rd Seed: 5 
- 4th Seed: 4  
- 5th Seed: 1 
- 6th Seed: 1 
- 7th Seed: 0 
- 8th Seed: 2 

This yields the following dataset for finals appearances by seed post-merger: 
- 1st Seed: 49
- 2nd Seed: 23
- 3rd Seed: 13
- 4th Seed: 4  
- 5th Seed: 1 
- 6th Seed: 2 
- 7th Seed: 0 
- 8th Seed: 2 

While lumping finals runner-up appearances together with finals titles may not be a completely fair assumption (seeds 4-8 have collectively won 1 out of the 9 finals they appeared in), this doubles our sample size and still gives us a decent barometer of how likely a team is to win the title based on their seed. 

With a relatively small training data set, we are prone to picking up noise due to random variation that isn't necessarily representative of true championship odds for each seed. In an effort to combat this, Guassian Smoothing was applied to the dataset to reduce noise and generalize to unseen data better.  

**How is the play-in tourney handled?**
Seeds 9 and 10 - 25% playoff chance (8 seed)
9/10 seeds must win 2 games to make the playoffs as the 8 seed. As there is likely not a huge difference in talent level between the 9 and 10 seed - both teams are assigned a 50% chance of winning this game. After winning this game, the 9/10 seed plays the loser of 7/8 matchup for the 8 seed. Assuming there is not a huge difference in talent level between winner of 9/10 and loser of 7/8, we assign a 50% win chance to this game as well. Assuming independence - 50% * 50% yields a 25% chance to make the playoffs. 

Seeds 7 and 8 - 75% playoff chance (50% 7 seed, 25% 8 seed) 
By similar logic as above 

**How does Guassian Smoothing work?**
Guassian Smoothing (aka Gaussian blur) is a technique used to reduce noise in a dataset by averaging values of neighboring data points using a Gaussian distribution. While most commonly used in image recognition software to reduce image noise, it can be applied to reducing the noise in our dataset. 

A Random Forest Regression model was trained on the output of our Gaussian smoothed dataset to assign championship percentages to each seed. 

**Why Random Forest Regression?**
Random forests are particularly effective for smaller datasets because they reduce overfitting (by virtue of the ensembling of many decision trees). Furthermore, overfitting can be mitigated by modifying hyperparameters of the model such as max_depth. In a modern NBA that's deeper with talent than ever before, ensuring we aren't overfitting to prior training data of the past is key. The output of the Random Forest Regression Model can be seen below: 

Championship Percentages for Each Seed:
- 1st Seed: 35.3%
- 2nd Seed: 30.3%
- 3rd Seed: 18.5%
- 4th Seed: 8.6%
- 5th Seed: 3.5%
- 6th Seed: 1.5%
- 7th Seed: 1.1%
- 8th Seed: 1.1%






