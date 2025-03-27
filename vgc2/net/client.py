from multiprocessing.connection import Client

from vgc2.agent import BattlePolicy, SelectionPolicy, SelectionCommand, TeamBuildPolicy, TeamBuildCommand, \
    MetaBalancePolicy, RosterBalanceCommand, RuleBalanceCommand, RuleBalancePolicy
from vgc2.battle_engine import State, BattleCommand, Team
from vgc2.competition import Competitor, DesignCompetitor
from vgc2.meta import Meta, Roster, MoveSet
from vgc2.meta.constraints import Constraints


class ProxyBattlePolicy(BattlePolicy):

    def __init__(self,
                 conn: Client):
        self.__conn: Client = conn

    def decision(self,
                 state: State) -> list[BattleCommand]:
        self.__conn.send(('BattlePolicy', state))
        return self.__conn.recv()


class ProxySelectionPolicy(SelectionPolicy):

    def __init__(self,
                 conn: Client):
        self.__conn: Client = conn

    def decision(self,
                 teams: tuple[Team, Team],
                 max_size: int) -> SelectionCommand:
        self.__conn.send(('SelectionPolicy', teams, max_size))
        return self.__conn.recv()


class ProxyTeamBuildPolicy(TeamBuildPolicy):

    def __init__(self,
                 conn: Client):
        self.conn: Client = conn

    def decision(self,
                 roster: Roster,
                 meta: Meta | None,
                 max_team_size: int,
                 max_pkm_moves: int,
                 n_active: int) -> TeamBuildCommand:
        self.conn.send(('TeamBuildPolicy', roster, meta, max_team_size, max_pkm_moves, n_active))
        return self.conn.recv()


class ProxyMetaBalancePolicy(MetaBalancePolicy):

    def __init__(self,
                 conn: Client):
        self.__conn: Client = conn

    def decision(self,
                 move_set: MoveSet,
                 roster: Roster,
                 meta: Meta,
                 constraints: Constraints) -> RosterBalanceCommand:
        self.__conn.send(('BalancePolicy', move_set, roster, meta, constraints))
        return self.__conn.recv()


class ProxyRuleBalancePolicy(RuleBalancePolicy):

    def __init__(self,
                 conn: Client):
        self.__conn: Client = conn

    def decision(self,
                 rules: RuleBalanceCommand) -> RuleBalanceCommand:
        self.__conn.send(('RuleBalancePolicy', rules))
        return self.__conn.recv()


class ProxyCompetitor(Competitor):

    def __init__(self,
                 conn: Client):
        self.__conn = conn
        self.__battle_policy = ProxyBattlePolicy(conn)
        self.__selection_policy = ProxySelectionPolicy(conn)
        self.__team_build_policy = ProxyTeamBuildPolicy(conn)

    @property
    def battle_policy(self) -> BattlePolicy:
        return self.__battle_policy

    @property
    def selection_policy(self) -> SelectionPolicy:
        return self.__selection_policy

    @property
    def team_build_policy(self) -> TeamBuildPolicy:
        return self.__team_build_policy

    @property
    def name(self) -> str:
        self.__conn.send(('name',))
        return self.__conn.recv()


class ProxyDesignCompetitor(DesignCompetitor):

    def __init__(self,
                 conn: Client):
        self.__conn = conn
        self.__meta_balance = ProxyMetaBalancePolicy(conn)
        self.__rule_balance = ProxyRuleBalancePolicy(conn)

    @property
    def meta_balance_policy(self) -> MetaBalancePolicy:
        return self.__meta_balance

    @property
    def rule_balance_policy(self) -> RuleBalancePolicy:
        return self.__rule_balance

    @property
    def name(self) -> str:
        self.__conn.send(('name',))
        return self.__conn.recv()
