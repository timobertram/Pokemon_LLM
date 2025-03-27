import math

from vgc2.battle_engine.constants import NATURES
from vgc2.battle_engine.modifiers import Type, Stat, Status, Stats, Nature
from vgc2.battle_engine.move import Move, BattlingMove


class PokemonSpecies:
    __slots__ = ('id', 'base_stats', 'types', 'moves', '_instances', 'name')

    def __init__(self,
                 base_stats: Stats,
                 types: list[Type],
                 moves: list[Move],
                 name: str = ""):
        self.id = -1
        self.base_stats = base_stats
        self.types = types
        self.moves = moves
        self.name = name
        self._instances = []

    def __str__(self):
        if self.name:
            return self.name
        return ("Base Stats " + str(self.base_stats) +
                ", Types " + str([t.name for t in self.types]) +
                ", Moves " + str([str(m) for m in self.moves]))

    def edit(self,
             base_stats: Stats,
             types: list[Type],
             moves: list[Move]):
        self.base_stats = base_stats
        self.types = types
        self.moves = moves
        for pkm in self._instances:
            pkm._base_edit()


def update_stats_from_nature(stats: list[int],
                             nature: Nature):
    new_stats = stats.copy()
    try:
        new_stats[NATURES[nature]['plus']] *= 1.1
        new_stats[NATURES[nature]['minus']] /= 1.1
    except KeyError:
        pass
    return new_stats


def calculate_stat(stat: int,
                   iv: int,
                   ev: int,
                   level: int) -> int:
    return math.floor(((2 * stat + iv + math.floor(ev / 4)) * level) / 100)


def calculate_stats(base_stats: Stats,
                    level: int,
                    ivs: Stats = (31,) * 6,
                    evs: Stats = (85,) * 6,
                    nature: Nature = Nature.SERIOUS) -> Stats:
    new_stats = [
        calculate_stat(
            base_stats[Stat.MAX_HP],
            ivs[0],
            evs[0],
            level
        ) + level + 10,
        calculate_stat(
            base_stats[Stat.ATTACK],
            ivs[1],
            evs[1],
            level
        ) + 5,
        calculate_stat(
            base_stats[Stat.DEFENSE],
            ivs[2],
            evs[2],
            level
        ) + 5,
        calculate_stat(
            base_stats[Stat.SPECIAL_ATTACK],
            ivs[3],
            evs[3],
            level
        ) + 5,
        calculate_stat(
            base_stats[Stat.SPECIAL_DEFENSE],
            ivs[4],
            evs[4],
            level
        ) + 5,
        calculate_stat(
            base_stats[Stat.SPEED],
            ivs[5],
            evs[5],
            level
        ) + 5]
    new_stats = update_stats_from_nature(new_stats, nature)
    new_stats = [int(v) for v in new_stats]
    return tuple(new_stats)


class Pokemon:
    __slots__ = ('species', 'moves', 'level', 'evs', 'ivs', 'nature', 'stats', '_views', '_move_indexes')

    def __init__(self,
                 species: PokemonSpecies,
                 move_indexes: list[int],
                 level: int = 100,
                 evs: Stats = (85,) * 6,
                 ivs: Stats = (31,) * 6,
                 nature: Nature = Nature.SERIOUS):
        self.species = species
        self.moves = [self.species.moves[i] for i in move_indexes if 0 <= i < len(move_indexes)]
        self.level = level
        self.evs = evs
        self.ivs = ivs
        self.nature = nature
        self.stats = calculate_stats(self.species.base_stats, self.level, self.ivs, self.evs, self.nature)
        self._move_indexes = move_indexes
        self._views = []
        self.species._instances += [self]

    def __str__(self):
        return ("Stats " + str(self.stats) +
                ", Types " + str([t.name for t in self.species.types]) +
                ", Moves " + str([str(m) for m in self.moves]))

    def __del__(self):
        self.species._instances.remove(self)

    def _base_edit(self):
        self.stats = calculate_stats(self.species.base_stats, self.level, self.ivs, self.evs, self.nature)
        self.moves = [self.species.moves[i] for i in self._move_indexes if 0 <= i < len(self._move_indexes)]

    def edit(self,
             move_indexes: list[int],
             level: int = 100,
             evs: Stats = (85,) * 6,
             ivs: Stats = (31,) * 6,
             nature: Nature = Nature.SERIOUS):
        self.moves = [self.species.moves[i] for i in move_indexes if 0 <= i < len(move_indexes)]
        self.level = level
        self.evs = evs
        self.ivs = ivs
        self.nature = nature
        self.stats = calculate_stats(self.species.base_stats, self.level, self.ivs, self.evs, self.nature)
        self._move_indexes = move_indexes

    def _on_move_used(self, i: int):
        for v in self._views:
            v._on_move_used(i)


class BattlingPokemon:
    __slots__ = ('constants', 'hp', 'types', 'boosts', 'status', '_wake_turns', 'battling_moves', 'last_used_move',
                 'protect', '_consecutive_protect', '_engine')

    def __init__(self,
                 constants: Pokemon):
        self.constants = constants
        self.hp = constants.stats[Stat.MAX_HP]
        self.types = constants.species.types
        self.boosts = [0] * 8  # position 0 is not used
        self.status = Status.NONE
        self._wake_turns = 0
        self.battling_moves = [BattlingMove(m) for m in constants.moves]
        self.last_used_move: BattlingMove | None = None
        self.protect = False
        self._consecutive_protect = 0
        self._engine = None

    def __str__(self):
        return ("Stats " + str(self.constants.stats) +
                ", Types " + str([t.name for t in self.types]) +
                ", HP " + str(self.hp) +
                (", Boosts " + str(self.boosts[1:]) if any(b > 0 for b in self.boosts) else "") +
                (", " + self.status.name if self.status != Status.NONE else "") +
                (", Moves " + str([str(m) for m in self.battling_moves])))

    def reset(self):
        self.hp = self.constants.stats[Stat.MAX_HP]
        self.types = self.constants.species.types
        self.boosts = [0] * 8
        self.status = Status.NONE
        self._wake_turns = 0
        for move in self.battling_moves:
            move.reset()
        self.last_used_move = None
        self.protect = False
        self._consecutive_protect = 0

    def fainted(self) -> bool:
        return self.hp == 0

    def deal_damage(self,
                    damage: int):
        self.hp = max(0, self.hp - damage)
        if self.fainted():
            self._engine._on_fainted(self)

    def recover(self,
                heal: int):
        self.hp = min(self.hp + heal, self.constants.species.base_stats[Stat.MAX_HP])

    def on_switch(self):
        self.boosts = [0] * 8
        for move in self.battling_moves:
            move.disabled = False
        self.last_used_move = None
        self.protect = False

    def on_turn_end(self):
        if self.protect:
            self.protect = False
            self._consecutive_protect += 1
        else:
            self._consecutive_protect = 0
        if self.status == Status.SLEEP:
            self._wake_turns -= 1

    def on_move_used(self, move: BattlingMove):
        self.constants._on_move_used(self.battling_moves.index(move))
