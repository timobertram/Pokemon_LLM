from typing import SupportsFloat, Any

from gymnasium import Env
from gymnasium.core import ActType, ObsType, RenderFrame
from gymnasium.spaces import MultiDiscrete, Box
from numpy import zeros

from vgc2.agent import BattlePolicy
from vgc2.agent.battle import RandomBattlePolicy
from vgc2.battle_engine import BattleEngine, TeamView, State, BattlingTeam, StateView, BattleRuleParam
from vgc2.battle_engine.game_state import get_battle_teams
from vgc2.competition.match import label_teams
from vgc2.util.encoding import encode_state, EncodeContext
from vgc2.util.generator import gen_team, TeamGenerator


def obs_encode_len(_encode_state,
                   n_active: int,
                   max_team_size: int,
                   max_pkm_moves: int) -> int:
    team = gen_team(max_team_size, max_pkm_moves)
    b_team = BattlingTeam(team.members[:n_active], team.members[n_active:])
    state = State((b_team, b_team))
    e = zeros(10000)
    return _encode_state(e, state, EncodeContext())


class BattleEnv(Env):

    def __init__(self,
                 ctx: EncodeContext,
                 n_active: int = 2,
                 max_team_size: int = 4,
                 max_pkm_moves: int = 4,
                 params: BattleRuleParam = BattleRuleParam(),
                 opponent: BattlePolicy = RandomBattlePolicy(),
                 _encode_state=encode_state,
                 _gen_team: TeamGenerator = gen_team):
        self.ctx = ctx
        self.n_active = n_active
        self.max_team_size = max_team_size
        self.max_pkm_moves = max_pkm_moves
        self.params = params
        self.opponent = opponent
        self.encode_state = _encode_state
        self.gen_team = gen_team
        encode_len = obs_encode_len(self.encode_state, n_active, max_team_size, max_pkm_moves)
        self.action_space = MultiDiscrete([max_pkm_moves + 1, max(max_team_size - n_active, n_active)] * n_active,
                                          start=[-1, 0] * n_active)
        self.observation_space = Box(-1., 1., (1, encode_len))  # TODO gym define obs limits per dim
        self.engine, self.state_view = self._get_engine_view()
        self.encode_buffer = zeros(encode_len)

    def _get_engine_view(self) -> tuple[BattleEngine, tuple[StateView, StateView]]:
        team = (self.gen_team(self.max_team_size, self.max_pkm_moves),
                self.gen_team(self.max_team_size, self.max_pkm_moves))
        label_teams(team)
        team_view = TeamView(team[0]), TeamView(team[1])
        state = State(get_battle_teams(team, self.n_active))
        return BattleEngine(state, self.params), (StateView(state, 0, team_view), StateView(state, 1, team_view))

    def set_opponent(self, opponent: BattlePolicy):
        self.opponent = opponent

    def set_random_teams(self):
        self.engine, self.state_view = self._get_engine_view()

    def step(self,
             action: ActType) -> tuple[ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        opp_action = self.opponent.decision(self.state_view[1])
        self.engine.run_turn(([(int(action[i * 2]), int(action[i * 2 + 1])) for i in range(self.n_active)], opp_action))
        terminated = self.engine.state.terminal()
        truncated = False
        reward = float(self.engine.winning_side == 0)  # the agent is only reached at the end of the episode
        observation = self._get_obs()
        info = self._get_info()
        return observation, reward, terminated, truncated, info

    def reset(self,
              *,
              seed: int | None = None,
              options: dict[str, Any] | None = None) -> tuple[ObsType, dict[str, Any]]:
        self.engine.reset()
        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def render(self) -> RenderFrame | list[RenderFrame] | None:
        pass

    def close(self):
        pass

    def _get_obs(self):
        self.encode_state(self.encode_buffer, self.state_view[0], self.ctx)
        return self.encode_buffer

    def _get_info(self):
        return {}
