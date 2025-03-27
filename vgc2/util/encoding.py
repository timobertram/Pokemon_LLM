from numpy import array

from vgc2.battle_engine.game_state import Side, State
from vgc2.battle_engine.modifiers import Weather, Terrain, Hazard, Status
from vgc2.battle_engine.move import Move, BattlingMove
from vgc2.battle_engine.pokemon import Pokemon, BattlingPokemon
from vgc2.battle_engine.team import Team, BattlingTeam


def one_hot(e: array,
            pos: int,
            n: int) -> int:
    i = 0
    while i < n:
        if i == pos:
            e[i] = 1
        else:
            e[i] = 0
        i += 1
    return i


def multi_hot(e: array,
              pos: list[int],
              n: int):
    i = 0
    while i < n:
        if i in pos:
            e[i] = 1
        else:
            e[i] = 0
        i += 1
    return i


class EncodeContext:
    __slots__ = ('max_hp', 'max_pp', 'max_stage', 'max_priority', 'n_types', 'n_status', 'n_weather', 'n_terrain',
                 'n_hazard', 'max_boost', 'n_boosts', 'max_ratio', 'n_category', 'n_stats', 'max_sleep')

    def __init__(self,
                 max_hp: int = 500,
                 max_pp: int = 20,
                 max_stage: int = 5,
                 max_priority: int = 1,
                 n_types: int = 18,
                 n_status: int = 5,
                 n_weather: int = 4,
                 n_terrain: int = 4,
                 n_hazard: int = 2,
                 max_boost: int = 6,
                 n_boosts: int = 7,
                 max_ratio: float = 1.0,
                 n_category: int = 3,
                 n_stats: int = 6,
                 max_sleep: int = 5):
        self.max_hp = max_hp
        self.max_pp = max_pp
        self.max_stage = max_stage
        self.n_types = n_types
        self.n_status = n_status
        self.n_weather = n_weather
        self.n_terrain = n_terrain
        self.n_hazard = n_hazard
        self.max_priority = max_priority
        self.max_boost = max_boost
        self.n_boosts = n_boosts
        self.max_ratio = max_ratio
        self.n_category = n_category
        self.n_stats = n_stats
        self.max_sleep = max_sleep


def encode_move(e: array,
                move: Move,
                ctx: EncodeContext) -> int:
    i = 0
    e[i] = move.base_power / ctx.max_hp
    i += 1
    e[i] = move.accuracy
    i += 1
    e[i] = move.max_pp / ctx.max_pp
    i += 1
    e[i] = move.priority / ctx.max_priority
    i += 1
    e[i] = move.effect_prob
    i += 1
    e[i] = float(move.force_switch)
    i += 1
    e[i] = float(move.self_switch)
    i += 1
    e[i] = float(move.ignore_evasion)
    i += 1
    e[i] = float(move.protect)
    i += 1
    e[i] = move.heal / ctx.max_ratio
    i += 1
    e[i] = move.recoil / ctx.max_ratio
    i += 1
    e[i] = float(move.toggle_trickroom)
    i += 1
    e[i] = float(move.toggle_reflect)
    i += 1
    e[i] = float(move.toggle_lightscreen)
    i += 1
    e[i] = float(move.toggle_tailwind)
    i += 1
    e[i] = float(move.change_type)
    i += 1
    e[i] = float(move.disable)
    i += 1
    for j in range(0, ctx.n_boosts):
        e[j + i] = move.boosts[j] / ctx.max_boost
    i += ctx.n_boosts
    e[i] = 0. if all(b == 0 for b in move.boosts) else (-1. if move.self_boosts else 1.)
    i += 1
    i += one_hot(e[i:], move.pkm_type, ctx.n_types)
    i += one_hot(e[i:], move.category, ctx.n_category)
    if move.weather_start != Weather.CLEAR:
        one_hot(e[i:], move.weather_start - 1, ctx.n_weather)
    i += ctx.n_weather
    if move.field_start != Terrain.NONE:
        one_hot(e[i:], move.field_start - 1, ctx.n_terrain)
    i += ctx.n_terrain
    if move.hazard != Hazard.NONE:
        one_hot(e[i:], move.hazard - 1, ctx.n_hazard)
    i += ctx.n_hazard
    return i


def encode_battling_move(e: array,
                         move: BattlingMove,
                         ctx: EncodeContext) -> int:
    i = encode_move(e, move.constants, ctx)
    e[i] = float(move.disabled)
    i += 1
    e[i] = move.pp / ctx.max_pp
    i += 1
    return i


def encode_pokemon(e: array,
                   pokemon: Pokemon,
                   ctx: EncodeContext) -> int:
    i = 0
    for m in pokemon.moves:
        i += encode_move(e[i:], m, ctx)
    for j in range(0, ctx.n_stats):
        e[j + i] = pokemon.stats[j] / ctx.max_hp
    i += ctx.n_stats
    i += multi_hot(e, pokemon.species.types, ctx.n_types)
    return i


def encode_battling_pokemon(e: array,
                            pokemon: BattlingPokemon,
                            ctx: EncodeContext) -> int:
    i = 0
    for j in range(0, ctx.n_stats):
        e[j + i] = pokemon.constants.stats[j] / ctx.max_hp
    i += ctx.n_stats
    for m in pokemon.battling_moves:
        i += encode_battling_move(e[i:], m, ctx)
    e[i] = pokemon.hp / ctx.max_hp
    i += multi_hot(e, pokemon.types, ctx.n_types)
    for j in range(0, ctx.n_boosts):
        e[j + i] = pokemon.boosts[j] / ctx.max_boost
    i += ctx.n_boosts
    if pokemon.status != Status.NONE:
        one_hot(e[i:], pokemon.status, ctx.n_status)
    i += ctx.n_status
    e[i] = float(pokemon.protect)
    i += 1
    e[i] = pokemon._wake_turns / ctx.max_sleep
    i += 1
    return i


def encode_team(e: array,
                team: Team,
                ctx: EncodeContext) -> int:
    i = 0
    for m in team.members:
        i += encode_pokemon(e[i:], m, ctx)
    return i


def encode_battling_team(e: array,
                         team: BattlingTeam,
                         ctx: EncodeContext) -> int:
    i = 0
    for m in team.active:
        i += encode_battling_pokemon(e[i:], m, ctx)
    for m in team.reserve:
        i += encode_battling_pokemon(e[i:], m, ctx)
    return i


def encode_side(e: array,
                side: Side,
                ctx: EncodeContext) -> int:
    i = 0
    i += encode_battling_team(e[i:], side.team, ctx)
    e[i] = float(side.conditions.reflect)
    i += 1
    e[i] = float(side.conditions.lightscreen)
    i += 1
    e[i] = float(side.conditions.tailwind)
    i += 1
    e[i] = float(side.conditions.stealth_rock)
    i += 1
    e[i] = float(side.conditions.poison_spikes)
    i += 1
    return i


def encode_state(e: array,
                 state: State,
                 ctx: EncodeContext) -> int:
    i = 0
    for s in state.sides:
        i += encode_side(e[i:], s, ctx)
    if state.weather != Weather.CLEAR:
        one_hot(e[i:], state.weather - 1, ctx.n_weather)
    i += ctx.n_weather
    if state.field != Terrain.NONE:
        one_hot(e[i:], state.field - 1, ctx.n_terrain)
    i += ctx.n_terrain
    e[i] = float(state.trickroom)
    i += 1
    return i
