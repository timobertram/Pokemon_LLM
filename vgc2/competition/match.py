from vgc2.agent import BattlePolicy, SelectionPolicy
from vgc2.battle_engine import BattleEngine, State
from vgc2.battle_engine.game_state import get_battle_teams
from vgc2.battle_engine.team import Team
from vgc2.battle_engine.view import TeamView, StateView
from vgc2.competition import CompetitorManager
from vgc2.util.generator import TeamGenerator, _RNG


def subteam(team: Team,
            view: TeamView,
            idx: list[int]) -> tuple[Team, TeamView]:
    sub_team = Team([team.members[i] for i in idx])
    sub_view = TeamView(team, [view._members[i] for i in idx])
    return sub_team, sub_view


def run_battle(engine: BattleEngine,
               agent: tuple[BattlePolicy, BattlePolicy],
               view: tuple[StateView, StateView]) -> int:
    while not engine.finished():
        engine.run_turn((agent[0].decision(view[0]), agent[1].decision(view[1])))
    return engine.winning_side


def label_teams(base_team: tuple[Team, Team]):
    p_id = 0
    m_id = 0
    for t in base_team:
        for p in t.members:
            p.species.id = p_id
            p_id += 1
            for m in p.species.moves:
                m.id = m_id
                m_id += 1


class Match:
    __slots__ = ('cm', 'n_active', 'n_battles', 'max_team_size', 'max_pkm_moves', 'random_teams', 'gen', 'wins')

    def __init__(self,
                 cm: tuple[CompetitorManager, CompetitorManager],
                 n_active: int = 2,
                 n_battles: int = 3,
                 max_team_size: int = 4,
                 max_pkm_moves: int = 4,
                 gen: TeamGenerator | None = None):
        self.cm = cm
        self.n_active = n_active
        self.n_battles = n_battles
        self.max_team_size = max_team_size
        self.max_pkm_moves = max_pkm_moves
        self.gen = gen
        self.wins = [0, 0]

    def run(self):
        if self.gen:
            self._run_random()
        else:
            self._run_non_random()

    def _run_once(self,
                  selector: tuple[SelectionPolicy, SelectionPolicy],
                  base_team: tuple[Team, Team],
                  base_view: tuple[TeamView, TeamView],
                  agent: tuple[BattlePolicy, BattlePolicy]):
        idx = (selector[0].decision((base_team[0], base_view[1]), self.max_team_size),
               selector[1].decision((base_team[1], base_view[0]), self.max_team_size))
        sub = (subteam(base_team[0], base_view[0], idx[0]), subteam(base_team[1], base_view[1], idx[1]))
        team, view = (sub[0][0], sub[1][0]), (sub[0][1], sub[1][1])
        state = State(get_battle_teams(team, self.n_active))
        state_view = StateView(state, 0, view), StateView(state, 1, view)
        engine = BattleEngine(state)
        self.wins[run_battle(engine, agent, state_view)] += 1

    def _run_random(self):
        agent = self.cm[0].competitor.battle_policy, self.cm[1].competitor.battle_policy
        selector = self.cm[0].competitor.selection_policy, self.cm[1].competitor.selection_policy
        tie = True
        runs = 0
        while tie or runs < self.n_battles:
            base_team = (self.gen(self.max_team_size, self.max_pkm_moves, _RNG),
                         self.gen(self.max_team_size, self.max_pkm_moves, _RNG))
            label_teams(base_team)
            base_view = TeamView(base_team[0]), TeamView(base_team[1])
            self._run_once(selector, base_team, base_view, agent)
            self._run_once(selector, (base_team[0], base_team[1]), (base_view[0], base_view[1]), agent)
            tie = self.wins[0] == self.wins[1]
            runs += 1

    def _run_non_random(self):
        agent = self.cm[0].competitor.battle_policy, self.cm[1].competitor.battle_policy
        selector = self.cm[0].competitor.selection_policy, self.cm[1].competitor.selection_policy
        base_team = self.cm[0].team, self.cm[1].team
        base_view = TeamView(base_team[0]), TeamView(base_team[1])
        tie = True
        run = 0
        while tie or run < self.n_battles:
            self._run_once(selector, base_team, base_view, agent)
            tie = self.wins[0] == self.wins[1]
            run += 1
