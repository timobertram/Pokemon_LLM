import argparse
from multiprocessing.connection import Client

from vgc2.competition import CompetitorManager
from vgc2.competition.ecosystem import Championship, Strategy, label_roster
from vgc2.meta import BasicMeta
from vgc2.net.client import ProxyCompetitor
from vgc2.net.server import BASE_PORT
from vgc2.util.generator import gen_move_set, gen_pkm_roster


def main(_args):
    move_set = gen_move_set(_args.n_moves)
    roster = gen_pkm_roster(_args.roster_size, move_set)
    label_roster(move_set, roster)
    meta = BasicMeta(move_set, roster)
    conns = []
    championship = Championship(roster, meta, _args.epochs, _args.n_active, _args.n_battles, _args.max_team_size,
                                _args.max_pkm_moves, Strategy.ELO_PAIRING)
    for i in range(_args.n_agents):
        address = ('localhost', _args.base_port + i)
        conn = Client(address, authkey=f'Competitor {i}'.encode('utf-8'))
        conns.append(conn)
        championship.register(CompetitorManager(ProxyCompetitor(conn)))
    championship.run()
    ranking = championship.ranking()
    winner = ranking[0]
    print(winner.competitor.name + " wins the tournament!")
    print(f"ELO {winner.elo}")
    for conn in conns:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--n_moves', type=int, default=100)
    parser.add_argument('--roster_size', type=int, default=50)
    parser.add_argument('--n_agents', type=int, default=2)
    parser.add_argument('--max_team_size', type=int, default=4)
    parser.add_argument('--n_active', type=int, default=2)
    parser.add_argument('--max_pkm_moves', type=int, default=4)
    parser.add_argument('--n_battles', type=int, default=3)
    parser.add_argument('--base_port', type=int, default=BASE_PORT)
    args = parser.parse_args()
    main(args)
