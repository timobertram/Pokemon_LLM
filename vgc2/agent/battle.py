from itertools import product
from math import prod
from random import sample


from vllm import LLM, SamplingParams


from numpy import argmax
from numpy.random import choice

from vgc2.agent import BattlePolicy
from vgc2.battle_engine import State, BattleCommand, calculate_damage, BattleRuleParam, BattlingTeam, BattlingPokemon, \
    BattlingMove, TeamView
from vgc2.util.forward import copy_state, forward
from vgc2.util.rng import ZERO_RNG, ONE_RNG


# RandomBattlePolicy

class RandomBattlePolicy(BattlePolicy):
    """
    Policy that selects moves and switches randomly. Tailored for single and double battles.
    """

    def __init__(self,
                 switch_prob: float = .15):
        self.switch_prob = switch_prob

    def decision(self,
                 state: State) -> list[BattleCommand]:
        team = state.sides[0].team
        n_switches = len(team.reserve)
        n_targets = len(state.sides[1].team.active)
        cmds: list[BattleCommand] = []
        for pkm in team.active:
            n_moves = len(pkm.battling_moves)
            switch_prob = 0 if n_switches == 0 else self.switch_prob
            action = choice(n_moves + 1, p=[switch_prob] + [(1. - switch_prob) / n_moves] * n_moves) - 1
            if action >= 0:
                target = choice(n_targets, p=[1 / n_targets] * n_targets)
            else:
                target = choice(n_switches, p=[1 / n_switches] * n_switches)
            cmds += [(action, target)]
        return cmds


# GreedyBattlePolicy

def greedy_single_battle_decision(params: BattleRuleParam,
                                  state: State) -> list[BattleCommand]:
    attacker, defender = state.sides[0].team.active[0], state.sides[1].team.active[0]
    outcomes = [calculate_damage(params, 0, move.constants, state, attacker, defender)
                if move.pp > 0 and not move.disabled else 0 for move in attacker.battling_moves]
    return [(int(argmax(outcomes)), 0) if outcomes else (0, 0)]


def greedy_double_battle_decision(params: BattleRuleParam,
                                  state: State) -> list[BattleCommand]:
    attackers, defenders = state.sides[0].team.active, state.sides[1].team.active
    strategies = []
    for sources in product(list(range(len(attackers[0].battling_moves))),
                           list(range(len(attackers[1].battling_moves))) if len(attackers) > 1 else []):
        for targets in product(list(range(len(defenders))), list(range(len(defenders)))):
            damage, ko, hp = 0, 0, [d.hp for d in defenders]
            for i, (source, target) in enumerate(zip(sources, targets)):
                attacker, defender, move = attackers[i], defenders[target], attackers[i].battling_moves[source]
                if move.pp == 0 or move.disabled:
                    continue
                new_hp = max(0, hp[target] - calculate_damage(params, 0, move.constants, state, attacker, defender))
                damage += hp[target] - new_hp
                ko += int(new_hp == 0)
                hp[target] = new_hp
            strategies += [(ko, damage, sources, targets)]
    if len(strategies) == 0:
        return [(choice(len(a.battling_moves)), choice(len(defenders))) for a in attackers]
    best = max(strategies, key=lambda x: 1000 * x[0] + x[1])
    return list(zip(best[2], best[3]))


class GreedyBattlePolicy(BattlePolicy):
    """
    Greedy strategy that prioritizes KOs and damage output with only one turn lookahead. Performs no switches.
    """

    def __init__(self,
                 params: BattleRuleParam = BattleRuleParam()):
        self.params = params

    def decision(self, state: State) -> list[BattleCommand]:
        n_active_0, n_active_1 = len(state.sides[0].team.active), len(state.sides[1].team.active)
        match max(n_active_0, n_active_1):
            case 1:
                return greedy_single_battle_decision(self.params, state)
            case 2:
                return greedy_double_battle_decision(self.params, state)


# TreeSearchBattlePolicy

def get_actions(team: tuple[BattlingTeam, BattlingTeam]) -> list[list[BattleCommand]]:
    attackers = team[0].active
    move_targets = [i for i in range(len(team[1].active))]
    switch_targets = [i for i, p in enumerate(team[0].reserve) if p.hp > 0]
    commands = []
    for attacker in attackers:
        moves = [i for i, m in enumerate(attacker.battling_moves) if m.pp > 0 and not m.disabled]
        commands += [list(product(moves, move_targets)) + list(product([-1], switch_targets))]
    return list(product(*commands))


def _deduce_moves(pokemon: BattlingPokemon,
                  max_moves: int):
    n_moves = len(pokemon.battling_moves)
    if n_moves < max_moves:
        ids = [m.constants.id for m in pokemon.battling_moves]
        moves = [m for m in pokemon.constants.species.moves if m.id not in ids]
        pokemon.battling_moves += [BattlingMove(m) for m in sample(moves, max_moves - n_moves)]  # ignoring meta


