import time

from vgc2.agent.teambuild import RandomTeamBuildPolicy
from vgc2.competition.ecosystem import build_team
from vgc2.util.generator import gen_move_set, gen_pkm_roster


def main():
    move_set = gen_move_set(100)
    roster = gen_pkm_roster(100, move_set)
    team_builder = RandomTeamBuildPolicy()
    t = time.time()
    team = build_team(team_builder.decision(roster, None, 4, 4, 2), roster)
    print("Duration: " + str(time.time() - t))
    print("~ Team ~")
    print(team)


if __name__ == '__main__':
    main()
