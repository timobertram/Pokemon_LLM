from abc import ABC

from vgc2.agent import BattlePolicy, SelectionPolicy, TeamBuildPolicy, MetaBalancePolicy, RuleBalancePolicy
from vgc2.battle_engine import Team


class Competitor(ABC):

    @property
    def battle_policy(self) -> BattlePolicy | None:
        return None

    @property
    def selection_policy(self) -> SelectionPolicy | None:
        return None

    @property
    def team_build_policy(self) -> TeamBuildPolicy | None:
        return None

    @property
    def name(self) -> str:
        return ""


class CompetitorManager:
    __slots__ = ('competitor', 'team', 'elo')

    def __init__(self,
                 c: Competitor):
        self.competitor: Competitor = c
        self.team: Team | None = None
        self.elo = 1200

    def __str__(self):
        return self.competitor.name + " ELO " + str(self.elo) + (" Team " + str(self.team) if self.team else "")


class DesignCompetitor(ABC):

    @property
    def meta_balance_policy(self) -> MetaBalancePolicy | None:
        return None

    @property
    def rule_balance_policy(self) -> RuleBalancePolicy | None:
        return None

    @property
    def name(self) -> str:
        return ""


class DesignCompetitorManager:
    __slots__ = ('competitor', 'score')

    def __init__(self,
                 c: DesignCompetitor):
        self.competitor: DesignCompetitor = c
        self.score = 0