def deduce_state(state: State,
                 opp_team_view: TeamView,
                 max_moves: int) -> State:
    _state = copy_state(state)
    opp_team = _state.sides[1].team
    # randomly assume reserve of opponent
    current_pokemon = len(opp_team.active + opp_team.reserve)
    total_pokemon = len(opp_team_view.members)
    if current_pokemon < total_pokemon:
        ids = [p.constants.species.id for p in opp_team.active + opp_team.reserve]
        pokemon = [p for p in opp_team_view.members if p.species.id not in ids]
        opp_team.reserve += [BattlingPokemon(p) for p in sample(pokemon, total_pokemon - current_pokemon)]
    # randomly set hidden moves of opponent
    for p in opp_team.active + opp_team.reserve:
        _deduce_moves(p, max_moves)
    return _state


def eval_state(state: State) -> float:
    my_team = state.sides[0].team
    my_hp = sum(p.hp / p.constants.stats[0] for p in my_team.active + my_team.reserve)
    opp_team = state.sides[1].team
    opp_hp = sum(p.hp / p.constants.stats[0] for p in opp_team.active + opp_team.reserve)
    return my_hp - 3 * opp_hp + 3. * (len(opp_team.active) + len(opp_team.reserve))


class TreeSearchBattlePolicy(BattlePolicy):
    """
    Look ahead strategy that can takes into account multiple actions from our side, and the possibility of multiple
    random scenarios. However, assumes a GreedyBattlePolicy as the opponent, so it only considers one possible action
    from the opponent and only branches the accuracy of moves.
    """

    def __init__(self,
                 opp_team: TeamView,
                 max_team_size: int = 4,
                 max_moves: int = 4,
                 max_depth: int = 1,
                 params: BattleRuleParam = BattleRuleParam()):
        self.opp_team = opp_team
        self.max_team_size = max_team_size
        self.max_moves = max_moves
        self.max_depth = max_depth
        self.params = params
        self.opp_policy = GreedyBattlePolicy(params)

    def get_states(self,
                   state: State,
                   action: list[BattleCommand],
                   opp_action: list[BattleCommand]) -> list[tuple[State, float]]:
        action = list(action)
        states: list[tuple[State, float]] = []
        combs = [[] for _ in range(len(action) + len(opp_action))]
        i = 0
        # iterate over all possible outcomes, setting fixed RNG and respective probabilities
        for side, _a in enumerate([list(enumerate(action)), list(enumerate(opp_action))]):
            for pos, a in _a:
                if a[0] == -1:
                    prob = 1.
                else:
                    prob = state.sides[side].team.active[pos].battling_moves[a[1]].constants.accuracy
                if prob < .9:
                    combs[i] += [(side, pos, ZERO_RNG, prob), (side, pos, ONE_RNG, 1. - prob)]
                else:
                    combs[i] += [(side, pos, ZERO_RNG, prob)]
                i += 1
        for comb in product(*combs):
            prob = prod([e[3] for e in comb])
            acc_rng = [[], []]
            for e in comb:
                acc_rng[e[0]] += [e[2]]
            _state = copy_state(state)
            forward(_state, (action, opp_action), self.params, acc_rng=(tuple(acc_rng[0]), tuple(acc_rng[1])))
            states += [(_state, prob)]
        return states

    def eval_action(self,
                    state: State,
                    action: list[BattleCommand],
                    opp_action: list[BattleCommand],
                    depth: int = 0) -> float:
        # predict possible states and probabilities after a turn passes
        states = self.get_states(state, action, opp_action)
        val = 0.
        weight = 0.
        for _state, prob in states:
            # if terminal or depth depleted we add the estimated state value
            if _state.terminal() or depth >= self.max_depth:
                val += prob * eval_state(_state)
            # otherwise lookahead one more turn
            else:
                actions = get_actions((_state.sides[0].team, _state.sides[1].team))
                opp_action = self.opp_policy.decision(State((_state.sides[1], _state.sides[0])))  # assume greedy and single decision
                evals = [self.eval_action(_state, action, opp_action, depth + 1) for action in actions]
                val += prob * max(evals, default=0.)  # assuming greedy
            weight += prob
        return 0.975 * val / weight

    def decision(self,
                 state: State) -> list[BattleCommand]:
        action_eval: dict[tuple[tuple[int, int], ...], float] = {}
        # deduce initial state
        _state = deduce_state(state, self.opp_team, self.max_moves)
        # iterate over all our possible actions
        for action in get_actions((_state.sides[0].team, _state.sides[1].team)):
            # assume a single and greedy decision from opponent
            opp_action = self.opp_policy.decision(State((_state.sides[1], _state.sides[0])))
            value = self.eval_action(_state, action, opp_action, 0)
            key = tuple(tuple(a) for a in action)
            action_eval[key] = value
        if not action_eval:
            action_eval = {((0, 0), (0, 0)): 0.}
        # print(action_eval)
        # print(list(max(action_eval, key=action_eval.get, default=0)))
        # return action that maximizes value
        return list(max(action_eval, key=action_eval.get, default=0))


