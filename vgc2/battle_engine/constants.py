from vgc2.battle_engine.modifiers import Stat, Nature

NATURES = {
    Nature.LONELY: {
        'plus': Stat.ATTACK,
        'minus': Stat.DEFENSE
    },
    Nature.ADAMANT: {
        'plus': Stat.ATTACK,
        'minus': Stat.SPECIAL_ATTACK
    },
    Nature.NAUGHTY: {
        'plus': Stat.ATTACK,
        'minus': Stat.SPECIAL_DEFENSE
    },
    Nature.BRAVE: {
        'plus': Stat.ATTACK,
        'minus': Stat.SPEED
    },
    Nature.BOLD: {
        'plus': Stat.DEFENSE,
        'minus': Stat.ATTACK
    },
    Nature.IMPISH: {
        'plus': Stat.DEFENSE,
        'minus': Stat.SPECIAL_ATTACK
    },
    Nature.LAX: {
        'plus': Stat.DEFENSE,
        'minus': Stat.SPECIAL_DEFENSE
    },
    Nature.RELAXED: {
        'plus': Stat.DEFENSE,
        'minus': Stat.SPEED
    },
    Nature.MODEST: {
        'plus': Stat.SPECIAL_ATTACK,
        'minus': Stat.ATTACK
    },
    Nature.MILD: {
        'plus': Stat.SPECIAL_ATTACK,
        'minus': Stat.DEFENSE
    },
    Nature.RASH: {
        'plus': Stat.SPECIAL_ATTACK,
        'minus': Stat.SPECIAL_DEFENSE
    },
    Nature.QUIET: {
        'plus': Stat.SPECIAL_ATTACK,
        'minus': Stat.SPEED
    },
    Nature.CALM: {
        'plus': Stat.SPECIAL_DEFENSE,
        'minus': Stat.ATTACK
    },
    Nature.GENTLE: {
        'plus': Stat.SPECIAL_DEFENSE,
        'minus': Stat.DEFENSE
    },
    Nature.CAREFUL: {
        'plus': Stat.SPECIAL_DEFENSE,
        'minus': Stat.SPECIAL_ATTACK
    },
    Nature.SASSY: {
        'plus': Stat.SPECIAL_DEFENSE,
        'minus': Stat.SPEED
    },
    Nature.TIMID: {
        'plus': Stat.SPEED,
        'minus': Stat.ATTACK
    },
    Nature.HASTY: {
        'plus': Stat.SPEED,
        'minus': Stat.DEFENSE
    },
    Nature.JOLLY: {
        'plus': Stat.SPEED,
        'minus': Stat.SPECIAL_ATTACK
    },
    Nature.NAIVE: {
        'plus': Stat.SPEED,
        'minus': Stat.SPECIAL_DEFENSE
    },
}


class BattleRuleParam:

    def __init__(self):
        self.DAMAGE_MULTIPLICATION_ARRAY = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, .5, 0, 1, 1, .5, 1, 1],
                                            [1, .5, .5, 1, 2, 2, 1, 1, 1, 1, 1, 2, .5, 1, .5, 1, 2, 1, 1],
                                            [1, 2, .5, 1, .5, 1, 1, 1, 2, 1, 1, 1, 2, 1, .5, 1, 1, 1, 1],
                                            [1, 1, 2, .5, .5, 1, 1, 1, 0, 2, 1, 1, 1, 1, .5, 1, 1, 1, 1],
                                            [1, .5, 2, 1, .5, 1, 1, .5, 2, .5, 1, .5, 2, 1, .5, 1, .5, 1, 1],
                                            [1, .5, .5, 1, 2, .5, 1, 1, 2, 2, 1, 1, 1, 1, 2, 1, .5, 1, 1],
                                            [2, 1, 1, 1, 1, 2, 1, .5, 1, .5, .5, .5, 2, 0, 1, 2, 2, .5, 1],
                                            [1, 1, 1, 1, 2, 1, 1, .5, .5, 1, 1, 1, .5, .5, 1, 1, 0, 2, 1],
                                            [1, 2, 1, 2, .5, 1, 1, 2, 1, 0, 1, .5, 2, 1, 1, 1, 2, 1, 1],
                                            [1, 1, 1, .5, 2, 1, 2, 1, 1, 1, 1, 2, .5, 1, 1, 1, .5, 1, 1],
                                            [1, 1, 1, 1, 1, 1, 2, 2, 1, 1, .5, 1, 1, 1, 1, 0, .5, 1, 1],
                                            [1, .5, 1, 1, 2, 1, .5, .5, 1, .5, 2, 1, 1, .5, 1, 2, .5, .5, 1],
                                            [1, 2, 1, 1, 1, 2, .5, 1, .5, 2, 1, 2, 1, 1, 1, 1, .5, 1, 1],
                                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, .5, 1, 1, 1],
                                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, .5, 0, 1],
                                            [1, 1, 1, 1, 1, 1, .5, 1, 1, 1, 2, 1, 1, 2, 1, .5, 1, .5, 1],
                                            [1, .5, .5, .5, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, .5, 2, 1],
                                            [1, .5, 1, 1, 1, 1, 2, .5, 1, 1, 1, 1, 1, 1, 2, 2, .5, 1, 1],
                                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        self.BOOST_MULTIPLIER_LOOKUP = {
            -6: 2 / 8,
            -5: 2 / 7,
            -4: 2 / 6,
            -3: 2 / 5,
            -2: 2 / 4,
            -1: 2 / 3,
            0: 2 / 2,
            1: 3 / 2,
            2: 4 / 2,
            3: 5 / 2,
            4: 6 / 2,
            5: 7 / 2,
            6: 8 / 2
        }
        self.ACCURACY_MULTIPLIER_LOOKUP = {
            -6: 3 / 9,
            -5: 3 / 8,
            -4: 3 / 7,
            -3: 3 / 6,
            -2: 3 / 5,
            -1: 3 / 4,
            0: 3 / 3,
            1: 4 / 3,
            2: 5 / 3,
            3: 6 / 3,
            4: 7 / 3,
            5: 8 / 3,
            6: 9 / 3
        }
        self.TRICKROOM_TURNS = 5
        self.WEATHER_TURNS = 5
        self.TERRAIN_TURNS = 5
        self.REFLECT_TURNS = 5
        self.LIGHTSCREEN_TURNS = 5
        self.TAILWIND_TURNS = 5
        # PRIORITY MODIFIERS
        self.PARALYSIS_MODIFIER = .5
        self.TRICKROOM_MODIFIER = -1.
        # THRESHOLD MODIFIERS
        self.PROTECT_MODIFIER = 1 / 3
        self.THAW_THRESHOLD = .2
        self.PARALYSIS_THRESHOLD = .25
        # DAMAGE MODIFIER
        self.WEATHER_BOOST = 1.5
        self.WEATHER_UNBOOST = .5
        self.STAB_MODIFIER = 1.5
        self.BURN_DAMAGE_MODIFIER = .5
        self.LIGHT_SCREEN_MODIFIER = .5
        self.REFLECT_MODIFIER = .5
        self.TERRAIN_DAMAGE_BOOST = 1.3
        self.TERRAIN_DAMAGE_UNBOOST = .5
        self.STEALTH_ROCK_MODIFIER = .125
        self.POISON_MODIFIER = .125
        self.BURN_MODIFIER = .0625
        self.SAND_MODIFIER = .125
