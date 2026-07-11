import consts
from consts import *
from team import *

def calculateChanges(elos: list[int], red_score: int, blue_score: int, event_type: int, match_type: int) -> list[int]:
    change = [0, 0, 0, 0]

    red_avg = (elos[0] ** 3 + elos[1] ** 3) / max(1, elos[0] ** 2 + elos[1] ** 2)
    blue_avg = (elos[2] ** 3 + elos[3] ** 3) / max(1, elos[2] ** 2 + elos[3] ** 2)

    E = EVENT[event_type]
    R = MATCH[match_type]
    P = 1 + abs(red_score - blue_score) / T

    if red_score > blue_score:
        change[0] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((blue_avg - elos[0]) / D)))))
        change[1] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((blue_avg - elos[1]) / D)))))
        change[2] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((red_avg - elos[2]) / D)))))
        change[3] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((red_avg - elos[3]) / D)))))
    elif red_score < blue_score:
        change[0] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((blue_avg - elos[0]) / D)))))
        change[1] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((blue_avg - elos[1]) / D)))))
        change[2] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((red_avg - elos[2]) / D)))))
        change[3] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((red_avg - elos[3]) / D)))))
    else:
        change[0] = round(P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[0]) / D))))
        change[1] = round(P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[1]) / D))))
        change[2] = round(P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[2]) / D))))
        change[3] = round(P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[3]) / D))))

    return change

def processMatch(teams: list[str], red_score: int, blue_score: int, event_type: int, match_type: int) -> None:
    if "Missing" in teams:
        return

    elos = [consts.ELOS.get(t, 1000) for t in teams]

    change = calculateChanges(elos, red_score, blue_score, event_type, match_type)

    for i in range(4):
        consts.ELOS[teams[i]] = max(0, consts.ELOS.get(teams[i], 1000) + change[i])

def simulateMatch(r1: str, r2: str, b1: str, b2: str, red_score: int, blue_score: int) -> None:
    teams = [r1, r2, b1, b2]
    elos = [consts.ELOS.get(t, 1000) for t in teams]
    change = calculateChanges(elos, red_score, blue_score, 1, 2)

    print(f"\nMatch:\n{r1} + {r2} vs. {b1} + {b2}")
    print(f"Score: {red_score} - {blue_score}\n")

    for i in range(4):
        print(f"{teams[i]}: {"+" if change[i] >= 0 else "-"}{abs(change[i])} ({elos[i]} -> {max(0, elos[i] + change[i])})")

    red_avg = (elos[0] ** 3 + elos[1] ** 3) / max(1, elos[0] ** 2 + elos[1] ** 2)
    blue_avg = (elos[2] ** 3 + elos[3] ** 3) / max(1, elos[2] ** 2 + elos[3] ** 2)

    red_prob = 1 / (1 + 10 ** ((blue_avg - red_avg) / D))
    blue_prob = 1 - red_prob

    print(f"\nRed win probability: {round(100 * red_prob, 2)}%")
    print(f"Blue win probability: {round(100 * blue_prob, 2)}%")
