from abc import ABC, abstractmethod

from vgc2.battle_engine import Team, Move
from vgc2.battle_engine.pokemon import PokemonSpecies

MoveSet = list[Move]
Roster = list[PokemonSpecies]


class Meta(ABC):
    @abstractmethod
    def add_match(self,
                  team: tuple[Team, Team],
                  winner: int,
                  elo: tuple[int, int]):
        pass

    @abstractmethod
    def change_roster(self,
                      move_set: MoveSet,
                      roster: Roster):
        pass

    @abstractmethod
    def usage_rate_move(self,
                        move: Move) -> float:
        pass

    @abstractmethod
    def usage_rate_pokemon(self,
                           pokemon: PokemonSpecies) -> float:
        pass

    @abstractmethod
    def usage_rate_team(self,
                        team: Team) -> float:
        pass


class BasicMeta(Meta):
    def __init__(self,
                 move_set: MoveSet,
                 roster: Roster,
                 limit: int = 1000):
        self.move_set = move_set
        self.roster = roster
        self.move_usage: list[int] = [0] * len(move_set)
        self.pokemon_usage: list[int] = [0] * len(roster)
        self.record: list[tuple[tuple[Team, Team], int, tuple[int, int]]] = []
        self.limit = limit

    def _update_usage(self,
                      team: tuple[Team, Team],
                      value: int):
        for t in team:
            counted_moves = []
            for p in t.members:
                self.pokemon_usage[p.species.id] += value
                for m in p.moves:
                    if m not in counted_moves:
                        self.move_usage[m.id] += value
                        counted_moves += [m]

    def add_match(self,
                  team: tuple[Team, Team],
                  winner: int,
                  elo: tuple[int, int]):
        self.record += [(team, winner, elo)]
        self._update_usage(team, 1)
        if len(self.record) > self.limit:
            old_team, _, _ = self.record.pop(0)
            self._update_usage(old_team, -1)

    def change_roster(self,
                      move_set: MoveSet,
                      roster: Roster):
        self.move_set = move_set
        self.roster = roster
        self.move_usage = [0] * len(self.move_set)
        self.pokemon_usage = [0] * len(self.roster)
        self.record = []

    def usage_rate_move(self,
                        move: Move) -> float:
        return self.move_usage[move.id] / (len(self.record) * 2)

    def usage_rate_pokemon(self,
                           pokemon: PokemonSpecies) -> float:
        return self.pokemon_usage[pokemon.id] / (len(self.record) * 2)

    def usage_rate_team(self,
                        team: Team) -> float:
        return sum(self.usage_rate_pokemon(p.species) for p in team.members) / len(team.members)
