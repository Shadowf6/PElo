import consts
from consts import *
from team import *


def calculateChanges(elo: list[int], vol: list[float], red_score: int, blue_score: int, event_type: int, match_type: int) -> list[int]:
    change = [0, 0, 0, 0]

    red_avg = (elo[0] ** 3 + elo[1] ** 3) / max(1, elo[0] ** 2 + elo[1] ** 2)
    blue_avg = (elo[2] ** 3 + elo[3] ** 3) / max(1, elo[2] ** 2 + elo[3] ** 2)

    event_mult = EVENT_TYPES[event_type]
    round_mult = MATCH_TYPES[match_type]
    performance_mult = 1 + abs(red_score - blue_score) / (MAX_SCORE / 2)

    win = event_mult * round_mult * performance_mult * BASE
    loss = (2 - event_mult) * (2 - round_mult) * performance_mult * BASE
    draw = performance_mult * BASE

    if red_score > blue_score:
        change[0] = max(1, int(win * vol[0] * (1 - 1 / (1 + 10 ** ((blue_avg - elo[0]) / ODDS)))))
        change[1] = max(1, int(win * vol[1] * (1 - 1 / (1 + 10 ** ((blue_avg - elo[1]) / ODDS)))))
        change[2] = -max(1, int(loss * vol[2] * (1 / (1 + 10 ** ((red_avg - elo[2]) / ODDS)))))
        change[3] = -max(1, int(loss * vol[3] * (1 / (1 + 10 ** ((red_avg - elo[3]) / ODDS)))))
    elif red_score < blue_score:
        change[0] = -max(1, int(loss * vol[0] * (1 / (1 + 10 ** ((blue_avg - elo[0]) / ODDS)))))
        change[1] = -max(1, int(loss * vol[1] * (1 / (1 + 10 ** ((blue_avg - elo[1]) / ODDS)))))
        change[2] = max(1, int(win * vol[2] * (1 - 1 / (1 + 10 ** ((red_avg - elo[2]) / ODDS)))))
        change[3] = max(1, int(win * vol[3] * (1 - 1 / (1 + 10 ** ((red_avg - elo[3]) / ODDS)))))
    else:
        change[0] = int(draw * vol[0] * (0.5 - 1 / (1 + 10 ** ((blue_avg - elo[0]) / ODDS))))
        change[1] = int(draw * vol[1] * (0.5 - 1 / (1 + 10 ** ((blue_avg - elo[1]) / ODDS))))
        change[2] = int(draw * vol[2] * (0.5 - 1 / (1 + 10 ** ((red_avg - elo[2]) / ODDS))))
        change[3] = int(draw * vol[3] * (0.5 - 1 / (1 + 10 ** ((red_avg - elo[3]) / ODDS))))

    return change


def processMatch(teams: list[str], red_score: int, blue_score: int, event_type: int, match_type: int, match: str, evaluate: bool) -> dict:
    if evaluate:
        for t in teams:
            if t not in consts.active["teams"]:
                consts.active["teams"][t] = 0
                consts.inactive[t] = 2.0
            else:
                consts.active["teams"][t] = 0

        elo = [consts.elos.get(t, DEFAULT_ELO) for t in teams]
        vol = [consts.inactive.get(t, 1.0) for t in teams]
        change = calculateChanges(elo, vol, red_score, blue_score, event_type, match_type)

        for t in teams:
            if t in consts.inactive:
                consts.inactive[t] = max(1.0, consts.inactive[t] - 0.17)

        for i in range(4):
            consts.elos[teams[i]] = max(0, elo[i] + change[i])

        return {
            "Match": match,
            "Matchup": f"{teams[0]} + {teams[1]} vs. {teams[2]} + {teams[3]}",
            "Score": f"{red_score}-{blue_score}",
            "Changes": [f"{teams[i]}{f" ({round(vol[i], 1)}x)" if vol[i] > 1 else ""}: {"+" if change[i] >= 0 else "-"}{abs(change[i])} ({elo[i]} -> {max(0, elo[i] + change[i])})" for i in range(4)]
        }
    else:
        side = ""
        if red_score == 0 and blue_score != 0:
            side = "Red"
        elif red_score != 0 and blue_score == 0:
            side = "Blue"
        elif red_score == 0 and blue_score == 0:
            side = "Double"

        return {
            "Match": match,
            "Matchup": f"{teams[0]} + {teams[1]} vs. {teams[2]} + {teams[3]}",
            "Score": f"{side} DQ"
        }


def simulateMatch(r1: str, r2: str, b1: str, b2: str, red_score: int, blue_score: int):
    teams = [r1, r2, b1, b2]
    elo = [consts.elos.get(t, DEFAULT_ELO) for t in teams]
    change = calculateChanges(elo, [1.0, 1.0, 1.0, 1.0], red_score, blue_score, 1, 2)

    print(f"\nMatch:\n{r1} + {r2} vs. {b1} + {b2}")
    print(f"Score: {red_score} - {blue_score}\n")

    for i in range(4):
        print(f"{teams[i]}: {"+" if change[i] >= 0 else "-"}{abs(change[i])} ({elo[i]} -> {max(0, elo[i] + change[i])})")

    red_avg = (elo[0] ** 3 + elo[1] ** 3) / max(1, elo[0] ** 2 + elo[1] ** 2)
    blue_avg = (elo[2] ** 3 + elo[3] ** 3) / max(1, elo[2] ** 2 + elo[3] ** 2)

    red_prob = 1 / (1 + 10 ** ((blue_avg - red_avg) / ODDS))
    blue_prob = 1 - red_prob

    print(f"\nRed win probability: {round(100 * red_prob, 2)}%")
    print(f"Blue win probability: {round(100 * blue_prob, 2)}%")
