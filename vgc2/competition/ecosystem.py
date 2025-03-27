from enum import IntEnum
from random import shuffle

from vgc2.agent import TeamBuildCommand, RosterBalanceCommand, MoveSetBalanceCommand
from vgc2.battle_engine import Team
from vgc2.battle_engine.pokemon import Pokemon
from vgc2.competition import CompetitorManager, DesignCompetitorManager
from vgc2.competition.elo import elo_rating
from vgc2.competition.match import Match
from vgc2.meta import Roster, Meta, MoveSet
from vgc2.meta.constraints import Constraints
from vgc2.meta.evaluator import MetaEvaluator, evaluate_meta


class Strategy(IntEnum):
    RANDOM_PAIRING = 0
    ELO_PAIRING = 1


def build_team(cmd: TeamBuildCommand,
               roster: Roster) -> Team:
    return Team([Pokemon(roster[params[0]], params[4], 100, params[1], params[2], params[3]) for params in cmd])


def label_roster(move_set: MoveSet,
                 roster: Roster):
    for i, m in enumerate(move_set):
        m.id = i
    for i, p in enumerate(roster):
        p.id = i


class Championship:
    __slots__ = ('cm', 'roster', 'meta', 'epochs', 'n_active', 'n_battles', 'max_team_size', 'max_pkm_moves',
                 'strategy')

    def __init__(self,
                 roster: Roster,
                 meta: Meta,
                 epochs: int = 100,
                 n_active: int = 2,
                 n_battles: int = 3,
                 max_team_size: int = 4,
                 max_pkm_moves: int = 4,
                 strategy: Strategy = Strategy.RANDOM_PAIRING):
        self.cm: list[CompetitorManager] = []
        self.roster = roster
        self.meta = meta
        self.epochs = epochs
        self.n_active = n_active
        self.n_battles = n_battles
        self.max_team_size = max_team_size
        self.max_pkm_moves = max_pkm_moves
        self.strategy = strategy

    def register(self,
                 cm: CompetitorManager):
        self.cm += [cm]

    def run(self):
        e = 0
        while e < self.epochs:
            self._build_teams()
            self._pairings()
            self._matches()
            e += 1

    def _build_teams(self):
        for cm in self.cm:
            cm.team = build_team(cm.competitor.team_build_policy.decision(
                self.roster, self.meta, self.max_team_size, self.max_pkm_moves, self.n_active), self.roster)

    def _pairings(self):
        match self.strategy:
            case Strategy.RANDOM_PAIRING:
                shuffle(self.cm)
            case Strategy.ELO_PAIRING:
                sorted(self.cm, key=lambda x: -x.elo)

    def _matches(self):
        n_matches = len(self.cm) // 2
        m = 0
        while m < n_matches:
            cm = self.cm[2 * m], self.cm[2 * m + 1]
            match = Match(cm, self.n_active, self.n_battles, self.max_team_size, self.max_pkm_moves, False)
            match.run()
            winner = 1 if match.wins[1] > match.wins[0] else 0
            cm[0].elo, cm[1].elo = elo_rating(cm[0].elo, cm[1].elo, winner)
            self.meta.add_match((cm[0].team, cm[1].team), winner, (cm[0].elo, cm[1].elo))
            m += 1

    def ranking(self) -> list[CompetitorManager]:
        return sorted(self.cm, key=lambda cm: -cm.elo)


def build_move_set(cmd: MoveSetBalanceCommand,
                   move_set: MoveSet):
    for c in cmd:
        c[1].id = c[0]  # assure labeling
        move_set[c[0]] = c[1]


def build_roster(cmd: RosterBalanceCommand,
                 roster: Roster,
                 move_set: MoveSet):
    for c in cmd:
        roster[c[0]].edit(c[2], c[1], [move_set[i] for i in c[3]])


class MetaDesign:
    __slots__ = ('move_set', 'roster', 'meta', 'constraints', 'championship', 'epochs', 'dcm', 'meta_evaluator')

    def __init__(self,
                 move_set: MoveSet,
                 roster: Roster,
                 meta: Meta,
                 constraints: Constraints,
                 championship: Championship,
                 epochs: int = 100,
                 meta_evaluator: MetaEvaluator = evaluate_meta):
        self.move_set = move_set
        self.roster = roster
        self.meta = meta
        self.constraints = constraints
        self.championship = championship
        self.epochs = epochs
        self.dcm: DesignCompetitorManager
        self.meta_evaluator = meta_evaluator

    def register(self, dcm: DesignCompetitorManager):
        self.dcm = dcm

    def run(self):
        e = 0
        while e < self.epochs:
            move_set_cmd, roster_cmd = self.dcm.competitor.meta_balance_policy.decision(self.move_set, self.roster,
                                                                                        self.meta, self.constraints)
            build_move_set(move_set_cmd, self.move_set)
            build_roster(roster_cmd, self.roster, self.move_set)
            self.meta.change_roster(self.move_set, self.roster)
            self.championship.run()
            self.dcm.score += self.meta_evaluator(self.meta)
            e += 1
