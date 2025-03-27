from vgc2.battle_engine.constants import BattleRuleParam
from vgc2.battle_engine.modifiers import Stat
from vgc2.battle_engine.move import Move
from vgc2.battle_engine.pokemon import BattlingPokemon


def accuracy_evasion_modifier(params: BattleRuleParam,
                              move: Move,
                              attacker: BattlingPokemon,
                              defender: BattlingPokemon) -> float:
    return params.ACCURACY_MULTIPLIER_LOOKUP[attacker.boosts[Stat.ACCURACY] -
                                             (0 if move.ignore_evasion else defender.boosts[Stat.EVASION])]


def protect_modifier(params: BattleRuleParam,
                     move: Move,
                     attacker: BattlingPokemon) -> float:
    return params.PROTECT_MODIFIER ** attacker._consecutive_protect if move.protect else 1.0


def move_hit_threshold(params: BattleRuleParam,
                       move: Move,
                       attacker: BattlingPokemon,
                       defender: BattlingPokemon) -> float:
    return (move.accuracy * accuracy_evasion_modifier(params, move, attacker, defender) *
            protect_modifier(params, move, attacker))


def thaw_threshold(params: BattleRuleParam):
    return params.THAW_THRESHOLD


def paralysis_threshold(params: BattleRuleParam):
    return params.PARALYSIS_THRESHOLD
