from vgc2.battle_engine.constants import BattleRuleParam
from vgc2.battle_engine.game_state import State
from vgc2.battle_engine.modifiers import Type, Category, Weather, Terrain, Status, MutableStats
from vgc2.battle_engine.move import Move
from vgc2.battle_engine.pokemon import Stat, BattlingPokemon


def calculate_damage(params: BattleRuleParam,
                     attacking_side: int,
                     move: Move,
                     state: State,
                     attacker: BattlingPokemon,
                     defender: BattlingPokemon) -> int:
    # determine if combat is physical or special
    attacking_type = move.category
    if attacking_type == Category.PHYSICAL:
        attack = Stat.ATTACK
        defense = Stat.DEFENSE
    elif attacking_type == Category.SPECIAL:
        attack = Stat.SPECIAL_ATTACK
        defense = Stat.SPECIAL_DEFENSE
    else:
        return 0
    # determine if move has no base power
    if move.base_power == 0:
        return 0
    # calculate actual power of attacker and defender
    attacking_stats = calculate_boosted_stats(params, attacker)
    defending_stats = calculate_boosted_stats(params, defender)
    # rock types get 1.5x SPDEF in sand
    # ice types get 1.5x DEF in snow
    try:
        if state.weather == Weather.SAND and Type.ROCK in defender.types:
            defending_stats[Stat.SPECIAL_DEFENSE] = int(defending_stats[Stat.SPECIAL_DEFENSE] * params.WEATHER_BOOST)
        elif state.weather == Weather.SNOW and Type.ICE in defender.types:
            defending_stats[Stat.DEFENSE] = int(defending_stats[Stat.DEFENSE] * params.WEATHER_BOOST)
    except KeyError:
        pass
    # apply damage formula
    damage = int(int((2 * attacker.constants.level) / 5) + 2) * move.base_power
    damage = int(damage * attacking_stats[attack] / defending_stats[defense])
    damage = int(damage / 50) + 2
    damage *= calculate_modifier(params, attacker, defender, move, state, attacking_side)
    # result
    return int(damage)


def calculate_boosted_stats(params: BattleRuleParam,
                            pkm: BattlingPokemon) -> MutableStats:
    return [
        0,
        params.BOOST_MULTIPLIER_LOOKUP[pkm.boosts[Stat.ATTACK]] * pkm.constants.stats[Stat.ATTACK],
        params.BOOST_MULTIPLIER_LOOKUP[pkm.boosts[Stat.DEFENSE]] * pkm.constants.stats[Stat.DEFENSE],
        params.BOOST_MULTIPLIER_LOOKUP[pkm.boosts[Stat.SPECIAL_ATTACK]] * pkm.constants.stats[Stat.SPECIAL_ATTACK],
        params.BOOST_MULTIPLIER_LOOKUP[pkm.boosts[Stat.SPECIAL_DEFENSE]] * pkm.constants.stats[Stat.SPECIAL_DEFENSE],
    ]


def calculate_modifier(params: BattleRuleParam,
                       attacker: BattlingPokemon,
                       defender: BattlingPokemon,
                       move: Move,
                       state: State,
                       attacking_side: int) -> float:
    modifier = 1
    modifier *= type_effectiveness_modifier(params, move.pkm_type, defender.types)
    modifier *= weather_modifier(params, move, state.weather)
    modifier *= stab_modifier(params, attacker, move)
    modifier *= burn_modifier(params, attacker, move)
    modifier *= terrain_modifier(params, move, state.field)
    modifier *= light_screen_modifier(params, move, state.sides[attacking_side].conditions.lightscreen)
    modifier *= reflect_modifier(params, move, state.sides[attacking_side].conditions.reflect)
    return modifier


def type_effectiveness_modifier(params: BattleRuleParam,
                                move_type: Type,
                                defending_types: list[Type]) -> float:
    if move_type == Type.TYPELESS:
        return 1.
    modifier = 1.
    for defending_pkm_type in defending_types:
        modifier *= params.DAMAGE_MULTIPLICATION_ARRAY[move_type][defending_pkm_type]
    return modifier


def weather_modifier(params: BattleRuleParam,
                     move: Move,
                     weather: Weather) -> float:
    if weather == Weather.CLEAR:
        return 1
    if weather == Weather.SUN and move.pkm_type == Type.FIRE:
        return params.WEATHER_BOOST
    elif weather == Weather.SUN and move.pkm_type == Type.WATER:
        return params.WEATHER_UNBOOST
    elif weather == Weather.RAIN and move.pkm_type == Type.WATER:
        return params.WEATHER_BOOST
    elif weather == Weather.RAIN and move.pkm_type == Type.FIRE:
        return params.WEATHER_UNBOOST
    return 1


def stab_modifier(params: BattleRuleParam,
                  attacker: BattlingPokemon,
                  move: Move) -> float:
    if move.pkm_type == Type.TYPELESS:
        return 1.
    return params.STAB_MODIFIER if move.pkm_type in [t for t in attacker.types] else 1


def burn_modifier(params: BattleRuleParam,
                  attacker: BattlingPokemon,
                  move: Move):
    return params.BURN_DAMAGE_MODIFIER if Status.BURN == attacker.status and move.category == Category.PHYSICAL else 1


def light_screen_modifier(params: BattleRuleParam,
                          move: Move,
                          light_screen: bool) -> float:
    return params.LIGHT_SCREEN_MODIFIER if light_screen and move.category == Category.SPECIAL else 1


def reflect_modifier(params: BattleRuleParam,
                     move: Move,
                     reflect: bool) -> float:
    return params.REFLECT_MODIFIER if reflect and move.category == Category.PHYSICAL else 1


def terrain_modifier(params: BattleRuleParam,
                     move: Move,
                     terrain: Terrain) -> float:
    if terrain == Terrain.NONE:
        return 1
    if terrain == Terrain.ELECTRIC_TERRAIN and move.pkm_type == Type.ELECTRIC:
        return params.TERRAIN_DAMAGE_BOOST
    elif terrain == Terrain.GRASSY_TERRAIN and move.pkm_type == Type.GRASS:
        return params.TERRAIN_DAMAGE_BOOST
    elif terrain == Terrain.MISTY_TERRAIN and move.pkm_type == Type.DRAGON:
        return params.TERRAIN_DAMAGE_UNBOOST
    elif terrain == Terrain.PSYCHIC_TERRAIN and move.pkm_type == Type.PSYCHIC:
        return params.TERRAIN_DAMAGE_BOOST
    elif terrain == Terrain.PSYCHIC_TERRAIN and move.priority > 0:
        return 0
    return 1


def calculate_stealth_rock_damage(params: BattleRuleParam,
                                  pkm: BattlingPokemon) -> int:
    return (pkm.constants.species.base_stats[Stat.MAX_HP] * params.STEALTH_ROCK_MODIFIER *
            type_effectiveness_modifier(params, Type.ROCK, pkm.types))


def calculate_poison_damage(params: BattleRuleParam,
                            pkm: BattlingPokemon) -> int:
    return pkm.constants.species.base_stats[Stat.MAX_HP] * params.POISON_MODIFIER


def calculate_burn_damage(params: BattleRuleParam,
                          pkm: BattlingPokemon) -> int:
    return pkm.constants.species.base_stats[Stat.MAX_HP] * params.BURN_MODIFIER


def calculate_sand_damage(params: BattleRuleParam,
                          pkm: BattlingPokemon) -> int:
    for t in pkm.types:
        if t in (Type.ROCK, Type.GROUND, Type.STEEL):
            return 0
    return pkm.constants.species.base_stats[Stat.MAX_HP] * params.SAND_MODIFIER
