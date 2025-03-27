from vgc2.battle_engine.constants import BattleRuleParam
from vgc2.battle_engine.game_state import State
from vgc2.battle_engine.modifiers import Status, Stat
from vgc2.battle_engine.move import Move
from vgc2.battle_engine.pokemon import BattlingPokemon


def paralysis_modifier(params: BattleRuleParam,
                       attacker: BattlingPokemon):
    return params.PARALYSIS_MODIFIER if attacker.status == Status.PARALYZED else 1.0


def trickroom_modifier(params: BattleRuleParam,
                       state: State):
    return params.TRICKROOM_MODIFIER if state.trickroom else 1.0


def boosted_speed(params: BattleRuleParam,
                  attacker: BattlingPokemon):
    return params.BOOST_MULTIPLIER_LOOKUP[attacker.boosts[Stat.SPEED]] * attacker.constants.stats[Stat.SPEED]


def priority_calculator(params: BattleRuleParam,
                        move: Move,
                        attacker: BattlingPokemon,
                        state: State):
    return (move.priority * 1000 + paralysis_modifier(params, attacker) * trickroom_modifier(params, state) *
            boosted_speed(params, attacker))
