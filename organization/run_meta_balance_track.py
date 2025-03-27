import argparse
from multiprocessing.connection import Client

from vgc2.competition import CompetitorManager, DesignCompetitorManager
from vgc2.competition.ecosystem import Championship, Strategy, MetaDesign, label_roster
from vgc2.meta import BasicMeta
from vgc2.meta.constraints import Constraints
from vgc2.net.client import ProxyCompetitor, ProxyDesignCompetitor
from vgc2.net.server import BASE_PORT
from vgc2.util.generator import gen_move_set, gen_pkm_roster


def main(_args):
    move_set = gen_move_set(_args.n_moves)
    roster = gen_pkm_roster(_args.roster_size, move_set)
    label_roster(move_set, roster)
    meta = BasicMeta(move_set, roster)
    constraints = Constraints()
    conns = []
    championship = Championship(roster, meta, _args.epochs, _args.n_active, _args.n_battles, _args.max_team_size,
                                _args.max_pkm_moves, Strategy.ELO_PAIRING)
    meta_design = MetaDesign(move_set, roster, meta, constraints, championship, _args.d_epochs)
    for i in range(_args.n_agents):
        address = ('localhost', _args.base_port + i)
        conn = Client(address, authkey=f'Competitor {i}'.encode('utf-8'))
        conns.append(conn)
        championship.register(CompetitorManager(ProxyCompetitor(conn)))
    i = _args.n_agents
    conn = Client(('localhost', _args.base_port + i), authkey=f'Competitor {i}'.encode('utf-8'))
    conns.append(conn)
    dcm = DesignCompetitorManager(ProxyDesignCompetitor(conn))
    meta_design.register(dcm)
    meta_design.run()
    print(dcm.competitor.name + " got " + dcm.score + " score!")
    for conn in conns:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--d_epochs', type=int, default=100)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--n_moves', type=int, default=100)
    parser.add_argument('--roster_size', type=int, default=50)
    parser.add_argument('--n_agents', type=int, default=2)
    parser.add_argument('--max_team_size', type=int, default=4)
    parser.add_argument('--n_active', type=int, default=2)
    parser.add_argument('--max_pkm_moves', type=int, default=4)
    parser.add_argument('--n_battles', type=int, default=10)
    parser.add_argument('--base_port', type=int, default=BASE_PORT)
    args = parser.parse_args()
    main(args)