class LLM_Policy(BattlePolicy):
    def __init__(self):
        import google.generativeai as genai

        API_KEY = "KEY EINFÜGEN"
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")
        genai.configure(api_key = API_KEY)

    def get_environment_description(self):
        return '''You are a player for a game of pokemon and need to choose actions. 
        The player has 4 Pokemon, each with 4 moves. The opponent has 4 Pokemon, each with 4 moves. 
        The player can choose to attack or switch Pokemon. 
        The goal is to defeat the opponent's Pokemon by reducing their HP to 0. 
        '''

    def get_state_description(self, state: State):
        return f'''The player has {len(state.sides[0].team.active)} active Pokemon and {len([pok for pok in state.sides[0].team.reserve if pok.hp > 0])} reserve Pokemon.
        The opponent has {len(state.sides[1].team.active)} active Pokemon and {len([pok for pok in state.sides[1].team.reserve if pok.hp > 0])} reserve Pokemon.
        Our first active Pokemon is: {str(state.sides[0].team.active[0])}.
        Our second active Pokemon is: {str(state.sides[0].team.active[1]) if len(state.sides[0].team.active) > 1 else 'NaN'}.
        Our first reserve Pokemon is: {str(state.sides[0].team.reserve[0]) if state.sides[0].team.reserve[0].hp > 0  else 'NaN'} 
        Our second reserve Pokemon is: {str(state.sides[0].team.reserve[1]) if state.sides[0].team.reserve[1].hp > 0  else 'NaN'} 
        The opponent's first active Pokemon is: {str(state.sides[1].team.active[0])} (opponent moves are only visible after first use).
        The opponent's second active Pokemon is {str(state.sides[1].team.active[1]) if len(state.sides[1].team.active) > 1 else 'NaN'} (opponent moves are only visible after first use).
        The current HP of the active Pokemon are: {state.sides[0].team.active[0].hp} and {state.sides[1].team.active[0].hp}.
        The current status of the active Pokemon are: {state.sides[0].team.active[0].status} and {state.sides[1].team.active[0].status}.
        The current stats of the active Pokemon are: {state.sides[0].team.active[0].constants.stats} and {state.sides[1].team.active[0].constants.stats}.
        '''
    
    def request_action(self, state: State):
        actions = get_actions((state.sides[0].team,state.sides[1].team))
        return f'''What actions should the player take?
        One action is required for each of the active pokemon.
        The available actions are:
        - Attack opponent 0 with move 0 (0,0)
        - Attack opponent 1 with move 0 (0,1)
        - Attack opponent 0 with move 1 (1,0)
        - Attack opponent 1 with move 1 (1,1)
        - Attack opponent 0 with move 2 (2,0)
        - Attack opponent 1 with move 2 (2,1)
        - Attack opponent 0 with move 3 (3,0)
        - Attack opponent 1 with move 3 (3,1)
        - Switch to reserve Pokemon 0 (-1,0)
        - Switch to reserve Pokemon 1 (-1,1)
        As an action, only output the part in brackets at the end.
        Let's thing step by step.
        Explain your reasoning for choosing your action and evaluate their effectiveness from 1-10.
        In addition, evaluate how likely you think you will win the match from 1-10.
        Your output should contain:
        Reasoning for pokemon 0:  <reasoning>
        Reasoning for pokemon 1:  <reasoning>
        Action for pokemon 0: <action>
        Evaluation for action of pokemon 0: <evaluation>
        Action for pokemon 1: <action>
        Evaluation for action of pokemon 1: <evaluation>
        Evaluation of winning the game: <evaluation>
        '''
        

    def decision(self, state: State) -> list[BattleCommand]:
        import re
        final_prompt = self.get_environment_description() + self.get_state_description(state) + self.request_action(state)
        response = self.model.generate_content(final_prompt).text
        print(final_prompt)
        print(response)
        # Regex pattern to match (number,number)
        pattern = r'\((-?\d+),(-?\d+)\)'

        # Find all matches in the text
        matches = re.findall(pattern, response)
        actions = tuples = [(int(num1), int(num2)) for num1, num2 in matches]
        return actions


# TerminalBattle

def select(max_action: int):
    while True:
        try:
            act = int(input('Select Action: '))
            if 0 < act < max_action:
                return act
            else:
                print('Invalid action. Select again.')
        except:
            print('Invalid action. Select again.')


class TerminalBattle(BattlePolicy):
    """
    Terminal battle interface. Tailored for single and double battles.
    """

    def decision(self,
                 state: State) -> list[BattleCommand]:
        cmds: list[BattleCommand] = []
        team = state.sides[0].team
        print('~ Actions ~')
        for pkm in team.active:
            print(pkm)
            n_moves = len(pkm.battling_moves)
            n_switches = len(team.reserve)
            for i, move in enumerate(pkm.battling_moves):
                print(i, '->', move)
            for i, r_pkm in enumerate(team.reserve):
                print(i + n_moves, '-> Switch to', r_pkm)
            act = select(n_moves + n_switches)
            targets = state.sides[1].team.active
            if 0 < act < n_moves and len(targets) > 1:
                print('~ Targets ~')
                for i, a in enumerate(targets):
                    print(i, '-> ', a)
                cmds += [(act, select(len(targets)))]
            else:
                cmds += [(-1, act - n_moves)]
        print()
        return cmds
