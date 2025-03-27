from itertools import product

from numpy import array

from vgc2.battle_engine import BattleRuleParam


def set_params(params: BattleRuleParam,
               attr: array) -> int:
    i = 0
    params.TRICKROOM_TURNS = int(attr[i])
    i += 1
    params.WEATHER_TURNS = int(attr[i])
    i += 1
    params.TERRAIN_TURNS = int(attr[i])
    i += 1
    params.REFLECT_TURNS = int(attr[i])
    i += 1
    params.LIGHTSCREEN_TURNS = int(attr[i])
    i += 1
    params.TAILWIND_TURNS = int(attr[i])
    i += 1
    # PRIORITY MODIFIERS
    params.PARALYSIS_MODIFIER = attr[i]
    i += 1
    params.TRICKROOM_MODIFIER = attr[i]
    i += 1
    # THRESHOLD MODIFIERS
    params.PROTECT_MODIFIER = attr[i]
    i += 1
    params.THAW_THRESHOLD = attr[i]
    i += 1
    params.PARALYSIS_THRESHOLD = attr[i]
    i += 1
    # DAMAGE MODIFIER
    params.WEATHER_BOOST = attr[i]
    i += 1
    params.WEATHER_UNBOOST = attr[i]
    i += 1
    params.STAB_MODIFIER = attr[i]
    i += 1
    params.BURN_DAMAGE_MODIFIER = attr[i]
    i += 1
    params.LIGHT_SCREEN_MODIFIER = attr[i]
    i += 1
    params.REFLECT_MODIFIER = attr[i]
    i += 1
    params.TERRAIN_DAMAGE_BOOST = attr[i]
    i += 1
    params.TERRAIN_DAMAGE_UNBOOST = attr[i]
    i += 1
    params.STEALTH_ROCK_MODIFIER = attr[i]
    i += 1
    params.POISON_MODIFIER = attr[i]
    i += 1
    params.BURN_MODIFIER = attr[i]
    i += 1
    params.SAND_MODIFIER = attr[i]
    i += 1
    for k in params.BOOST_MULTIPLIER_LOOKUP:
        params.BOOST_MULTIPLIER_LOOKUP[k] = attr[i]
        i += 1
    for k in params.ACCURACY_MULTIPLIER_LOOKUP:
        params.ACCURACY_MULTIPLIER_LOOKUP[k] = attr[i]
        i += 1
    for j, k in product(range(len(params.DAMAGE_MULTIPLICATION_ARRAY)), range(len(params.DAMAGE_MULTIPLICATION_ARRAY))):
        params.DAMAGE_MULTIPLICATION_ARRAY[j][k] = attr[i]
        i += 1
    return i
