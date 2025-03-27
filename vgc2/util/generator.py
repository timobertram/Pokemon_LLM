from random import sample
from typing import Callable

from numpy import clip
from numpy.random import default_rng, Generator

from vgc2.battle_engine import Type
from vgc2.battle_engine.modifiers import Category, Weather, Terrain, Hazard, Status, Nature
from vgc2.battle_engine.move import Move
from vgc2.battle_engine.pokemon import PokemonSpecies, Pokemon
from vgc2.battle_engine.team import Team
from vgc2.meta import MoveSet, Roster

MoveGenerator = Callable[[Generator], Move]
MoveSetGenerator = Callable[[int, Generator, MoveGenerator], MoveSet]
PokemonSpeciesGenerator = Callable[[MoveSet, int, Generator], PokemonSpecies]
PokemonGenerator = Callable[[PokemonSpecies, int, Generator], Pokemon]
RosterGenerator = Callable[[int, MoveSet, int, Generator, PokemonSpeciesGenerator], Roster]
TeamGenerator = Callable[[int, int, Generator, MoveSetGenerator, PokemonSpeciesGenerator, PokemonGenerator], Team]

_RNG = default_rng()


def gen_move(rng: Generator = _RNG) -> Move:
    category = Category(rng.choice(len(Category), 1, False))
    base_power = 0 if category == Category.OTHER else int(clip(rng.normal(100, 40, 1)[0], 0, 140))
    effect_prob = 1. - base_power / 140
    effect = float(rng.random()) if effect_prob > 0. else -1
    return Move(
        pkm_type=Type(rng.choice(len(Type) - 1, 1, False)),  # no typeless
        base_power=base_power,
        accuracy=1. if rng.random() < .5 else float(rng.uniform(.75, 1.)),
        max_pp=int(clip(rng.normal(10, 2, 1)[0], 5, 20)),
        category=category,
        priority=1 if rng.random() < .3 else 0,
        effect_prob=effect_prob,
        force_switch=0 <= effect < 1 / 17,
        self_switch=1 / 17 <= effect < 2 / 17,
        ignore_evasion=2 / 17 <= effect < 3 / 17,
        protect=3 / 17 <= effect < 4 / 17,
        boosts=tuple([0] + list(int(x) if rng.random() > .5 else -int(x) for x in rng.multinomial(2, [1 / 7] * 7)))
        if 4 / 17 <= effect < 5 / 17 else (0,) * 8,
        self_boosts=rng.random() > .5 if 4 / 17 <= effect < 5 / 17 else True,
        heal=float(rng.random()) / 2 if 5 / 17 <= effect < 6 / 17 else 0.,
        recoil=float(rng.random()) / 2 if 6 / 17 <= effect < 7 / 17 else 0.,
        weather_start=Weather(rng.choice(len(Weather) - 1, 1)[0] + 1) if 7 / 17 <= effect < 8 / 17
        else Weather.CLEAR,
        field_start=Terrain(rng.choice(len(Terrain) - 1, 1)[0] + 1) if 8 / 17 <= effect < 9 / 17
        else Terrain.NONE,
        toggle_trickroom=9 / 17 <= effect < 10 / 17,
        change_type=10 / 17 <= effect < 11 / 17,
        toggle_reflect=11 / 17 <= effect < 12 / 17,
        toggle_lightscreen=12 / 17 <= effect < 13 / 17,
        toggle_tailwind=13 / 17 <= effect < 14 / 17,
        hazard=Hazard(rng.choice(len(Hazard) - 1, 1)[0] + 1) if 14 / 17 <= effect < 15 / 17 else Hazard.NONE,
        status=Status(rng.choice(len(Status) - 1, 1)[0] + 1) if 15 / 17 <= effect < 16 / 17 else Status.NONE,
        disable=16 / 17 <= effect < 1)


def gen_move_set(n: int,
                 rng: Generator = _RNG,
                 _gen_move: MoveGenerator = gen_move) -> MoveSet:
    return [_gen_move(rng) for _ in range(n)]


def gen_move_subset(n: int,
                    moves: MoveSet) -> MoveSet:
    return sample(moves, min(n, len(moves)))


def gen_pkm_species(moves: MoveSet,
                    n_moves: int = 4,
                    rng: Generator = _RNG) -> PokemonSpecies:
    n_types = 1 if rng.random() < 0.5 else 2
    return PokemonSpecies(
        base_stats=(
            int(clip(rng.normal(120, 30, 1)[0], 0, 160)),
            int(clip(rng.normal(100, 40, 1)[0], 0, 140)),
            int(clip(rng.normal(100, 40, 1)[0], 0, 140)),
            int(clip(rng.normal(100, 40, 1)[0], 0, 140)),
            int(clip(rng.normal(100, 40, 1)[0], 0, 140)),
            int(clip(rng.normal(100, 40, 1)[0], 0, 140))),
        types=[Type(x) for x in sample([x for x in range(len(Type) - 1)], n_types)],  # no typeless
        moves=gen_move_subset(n_moves, moves))


def gen_pkm_roster(n: int,
                   moves: MoveSet,
                   n_moves: int = 4,
                   rng: Generator = _RNG,
                   _gen_pkm_species: PokemonSpeciesGenerator = gen_pkm_species) -> Roster:
    return [_gen_pkm_species(moves, n_moves, rng) for _ in range(n)]


def gen_pkm(species: PokemonSpecies,
            max_moves: int = 4,
            rng: Generator = _RNG) -> Pokemon:
    n_moves = len(species.moves)
    return Pokemon(
        species=species,
        move_indexes=list(sample([i for i in range(n_moves)], min(max_moves, n_moves))),
        level=100,
        ivs=(31,) * 6,
        evs=tuple(list(int(x) for x in rng.multinomial(510, [1 / 6] * 6))),
        nature=Nature(rng.choice(len(Nature), 1)[0]))


def gen_team(n: int,
             n_moves: int,
             rng: Generator = _RNG,
             _gen_move_set: MoveSetGenerator = gen_move_set,
             _gen_pkm_species: PokemonSpeciesGenerator = gen_pkm_species,
             _gen_pkm: PokemonGenerator = gen_pkm) -> Team:
    return Team([_gen_pkm(_gen_pkm_species(_gen_move_set(n_moves, rng), n_moves, rng), n_moves, rng) for _ in range(n)])


def gen_team_from_roster(roster: Roster,
                         n: int,
                         n_moves: int,
                         rng: Generator = _RNG,
                         _gen_pkm: PokemonGenerator = gen_pkm) -> Team:
    return Team([_gen_pkm(roster[i], n_moves, rng) for i in rng.choice(len(roster), n)])
