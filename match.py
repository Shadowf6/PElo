import consts
from consts import *
from team import *

def processMatch(teams: list[str], diff: int, event_type: int, match_type: int) -> None:
    if "Missing" in teams:
        return

    elos = [consts.TEAMS.get(t, 1000) for t in teams]
    change = [0, 0, 0, 0]

    red_total = max(1, elos[0] + elos[1])
    blue_total = max(1, elos[2] + elos[3])

    red_avg = elos[0] / red_total * elos[0] + elos[1] / red_total * elos[1]
    blue_avg = elos[2] / blue_total * elos[2] + elos[3] / blue_total * elos[3]

    E = EVENT[event_type]  # event type
    R = MATCH[match_type]  # match round
    P = 1 + abs(diff) / T  # performance bonus

    if diff > 0:
        change[0] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((blue_avg - elos[0]) / D)))))
        change[1] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((blue_avg - elos[1]) / D)))))
        change[2] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((red_avg - elos[2]) / D)))))
        change[3] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((red_avg - elos[3]) / D)))))
    elif diff < 0:
        change[0] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((blue_avg - elos[0]) / D)))))
        change[1] = -max(1, int((2 - E) * (2 - R) * P * B * (1 / (1 + 10 ** ((blue_avg - elos[1]) / D)))))
        change[2] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((red_avg - elos[2]) / D)))))
        change[3] = max(1, int(E * R * P * B * (1 - 1 / (1 + 10 ** ((red_avg - elos[3]) / D)))))
    else:
        change[0] = int(E * R * P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[0]) / D))))
        change[1] = int(E * R * P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[1]) / D))))
        change[2] = int(E * R * P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[2]) / D))))
        change[3] = int(E * R * P * B * (0.5 - 1 / (1 + 10 ** ((blue_avg - elos[3]) / D))))

    for i in range(4):
        consts.TEAMS[teams[i]] = max(0, consts.TEAMS.get(teams[i], 1000) + change[i])
