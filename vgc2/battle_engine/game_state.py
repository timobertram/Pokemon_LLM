from vgc2.battle_engine import BattleRuleParam
from vgc2.battle_engine.modifiers import Weather, Terrain
from vgc2.battle_engine.pokemon import BattlingPokemon
from vgc2.battle_engine.team import BattlingTeam, Team


class SideConditions:
    __slots__ = ('reflect', '_reflect_turns', 'lightscreen', '_lightscreen_turns', 'tailwind', '_tailwind_turns',
                 'stealth_rock', 'poison_spikes')

    def __init__(self):
        self.reflect = False
        self._reflect_turns = 0
        self.lightscreen = False
        self._lightscreen_turns = 0
        self.tailwind = False
        self._tailwind_turns = 0
        self.stealth_rock = False
        self.poison_spikes = False

    def __str__(self):
        return ((", Reflect" if self.reflect else "") +
                (", Light Screen" if self.lightscreen else "") +
                (", Tailwind" if self.tailwind else "") +
                (", Stealth Rock" if self.stealth_rock else "") +
                (", Poison Spikes" if self.poison_spikes else ""))

    def reset(self):
        self.reflect = False
        self._reflect_turns = 0
        self.lightscreen = False
        self._lightscreen_turns = 0
        self.tailwind = False
        self._tailwind_turns = 0
        self.stealth_rock = False
        self.poison_spikes = False

    def _on_turn_end(self,
                     params: BattleRuleParam):
        if self.reflect:
            self._reflect_turns += 1
            if self._reflect_turns >= params.REFLECT_TURNS:
                self.reflect = False
                self._reflect_turns = 0
        if self.lightscreen:
            self._lightscreen_turns += 1
            if self._lightscreen_turns >= params.LIGHTSCREEN_TURNS:
                self.lightscreen = False
                self._lightscreen_turns = 0
        if self.tailwind:
            self._tailwind_turns += 1
            if self._tailwind_turns >= params.TAILWIND_TURNS:
                self.tailwind = False
                self._tailwind_turns = 0


class Side:
    __slots__ = ('team', 'conditions', '_engine', '_views')

    def __init__(self,
                 team: BattlingTeam,
                 conditions: SideConditions | None = None):
        self.team = team
        self.conditions = conditions if conditions else SideConditions()
        self._engine = None
        self._views = []

    def __str__(self):
        return str(self.team) + str(self.conditions)

    def set_team(self, team: BattlingTeam, view):
        self.team = team
        for v in self._views:
            v._on_set_team(view)

    def reset(self):
        if self.team:
            self.team.reset()
        self.conditions.reset()

    def _on_turn_end(self,
                     params: BattleRuleParam):
        self.conditions._on_turn_end(params)
        self.team._on_turn_end()


def get_battle_teams(team: tuple[Team, Team],
                     n_active: int) -> tuple[BattlingTeam, BattlingTeam]:
    return (BattlingTeam(team[0].members[:n_active], team[0].members[n_active:]),
            BattlingTeam(team[1].members[:n_active], team[1].members[n_active:]))


class State:
    __slots__ = ('sides', 'weather', '_weather_turns', 'field', '_field_turns', 'trickroom', '_trickroom_turns')

    def __init__(self,
                 team_side: tuple[BattlingTeam, BattlingTeam] | tuple[Side, Side]):
        self.sides = (Side(team_side[0]), Side(team_side[1])) if isinstance(team_side[0], BattlingTeam) else team_side
        self.weather = Weather.CLEAR
        self._weather_turns = 0
        self.field = Terrain.NONE
        self._field_turns = 0
        self.trickroom = False
        self._trickroom_turns = 0

    def __str__(self):
        return (("Weather " + self.weather.name + ", " if self.weather != Weather.CLEAR else "") +
                ("Terrain " + self.field.name + ", " if self.field != Terrain.NONE else "") +
                ("Trickroom, " if self.trickroom else "") +
                "Side 0 " + str(self.sides[0]) + ", Side 1 " + str(self.sides[1]))

    def reset(self):
        for side in self.sides:
            side.reset()
        self.weather = Weather.CLEAR
        self._weather_turns = 0
        self.field = Terrain.NONE
        self._field_turns = 0
        self.trickroom = False
        self._trickroom_turns = 0

    def _on_turn_end(self,
                     params: BattleRuleParam):
        # weather advance
        if self.weather != Weather.CLEAR:
            self._weather_turns += 1
            if self._weather_turns >= params.WEATHER_TURNS:
                self._weather_turns = 0
                self.weather = Weather.CLEAR
        # terrain advance
        if self.field != Terrain.NONE:
            self._field_turns += 1
            if self._field_turns >= params.TERRAIN_TURNS:
                self._field_turns = 0
                self.field = Terrain.NONE
        # trickroom advance
        if self.trickroom:
            self._trickroom_turns += 1
            if self._trickroom_turns >= params.TRICKROOM_TURNS:
                self.trickroom = False
                self._trickroom_turns = 0
        for side in self.sides:
            side._on_turn_end(params)

    def terminal(self) -> bool:
        return any(s.team.fainted() for s in self.sides)

    def get_side(self,
                 pkm: BattlingPokemon) -> int:
        return 0 if pkm in self.sides[0].team.active or pkm in self.sides[0].team.reserve else 1
