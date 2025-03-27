from numpy.random import Generator

from vgc2.battle_engine import State, BattleEngine, Side, BattlingTeam, BattlingPokemon, BattlingMove, FullCommand, \
    _RNG, BattleRuleParam
from vgc2.battle_engine.game_state import SideConditions


def copy_battling_move(move: BattlingMove) -> BattlingMove:
    new_move = BattlingMove(move.constants)
    new_move.pp = move.pp
    new_move.disabled = move.disabled
    return new_move


def copy_battling_pokemon(pokemon: BattlingPokemon) -> BattlingPokemon:
    new_pokemon = BattlingPokemon(pokemon.constants)
    new_pokemon.hp = pokemon.hp
    new_pokemon.types = pokemon.types
    new_pokemon.boosts = pokemon.boosts
    new_pokemon.status = pokemon.status
    new_pokemon._wake_turns = pokemon._wake_turns
    new_pokemon.battling_moves = [copy_battling_move(m) for m in pokemon.battling_moves]
    if pokemon.last_used_move:
        new_pokemon.last_used_move = new_pokemon.battling_moves[pokemon.battling_moves.index(pokemon.last_used_move)]
    new_pokemon.protect = pokemon.protect
    new_pokemon._consecutive_protect = pokemon._consecutive_protect
    return new_pokemon


def copy_battling_team(team: BattlingTeam) -> BattlingTeam:
    return BattlingTeam([copy_battling_pokemon(p) for p in team.active],
                        [copy_battling_pokemon(p) for p in team.reserve])


def copy_conditions(conditions: SideConditions) -> SideConditions:
    new_conditions = SideConditions()
    new_conditions.reflect = conditions.reflect
    new_conditions._reflect_turns = conditions._reflect_turns
    new_conditions.lightscreen = conditions.lightscreen
    new_conditions._lightscreen_turns = conditions._lightscreen_turns
    new_conditions.tailwind = conditions.tailwind
    new_conditions._tailwind_turns = conditions._tailwind_turns
    new_conditions.stealth_rock = conditions.stealth_rock
    new_conditions.poison_spikes = conditions.poison_spikes
    return new_conditions


def copy_side(side: Side) -> Side:
    new_side = Side(copy_battling_team(side.team), copy_conditions(side.conditions))
    return new_side


def copy_state(state: State) -> State:
    new_state = State((copy_side(state.sides[0]), copy_side(state.sides[1])))
    new_state.weather = state.weather
    new_state._weather_turns = state._weather_turns
    new_state.field = state.field
    new_state._field_turns = state._field_turns
    new_state.trickroom = state.trickroom
    new_state._trickroom_turns = state._trickroom_turns
    return new_state


def forward(state: State,
            commands: FullCommand,
            params: BattleRuleParam = BattleRuleParam(),
            acc_rng: tuple[tuple[Generator, ...], tuple[Generator, ...]] = ((_RNG, _RNG), (_RNG, _RNG)),
            eff_rng: tuple[tuple[Generator, ...], tuple[Generator, ...]] = ((_RNG, _RNG), (_RNG, _RNG)),
            sta_rng: tuple[tuple[Generator, ...], tuple[Generator, ...]] = ((_RNG, _RNG), (_RNG, _RNG))):
    new_engine = BattleEngine(state, params, acc_rng, eff_rng, sta_rng)
    new_engine.run_turn(commands)
