# PElo
### By V5RC Team 355P PowerHouse

---
### Description
PElo is an elo rating system for the VEX V5 game. The only data processed for elo calculations is match data and the teams' elos.

Teams start at 1000 elo, and gain/lose elo per win/loss/tie. Multipliers affecting elo gain/loss are the opposing team's elo, the score dominance, the level of the event, and the round of the match.

The basic algorithm is inspired by the chess elo system, which a logistic probability model on predicted outcomes between two players. The algorithm had to be modified for a 2-on-2 format, which uses a weighted average (which favors higher elos) as the "second" elo and the first elo being calculated for each individual team in the alliance.

### ELO IS NOT AN OBJECTIVE MEASURE OF SKILL, IT IS ONLY A METRIC!
This also reflects in the fact that a team that goes to more competitions will on average improve more.

---
## Changelog
### Release v1

3/7/2026: Added RobotEvents API getters for teams

3/8/2026: Added RobotEvents API getters for events

3/9/2026: Finished elo calculation formula

3/10/2026: Updated elos from beginning of season to 11/16/2025

3/11/2026: Updated elos from 11/17/2025 to 12/31/2025

3/12/2026: Implemented rate-limit handling to bulk-process events
<br>
Updated elos from 1/1/2026 to 3/8/26

3/16/2026: Updated elos from 3/9/26 to 3/15/26
<br>

### Release v1.1

3/16/2026: Lowered base elo from 40 to 30
<br>
Changed method of calculating performance factor
