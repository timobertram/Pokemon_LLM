from vgc2.battle_engine.pokemon import BattlingPokemon, Pokemon


class Team:
    __slots__ = ('members',)

    def __init__(self,
                 members: list[Pokemon]):
        self.members = members

    def __str__(self):
        return str([str(m) for m in self.members])


class BattlingTeam:
    __slots__ = ('active', '_initial_active', 'reserve', '_initial_reserve', '_views', '_engine')

    def __init__(self,
                 active: list[Pokemon] | list[BattlingPokemon],
                 reserve: list[Pokemon] | list[BattlingPokemon]):
        self.active = [BattlingPokemon(p) for p in active] if isinstance(active[0], Pokemon) else active
        self._initial_active = self.active[:]
        self.reserve = ([BattlingPokemon(p) for p in reserve] if isinstance(reserve[0], Pokemon) else reserve) if len(
            reserve) > 0 else []
        self._initial_reserve = self.active[:]
        self._views = []
        self._engine = None

    def __str__(self):
        return "Active " + str([str(a) for a in self.active]) + ", Reserve " + str([str(r) for r in self.reserve])

    def reset(self):
        self.active = self._initial_active[:]
        self.reserve = self._initial_reserve[:]
        for pkm in self.active:
            pkm.reset()
        for pkm in self.reserve:
            pkm.reset()

    def switch(self,
               active_pos: int,
               reserve_pos: int):
        if not 0 <= active_pos < len(self.active):
            return
        old_active = self.active[active_pos]
        if all(p.fainted() for p in self.reserve) and old_active.fainted():  # active fainted and reserve fainted
            self.reserve += [self.active.pop(active_pos)]
            self._engine._on_switch(None, old_active)
            return
        if not 0 <= reserve_pos < len(self.reserve):
            return
        old_reserve = self.reserve[reserve_pos]
        if old_reserve.fainted():
            return
        old_active.on_switch()
        for v in self._views:
            v.on_switch(old_reserve)
        self.reserve[reserve_pos] = old_active
        self.active[active_pos] = old_reserve
        self._engine._on_switch(old_reserve, old_active)

    def _on_turn_end(self):
        for active in self.active:
            active.on_turn_end()

    def fainted(self) -> bool:
        return all(p.fainted() for p in self.active + self.reserve)

    def get_active_pos(self,
                       pkm: BattlingPokemon) -> int:
        return next((i for i, p in enumerate(self.active) if p == pkm), -1)

    def first_from_reserve(self) -> int:
        return next((i for i, p in enumerate(self.reserve) if not p.fainted()), -1)
