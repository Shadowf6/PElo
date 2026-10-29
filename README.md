# PElo
### By V5RC Team 355P PowerHouse

---
### Description
PElo is an elo rating system for the VEX V5 game. The only data processed for elo calculations is match data and the teams' elos.

Teams start at 1000 elo, and gain/lose elo per win/loss/tie. Multipliers affecting elo gain/loss are the opposing team's elo, the score dominance, the level of the event, and the round of the match.

The basic algorithm is inspired by the chess elo system, which a logistic probability model that predicts outcomes between two parties. The algorithm had to be modified for a 2-on-2 format, which uses a weighted average (favoring higher elos) as the "opponent's" elo and the first elo being calculated for each individual team in the alliance.

#### ELO IS NOT AN OBJECTIVE MEASURE OF SKILL, IT IS ONLY A METRIC!
This also reflects in the fact that a team that goes to more competitions will on average improve more.

A more recent addition was a system to track long stretches of time between competitions. A team with ample time to rebuild will likely not be representative of their previous elo, so they are given a decaying multiplier that boosts elo gains/losses for one tournament.