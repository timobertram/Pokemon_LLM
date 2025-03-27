from vgc2.battle_engine.game_state import Side, State
from vgc2.battle_engine.pokemon import Pokemon, BattlingPokemon
from vgc2.battle_engine.team import Team, BattlingTeam


class PokemonView(Pokemon):
    __slots__ = ('_pkm', '_revealed')

    def __init__(self,
                 pkm: Pokemon):
        self._pkm = pkm
        self._pkm._views += [self]
        self._revealed: list[int] = []

    def __del__(self):
        self._pkm._views.remove(self)

    def __getattr__(self,
                    attr):
        if attr == "moves":
            return [self._pkm.moves[i] for i in self._revealed]
        if attr in ["_pkm"]:
            return None
        return getattr(self._pkm, attr)

    def _on_move_used(self,
                      i: int):
        if i not in self._revealed:
            self._revealed += [i]

    def hide(self):
        self._revealed = []


class BattlingPokemonView(BattlingPokemon):
    __slots__ = ('_pkm', '_constants_view', '_revealed')

    def __init__(self,
                 pkm: BattlingPokemon,
                 view: PokemonView | None = None):
        self._pkm = pkm
        self._constants_view = view if view else PokemonView(self._pkm.constants)
        self._pkm.constants._views += [self]
        self._revealed: list[int] = []

    def __del__(self):
        self._pkm.constants._views.remove(self)

    def __getattr__(self,
                    attr):
        if attr == "_pkm":
            return None
        if attr == "constants":
            return self._constants_view
        if attr == "battling_moves":
            return [self._pkm.battling_moves[i] for i in self._revealed]
        return getattr(self._pkm, attr)

    def _on_move_used(self,
                      i: int):
        if i not in self._revealed:
            self._revealed += [i]

    def hide(self):
        self._revealed = []


class TeamView(Team):
    __slots__ = ('_team', '_members')

    def __init__(self,
                 team: Team,
                 members_view: list[PokemonView] | None = None):
        self._team = team
        if members_view:
            self._members = members_view
        else:
            self._members = [PokemonView(p) for p in team.members]

    def __getattr__(self,
                    attr):
        if attr == "_team":
            return None
        if attr == "members":
            return self._members
        return getattr(self._team, attr)

    def hide(self):
        for m in self._members:
            m.hide()


class BattlingTeamView(BattlingTeam):
    __slots__ = ('_team', '_views', '_revealed')

    def __init__(self, team: BattlingTeam, view: TeamView):
        self._team = team
        self._views = ({p: BattlingPokemonView(p, v) for p, v in
                        zip(self._team.active, view.members[:len(self._team.active)])} |
                       {p: BattlingPokemonView(p, v) for p, v in
                        zip(self._team.reserve, view.members[len(self._team.active):])})
        self._revealed: list[BattlingPokemon] = [p for p in self._team.active]
        self._team._views += [self]

    def __del__(self):
        self._team._views.remove(self)

    def __getattr__(self,
                    attr):
        if attr == "_team":
            return None
        if attr == "active":
            return [self._views[p] for p in self._team.active]
        if attr == "reserve":
            return [self._views[p] for p in self._team.reserve if p in self._revealed]
        return getattr(self._team, attr)

    def on_switch(self, switch_in: BattlingPokemon | None):
        if switch_in and switch_in not in self._revealed:
            self._revealed += [switch_in]


class SideView(Side):
    __slots__ = ('_side', '_team')

    def __init__(self, side: Side, view: TeamView):
        self._side = side
        self._team = BattlingTeamView(self._side.team, view)
        self._side._views += [self]

    def __del__(self):
        self._side._views.remove(self)

    def __getattr__(self,
                    attr):
        if attr == "_side":
            return None
        if attr == "team":
            return self._team
        return getattr(self._side, attr)


class StateView(State):
    __slots__ = ('_state', '_sides')

    def __init__(self,
                 state: State,
                 side: int,
                 view: tuple[TeamView, TeamView]):
        self._state = state
        self._sides = (state.sides[side], SideView(state.sides[not side], view[not side]))

    def __getattr__(self,
                    attr):
        if attr == "_state":
            return None
        if attr == "sides":
            return self._sides
        return getattr(self._state, attr)
