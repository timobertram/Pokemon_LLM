from abc import ABC, abstractmethod
from multiprocessing.connection import Listener

from vgc2.competition import Competitor, DesignCompetitor

DEFAULT_ADDRESS = 'localhost'
BASE_PORT = 5000


class RemoteManager(ABC):

    def __init__(self, authkey, address=DEFAULT_ADDRESS, port=BASE_PORT):
        self.authkey = authkey
        self.address = address
        self.port = port
        self.conn = None

    def run(self):
        while True:
            listener = Listener((self.address, self.port), authkey=self.authkey)
            print('Waiting...')
            self.conn = listener.accept()
            print('Connection accepted from', listener.last_accepted)
            while True:
                try:
                    msg = self.conn.recv()
                except EOFError:
                    self.conn.close()
                    break
                self._run_method(msg)
            listener.close()

    @abstractmethod
    def _run_method(self, msg):
        pass


class RemoteCompetitorManager(RemoteManager):

    def __init__(self, competitor: Competitor, authkey, address=DEFAULT_ADDRESS, port=BASE_PORT):
        super().__init__(authkey, address, port)
        self.competitor = competitor

    def _run_method(self, msg):
        match msg[0]:
            case 'BattlePolicy':
                self.conn.send(self.competitor.battle_policy.decision(msg[1]))
            case 'SelectionPolicy':
                self.conn.send(self.competitor.selection_policy.decision(msg[1], msg[2]))
            case 'TeamBuildPolicy':
                self.conn.send(self.competitor.team_build_policy.decision(msg[1], msg[2], msg[3], msg[4], msg[5]))
            case 'name':
                self.conn.send(self.competitor.name)


class RemoteDesignCompetitorManager(RemoteManager):

    def __init__(self, competitor: DesignCompetitor, authkey, address=DEFAULT_ADDRESS, port=BASE_PORT):
        super().__init__(authkey, address, port)
        self.competitor = competitor

    def _run_method(self, msg):
        match msg[0]:
            case 'MetaBalancePolicy':
                self.conn.send(self.competitor.meta_balance_policy.decision(msg[1], msg[2], msg[3], msg[4]))
            case 'RuleBalancePolicy':
                self.conn.send(self.competitor.rule_balance_policy.decision(msg[1]))
            case 'name':
                self.conn.send(self.competitor.name)
