from vgc2.battle_engine.modifiers import Category, Status, Hazard, Weather, Terrain, Type


class Move:
    __slots__ = ('id', 'pkm_type', 'base_power', 'accuracy', 'max_pp', 'category', 'priority', 'effect_prob',
                 'force_switch', 'self_switch', 'ignore_evasion', 'protect', 'boosts', 'self_boosts', 'heal', 'recoil',
                 'weather_start', 'field_start', 'toggle_trickroom', 'change_type', 'toggle_reflect',
                 'toggle_lightscreen', 'toggle_tailwind', 'hazard', 'status', 'disable', 'name')

    def __init__(self,
                 pkm_type: Type,
                 base_power: int,
                 accuracy: float,
                 max_pp: int,
                 category: Category,
                 priority: int = 0,
                 effect_prob: float = 1.,
                 force_switch: bool = False,
                 self_switch: bool = False,
                 ignore_evasion: bool = False,
                 protect: bool = False,
                 boosts: tuple[int, int, int, int, int, int, int, int] = (0,) * 8,
                 self_boosts: bool = True,
                 heal: float = 0.,
                 recoil: float = 0.,
                 weather_start: Weather = Weather.CLEAR,
                 field_start: Terrain = Terrain.NONE,
                 toggle_trickroom: bool = False,
                 change_type: bool = False,
                 toggle_reflect: bool = False,
                 toggle_lightscreen: bool = False,
                 toggle_tailwind: bool = False,
                 hazard: Hazard = Hazard.NONE,
                 status: Status = Status.NONE,
                 disable: bool = False,
                 name: str = ""):
        self.id = -1
        self.pkm_type = pkm_type
        self.base_power = base_power
        self.accuracy = accuracy
        self.max_pp = max_pp
        self.category = category
        self.priority = priority
        self.effect_prob = effect_prob
        # both_opposing/all_adjacent
        # special effects
        self.force_switch = force_switch
        self.self_switch = self_switch
        self.ignore_evasion = ignore_evasion
        self.protect = protect
        self.boosts = boosts
        self.self_boosts = self_boosts
        # boosts_reset)
        self.heal = heal
        # /heal_target)
        self.recoil = recoil
        self.weather_start = weather_start
        # weather_end
        self.field_start = field_start
        # field_end)
        self.toggle_trickroom = toggle_trickroom
        self.change_type = change_type
        self.toggle_reflect = toggle_reflect
        self.toggle_lightscreen = toggle_lightscreen
        self.toggle_tailwind = toggle_tailwind
        self.hazard = hazard
        # HAZARD_CLEARING
        self.status = status
        self.disable = disable
        # what is the special ability, dimension, probability, percentage, target/signal
        self.name = name

    def __str__(self):
        if self.name:
            return self.name
        return (str(self.pkm_type.name) +
                (", Power " + str(self.base_power) if self.base_power > 0 else "") +
                (", Accuracy %.2f" % self.accuracy if self.accuracy < 1. else "") +
                ", Max PP " + str(self.max_pp) + ", " + self.category.name +
                (", Priority " + str(self.priority) if self.priority > 0 else "") +
                (", Probability %.2f" % self.effect_prob if 0. < self.effect_prob < 1. else "") +
                (", Force Switch" if self.force_switch else "") +
                (", Self Switch" if self.self_switch else "") +
                (", Ignore Evasion" if self.ignore_evasion else "") +
                (", Protect" if self.protect else "") +
                ((f", %sBoosts " % ("Self " if self.self_boosts else "Target ")) + str(self.boosts)
                 if any(b != 0 for b in self.boosts) else "") +
                (", Heal %.2f" % self.heal if self.heal > 0. else "") +
                (", Recoil %.2f" % self.recoil if self.recoil > 0. else "") +
                (", " + self.weather_start.name if self.weather_start != Weather.CLEAR else "") +
                (", " + self.field_start.name if self.field_start != Terrain.NONE else "") +
                (", Trickroom" if self.toggle_trickroom else "") +
                (", Change Type" if self.change_type else "") +
                (", Reflect" if self.toggle_reflect else "") +
                (", Light Screen" if self.toggle_lightscreen else "") +
                (", Tailwind" if self.toggle_tailwind else "") +
                (", " + self.hazard.name if self.hazard != Hazard.NONE else "") +
                (", " + self.status.name if self.status != Status.NONE else "") +
                (", Disable" if self.disable else ""))


class BattlingMove:
    __slots__ = ('constants', 'pp', 'disabled')

    def __init__(self,
                 constants: Move):
        self.constants = constants
        self.pp = constants.max_pp
        self.disabled = False

    def __str__(self):
        return str(self.constants) + ", PP " + str(self.pp) + (", Disabled" if self.disabled else "")

    def reset(self):
        self.pp = self.constants.max_pp
        self.disabled = False
