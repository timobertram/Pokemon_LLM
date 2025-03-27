from vgc2.agent.battle import GreedyBattlePolicy, RandomBattlePolicy
from vgc2.battle_engine import BattleEngine, State, StateView, TeamView
from vgc2.battle_engine.game_state import get_battle_teams
from vgc2.competition.match import run_battle, label_teams
from vgc2.util.generator import gen_team


def main():
    n_active = 2
    team_size = 4
    n_moves = 4
    team = gen_team(team_size, n_moves), gen_team(team_size, n_moves)
    label_teams(team)
    team_view = TeamView(team[0]), TeamView(team[1])
    state = State(get_battle_teams(team, n_active))
    state_view = StateView(state, 0, team_view), StateView(state, 1, team_view)
    engine = BattleEngine(state)
    agent = GreedyBattlePolicy(), RandomBattlePolicy()
    print("~ Team 0 ~")
    print(team[0])
    print("~ Team 1 ~")
    print(team[1])
    winner = run_battle(engine, agent, state_view)
    print("Side " + str(winner) + " wins!")


if __name__ == '__main__':
    main()
